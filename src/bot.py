"""
FIXED bot.py - Handle None returns from async commands
Replace: bot.py
"""

import discord
import os
import asyncio
import threading
from typing import Optional
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv
from discord import app_commands

from _HANDLERS.commandManager import commandManager
from _HANDLERS.interactionManager import interactionManager
from _HANDLERS.clopenManager import channelManager
from utils.language_manager import language_manager

from commands import equipment as equipment_command
from commands import help as help_command
from commands import kit as kit_command
from commands import language as language_command
from commands import mantra as mantra_command
from commands import outfit as outfit_command
from commands import talent as talent_command
from commands import weapon as weapon_command

load_dotenv()

# Health check server
def start_health_server():
    port = int(os.getenv("PORT", "10000"))
    external_base = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("EXTERNAL_URL")
    
    class HealthHandler(BaseHTTPRequestHandler):
        def _log_uptime_ping(self):
            proto = self.headers.get("X-Forwarded-Proto", "").lower()
            scheme = "https" if proto == "https" else "http"
            host = self.headers.get("Host", f"0.0.0.0:{self.server.server_port}")
            full_url = f"{scheme}://{host}{self.path}"
            ua = self.headers.get("User-Agent", "-")
            src = f"{self.client_address[0]}" if self.client_address else "-"

            if self.path == "/":
                print(f"[UptimeRobot] Ping to ROOT: {full_url} from {src} UA='{ua}'")
            elif self.path == "/health":
                print(f"[UptimeRobot] Ping to HEALTH: {full_url} from {src} UA='{ua}'")

        def do_GET(self):
            self.send_response(200 if self.path in ("/", "/health") else 404)
            if self.path in ("/", "/health"):
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"OK")
                self._log_uptime_ping()
            else:
                self.end_headers()
        
        def do_HEAD(self):
            self.send_response(200 if self.path in ("/", "/health") else 404)
            if self.path in ("/", "/health"):
                self.send_header("Content-Type", "text/plain")
            self.end_headers()
            if self.path in ("/", "/health"):
                self._log_uptime_ping()
        
        log_message = lambda self, *args: None
    
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    if external_base:
        print(
            f"Health server running on port {port} (paths: /, /health) | External endpoints: {external_base}/ , {external_base}/health"
        )
    else:
        print(f"Health server running on port {port} (paths: /, /health)")
    server.serve_forever()

threading.Thread(target=start_health_server, daemon=True).start()

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.reactions = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
_slash_synced = False

# Initialize managers
cmd_manager = commandManager(client)
interaction_manager = interactionManager(client)
clopen_manager = channelManager(client)

# Link managers together
client.clopen_manager = clopen_manager
cmd_manager.clopen_manager = clopen_manager


async def _send_text_response(interaction: discord.Interaction, content: str, *, ephemeral: bool = True):
    # Always prefer followups; ensure we've acknowledged the interaction
    if not interaction.response.is_done():
        try:
            await interaction.response.defer(thinking=False, ephemeral=ephemeral)
        except Exception:
            pass
    await interaction.followup.send(content, ephemeral=ephemeral)


async def _dispatch_command_result(
    interaction: discord.Interaction,
    result,
    *,
    fallback: str = "No data was returned.",
    ephemeral_override: Optional[bool] = None,
):
    if isinstance(result, tuple):
        embed, meta = result
    else:
        embed, meta = result, None

    ephemeral = ephemeral_override if ephemeral_override is not None else bool(meta and meta.get('auto_delete'))

    if not embed:
        await _send_text_response(interaction, fallback, ephemeral=True)
        return

    # Ensure interaction is acknowledged, then send followup (robust against delays)
    if not interaction.response.is_done():
        try:
            await interaction.response.defer(thinking=False, ephemeral=ephemeral)
        except Exception:
            pass
    await interaction.followup.send(embed=embed, ephemeral=ephemeral)


async def _run_lookup_command(
    interaction: discord.Interaction,
    module,
    query: str,
    *,
    fallback: str,
):
    cleaned_query = (query or "").strip()
    if not cleaned_query:
        await _send_text_response(interaction, "Please provide a name to search.", ephemeral=True)
        return

    # Defer immediately to avoid 3s timeouts while we do blocking lookups
    if not interaction.response.is_done():
        try:
            await interaction.response.defer(thinking=True, ephemeral=True)
        except Exception:
            pass

    try:
        result = module.execute(cleaned_query, None)
    except Exception as exc:
        error_embed = discord.Embed(
            title="Lookup failed",
            description=f"An unexpected error occurred: {exc}",
            color=0xED4245,
        )
        await _dispatch_command_result(interaction, error_embed, ephemeral_override=True)
        return

    await _dispatch_command_result(interaction, result, fallback=fallback)


