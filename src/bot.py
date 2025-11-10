import discord
import os
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv

from handlers.commandManager import commandManager
from handlers.interactionManager import interactionManager
from utils.language_manager import language_manager

intents = discord.Intents.default()
intents.message_content = True

#setup
load_dotenv()

# Start a tiny HTTP server for Render/Uptime probes in a background thread
def _start_webserver_in_thread():
    """Start a small HTTP server that responds 200 OK on / and /health.

    Uses PORT env var (defaults to 8080). Runs in a daemon thread so it won't block shutdown.
    """
    port = int(os.getenv("PORT", "8080"))

    class _HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path in ("/", "/health"):
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"OK")
            else:
                self.send_response(404)
                self.end_headers()

        def do_HEAD(self):
            if self.path in ("/", "/health"):
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()

        # Silence default logging
        def log_message(self, format, *args):
            return

    server = HTTPServer(("0.0.0.0", port), _HealthHandler)
    print(f"Starting HTTP server on 0.0.0.0:{port} (health endpoint)")
    try:
        server.serve_forever()
    except Exception as exc:
        print("Webserver stopped:", exc)

# Launch health server thread
threading.Thread(target=_start_webserver_in_thread, daemon=True).start()
BOT_TOKEN = str(os.getenv("BOT_TOKEN"))
client = discord.Client(intents=intents)
commands = commandManager(client)
interactions = interactionManager(client)
commands.loadCommands()

@client.event
async def on_ready():
    print(f'Im fucking poa at {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith(commands.PREFIX):
        # Special handling for language command (requires admin permissions)
        if message.content.startswith('.language ') or message.content == '.language':
            # Check if in a guild and user has admin permissions
            if message.guild:
                if message.author.guild_permissions.administrator:
                    # Extract language code from command
                    lang_code = message.content[10:].strip().lower()  # Remove '.language '
                    if lang_code in ['en', 'es']:
                        language_manager.set_language(message.guild.id, lang_code)
                    # Process command normally to show response (in a thread to avoid blocking)
                    result = await asyncio.to_thread(commands.processCommand, message)
                    if result:
                        if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], dict):
                            embed, meta = result
                        else:
                            embed, meta = result, None
                        sent_message = await message.channel.send(embed=embed, reference=message)
                        if meta and meta.get('auto_delete'):
                            await asyncio.sleep(int(meta.get('timeout', 10)))
                            try:
                                await sent_message.delete()
                                if meta.get('delete_user_message'):
                                    await message.delete()
                            except (discord.errors.NotFound, discord.errors.Forbidden):
                                pass
                else:
                    # User doesn't have permission
                    guild_id = message.guild.id if message.guild else None
                    lang = language_manager.get_language(guild_id)
                    title = "Permission Denied" if lang == 'en' else "Permiso Denegado"
                    desc = "Only administrators can change the bot language." if lang == 'en' else "Solo los administradores pueden cambiar el idioma del bot."
                    embed = discord.Embed(title=f"{title}", description=desc, color=0xED4245)
                    sent_message = await message.channel.send(embed=embed, reference=message)
                    # Auto-delete permission error after 10 seconds
                    await asyncio.sleep(10)
                    try:
                        await sent_message.delete()
                        await message.delete()
                    except (discord.errors.NotFound, discord.errors.Forbidden):
                        pass
            else:
                # DM - just show the info (in a thread to avoid blocking)
                result = await asyncio.to_thread(commands.processCommand, message)
                if result:
                    if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], dict):
                        embed, meta = result
                    else:
                        embed, meta = result, None
                    sent_message = await message.channel.send(embed=embed, reference=message)
                    if meta and meta.get('auto_delete'):
                        await asyncio.sleep(int(meta.get('timeout', 10)))
                        try:
                            await sent_message.delete()
                            if meta.get('delete_user_message'):
                                await message.delete()
                        except (discord.errors.NotFound, discord.errors.Forbidden):
                            pass
        else:
            # Normal command processing (in a thread to avoid blocking)
            result = await asyncio.to_thread(commands.processCommand, message)
            if result:
                # Allow returning either an Embed or (Embed, meta) where meta controls auto-delete
                if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], dict):
                    embed, meta = result
                else:
                    embed, meta = result, None

                sent_message = await message.channel.send(embed=embed, reference=message)
                # Auto-delete error/usage messages after timeout if meta requests it
                if meta and meta.get('auto_delete'):
                    await asyncio.sleep(int(meta.get('timeout', 10)))
                    try:
                        await sent_message.delete()
                        if meta.get('delete_user_message'):
                            await message.delete()  # Also delete the user's command
                    except (discord.errors.NotFound, discord.errors.Forbidden):
                        pass
    
    if message.type == discord.MessageType.reply:
        referenced = message.reference
        if referenced and referenced.resolved:
            replied_msg = referenced.resolved
            if 'https://deepwoken.co/builder?id=' in replied_msg.content:
                # Process interaction in a thread to avoid blocking
                result = await asyncio.to_thread(interactions.processReply, message)
                if result is not None:
                    embed, file = result
                    if embed is not None or file is not None:
                        await message.channel.send(embed=embed, file=file, reference=message)


client.run(BOT_TOKEN)
