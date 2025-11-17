"""
Lookup slash commands - Help, Equipment, Weapon, Talent, Mantra, Outfit, Kit, Language
"""
import discord
from discord import app_commands
from typing import Optional

import commands.help as help_command
import commands.equipment as equipment_command
import commands.weapon as weapon_command
import commands.talent as talent_command
import commands.mantra as mantra_command
import commands.outfit as outfit_command
import commands.kit as kit_command
import commands.language as language_command


async def execute_help(interaction: discord.Interaction):
    """Execute the /help command."""
    # Import here to avoid circular dependency
    from bot import _run_lookup_command
    await _run_lookup_command(interaction, help_command, item_name=None)


async def execute_equipment(interaction: discord.Interaction, equipment_name: str):
    """Execute the /equipment command."""
    from bot import _run_lookup_command
    await _run_lookup_command(interaction, equipment_command, item_name=equipment_name)


async def execute_weapon(interaction: discord.Interaction, weapon_name: str):
    """Execute the /weapon command."""
    from bot import _run_lookup_command
    await _run_lookup_command(interaction, weapon_command, item_name=weapon_name)


async def execute_talent(interaction: discord.Interaction, talent_name: str):
    """Execute the /talent command."""
    from bot import _run_lookup_command
    await _run_lookup_command(interaction, talent_command, item_name=talent_name)


async def execute_mantra(interaction: discord.Interaction, mantra_name: str):
    """Execute the /mantra command."""
    from bot import _run_lookup_command
    await _run_lookup_command(interaction, mantra_command, item_name=mantra_name)


async def execute_outfit(interaction: discord.Interaction, outfit_name: str):
    """Execute the /outfit command."""
    from bot import _run_lookup_command
    await _run_lookup_command(interaction, outfit_command, item_name=outfit_name)


async def execute_kit(interaction: discord.Interaction, kit_name: str):
    """Execute the /kit command."""
    from bot import _run_lookup_command
    await _run_lookup_command(interaction, kit_command, item_name=kit_name)


async def execute_language(interaction: discord.Interaction, language_code: Optional[app_commands.Choice[str]] = None):
    """Execute the /language command."""
    from bot import _send_text_response, _dispatch_command_result
    
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