@tree.command(name="help", description="Show the Analytic Deepwoken help menu.")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def help_slash_command(interaction: discord.Interaction):
    if not interaction.response.is_done():
        try:
            await interaction.response.defer(thinking=False, ephemeral=True)
        except Exception:
            pass
    embed = help_command.execute("slash", None)
    await _dispatch_command_result(interaction, embed, fallback="Unable to display the help menu.")


@tree.command(name="equipment", description="Look up equipment details by name.")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(name="Full or partial equipment name")
async def equipment_slash_command(interaction: discord.Interaction, name: str):
    await _run_lookup_command(
        interaction,
        equipment_command,
        name,
        fallback="Equipment not found. Try another name.",
    )


@tree.command(name="weapon", description="Look up weapon details by name.")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(name="Full or partial weapon name")
async def weapon_slash_command(interaction: discord.Interaction, name: str):
    await _run_lookup_command(
        interaction,
        weapon_command,
        name,
        fallback="Weapon not found. Try another name.",
    )


@tree.command(name="talent", description="Look up talent details by name.")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(name="Full or partial talent name")
async def talent_slash_command(interaction: discord.Interaction, name: str):
    await _run_lookup_command(
        interaction,
        talent_command,
        name,
        fallback="Talent not found. Try another name.",
    )


@tree.command(name="mantra", description="Look up mantra details by name.")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(name="Full or partial mantra name")
async def mantra_slash_command(interaction: discord.Interaction, name: str):
    await _run_lookup_command(
        interaction,
        mantra_command,
        name,
        fallback="Mantra not found. Try another name.",
    )


@tree.command(name="outfit", description="Look up outfit details by name.")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(name="Full or partial outfit name")
async def outfit_slash_command(interaction: discord.Interaction, name: str):
    await _run_lookup_command(
        interaction,
        outfit_command,
        name,
        fallback="Outfit not found. Try another name.",
    )


@tree.command(name="kit", description="Look up kit details by share ID.")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(kit_id="Kit share ID from the Deepwoken planner")
async def kit_slash_command(interaction: discord.Interaction, kit_id: str):
    cleaned = (kit_id or "").strip()
    if not cleaned:
        await _send_text_response(interaction, "Please provide a kit share ID.", ephemeral=True)
        return

    if not interaction.response.is_done():
        try:
            await interaction.response.defer(thinking=True, ephemeral=True)
        except Exception:
            pass

    try:
        result = kit_command.execute(cleaned, None)
    except Exception as exc:
        error_embed = discord.Embed(
            title="Kit lookup failed",
            description=f"An unexpected error occurred: {exc}",
            color=0xED4245,
        )
        await _dispatch_command_result(interaction, error_embed, ephemeral_override=True)
        return

    await _dispatch_command_result(
        interaction,
        result,
        fallback="Kit not found. Please verify the share ID.",
    )


language_choices = [
    app_commands.Choice(name="English", value="en"),
    app_commands.Choice(name="Spanish", value="es"),
]


@tree.command(name="language", description="Configure the bot language for this server.")
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
@app_commands.describe(language_code="Language to apply (English or Spanish)")
@app_commands.choices(language_code=language_choices)
async def language_slash_command(
    interaction: discord.Interaction,
    language_code: Optional[app_commands.Choice[str]] = None,
):
    # Language management can be quick, but defer to be safe and to unify UX
    if not interaction.response.is_done():
        try:
            await interaction.response.defer(thinking=False, ephemeral=True)
        except Exception:
            pass
    if interaction.guild is None:
        await _send_text_response(
            interaction,
            "This command can only be used inside a server.",
            ephemeral=True,
        )
        return

    member = interaction.user if isinstance(interaction.user, discord.Member) else interaction.guild.get_member(interaction.user.id)
    if not member or not member.guild_permissions.administrator:
        await _send_text_response(
            interaction,
            "Only server administrators can change the bot language.",
            ephemeral=True,
        )
        return

    if language_code is None:
        info_embed = discord.Embed(
            title="Language Settings",
            description="Select a language to apply. Available options: English (`/language English`) or Spanish (`/language Spanish`).",
            color=0x5865F2,
        )
        await _dispatch_command_result(interaction, info_embed)
        return

    language_command.set_language_for_guild(interaction.guild.id, language_code.value)

    lang_display = "English" if language_code.value == 'en' else "Spanish"
    confirmation = discord.Embed(
        title="Language Updated",
        description=f"The bot will now respond in **{lang_display}** for this server.",
        color=0x57F287,
    )
    await _dispatch_command_result(interaction, confirmation, ephemeral_override=True)

# Try to pre-load commands at startup, but don't crash the bot if it fails
try:
    cmd_manager.loadCommands()
except Exception as e:
    print(f"Warning: failed to load commands at startup: {e}")

@client.event
async def on_ready():
    global _slash_synced
    if not _slash_synced:
        try:
            synced = await tree.sync()
            print(f"Synced {len(synced)} slash commands globally")
        except Exception as e:
            print(f"Warning: failed to sync slash commands: {e}")
        else:
            _slash_synced = True

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
