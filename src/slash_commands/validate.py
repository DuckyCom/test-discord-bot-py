"""
/validate slash command - Validate a Deepwoken build for legality
"""
import discord
from typing import Optional

from .helpers import extract_build_id, get_build_link_from_reply, send_missing_link_error
from .shared import dispatch_command_result
import plugins._DWBAPIWRAPPER as dwb
import interactions.validate as validate_interaction


async def execute(interaction: discord.Interaction, build_link: Optional[str] = None):
    """Execute the /validate command."""
    if not interaction.response.is_done():
        try:
            await interaction.response.defer(thinking=True, ephemeral=False)
        except Exception:
            pass

    # Try to get build link from parameter or replied message
    final_build_link = await get_build_link_from_reply(interaction, build_link)
    
    if not final_build_link:
        await send_missing_link_error(interaction, "validate")
        return

    build_id = extract_build_id(final_build_link)
    
    try:
        build = dwb.dwbBuild(build_id)
    except Exception as exc:
        error_embed = discord.Embed(
            title="Build Load Failed",
            description=f"Could not load build from the provided link. Make sure it's a valid Deepwoken builder URL.\n\nError: {exc}",
            color=0xED4245,
        )
        await dispatch_command_result(interaction, error_embed, ephemeral_override=True)
        return

    try:
        embed = validate_interaction.execute(build, None)
        
        if not interaction.response.is_done():
            await interaction.response.defer(thinking=False, ephemeral=False)
        await interaction.followup.send(embed=embed, ephemeral=False)
    except Exception as exc:
        error_embed = discord.Embed(
            title="Validation Failed",
            description=f"An error occurred while validating the build.\n\nError: {exc}",
            color=0xED4245,
        )
        await dispatch_command_result(interaction, error_embed, ephemeral_override=True)
