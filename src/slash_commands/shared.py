"""
Shared utilities for slash commands - avoids circular imports
"""
import discord
from typing import Optional


async def send_text_response(interaction: discord.Interaction, content: str, *, ephemeral: bool = True):
    """Send a text-only response to an interaction."""
    if not interaction.response.is_done():
        try:
            await interaction.response.defer(thinking=False, ephemeral=ephemeral)
        except Exception:
            pass
    await interaction.followup.send(content, ephemeral=ephemeral)


async def dispatch_command_result(
    interaction: discord.Interaction,
    result,
    *,
    fallback: str = "No data was returned.",
    ephemeral_override: Optional[bool] = None,
):
    """
    Dispatch the result of a command execution to the user.
    Handles both embed-only and (embed, meta) tuple results.
    """
    if isinstance(result, tuple):
        embed, meta = result
    else:
        embed, meta = result, None

    ephemeral = ephemeral_override if ephemeral_override is not None else bool(meta and meta.get('auto_delete'))

    if not embed:
        await send_text_response(interaction, fallback, ephemeral=True)
        return

    # Ensure interaction is acknowledged, then send followup
    if not interaction.response.is_done():
        try:
            await interaction.response.defer(thinking=False, ephemeral=ephemeral)
        except Exception:
            pass
    await interaction.followup.send(embed=embed, ephemeral=ephemeral)
