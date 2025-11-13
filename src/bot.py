"""
FIXED bot.py - Handle None returns from async commands
Replace: bot.py
"""

import discord
import os
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv

from _HANDLERS.commandManager import commandManager
from _HANDLERS.interactionManager import interactionManager
from _HANDLERS.clopenManager import channelManager
from utils.language_manager import language_manager

load_dotenv()

# Health check server
def start_health_server():
    port = int(os.getenv("PORT", "8080"))
    
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200 if self.path in ("/", "/health") else 404)
            if self.path in ("/", "/health"):
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"OK")
            else:
                self.end_headers()
        
        do_HEAD = do_GET
        log_message = lambda self, *args: None
    
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    print(f"Health server running on port {port}")
    server.serve_forever()

threading.Thread(target=start_health_server, daemon=True).start()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True

client = discord.Client(intents=intents)

# Initialize managers
cmd_manager = commandManager(client)
interaction_manager = interactionManager(client)
clopen_manager = channelManager(client)

# Link managers together
client.clopen_manager = clopen_manager
cmd_manager.clopen_manager = clopen_manager

cmd_manager.loadCommands()

@client.event
async def on_ready():
    print(f'Bot ready as {client.user}')
    
    # Load clopen configuration
    await clopen_manager.load_config()
    print(f"Clopen system loaded: {len(clopen_manager.guild_configs)} guilds, {len(clopen_manager.channels)} channels")
    
    # Start clopen scheduler
    clopen_manager.scheduler_task = asyncio.create_task(
        clopen_manager.start_scheduler()
    )

@client.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Handle clopen system (must be first)
    await clopen_manager.on_message(message)
    
    # Handle prefix commands
    if message.content.startswith(cmd_manager.PREFIX):
        await handle_command(message)
    
    # Handle Deepwoken builder replies
    if message.type == discord.MessageType.reply and message.reference:
        replied_msg = message.reference.resolved
        if replied_msg and 'https://deepwoken.co/builder?id=' in replied_msg.content:
            result = await asyncio.to_thread(interaction_manager.processReply, message)
            if result:
                embed, file = result
                if embed or file:
                    await message.channel.send(embed=embed, file=file, reference=message)

@client.event
async def on_reaction_add(reaction, user):
    await clopen_manager.on_reaction_add(reaction, user)

async def handle_command(message):
    # Language command special handling
    if message.content.startswith('.language'):
        if not await handle_language_command(message):
            return
    
    # Process command (now async)
    result = await cmd_manager.processCommand(message)
    
    # If result is None, it means async command already sent its own message
    if not result:
        return
    
    # Parse result - handle both (embed, meta) and plain embed
    if isinstance(result, tuple) and len(result) == 2:
        embed, meta = result
    else:
        embed, meta = result, None
    
    # Send response
    if embed:
        sent = await message.channel.send(embed=embed, reference=message)
        
        # Auto-delete if requested
        if meta and meta.get('auto_delete'):
            await asyncio.sleep(meta.get('timeout', 10))
            try:
                await sent.delete()
                if meta.get('delete_user_message'):
                    await message.delete()
            except discord.errors.NotFound:
                pass

async def handle_language_command(message):
    guild_id = message.guild.id if message.guild else None
    lang = language_manager.get_language(guild_id)
    
    # Check permissions in guilds
    if message.guild:
        if not message.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="Permission Denied" if lang == 'en' else "Permiso Denegado",
                description=(
                    "Only administrators can change the bot language." 
                    if lang == 'en' else 
                    "Solo los administradores pueden cambiar el idioma del bot."
                ),
                color=0xED4245
            )
            sent = await message.channel.send(embed=embed, reference=message)
            await asyncio.sleep(10)
            try:
                await sent.delete()
                await message.delete()
            except discord.errors.NotFound:
                pass
            return False
        
        # Set language if valid
        lang_code = message.content[10:].strip().lower()
        if lang_code in ['en', 'es']:
            language_manager.set_language(guild_id, lang_code)
    
    return True

client.run(os.getenv("BOT_TOKEN"))
