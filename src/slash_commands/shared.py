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


async def run_lookup_command(
    interaction: discord.Interaction,
    module,
    item_name: Optional[str],
    *,
    fallback: str = "Item not found."
):
    """
    Run a lookup command (equipment, weapon, talent, mantra, outfit, kit, help).
    This function handles the common logic for all lookup commands.
    """
    # For help command, item_name is None
    if item_name is None:
        # Assume this is the help command
        if not interaction.response.is_done():
            try:
                await interaction.response.defer(thinking=False, ephemeral=True)
            except Exception:
                pass
        embed = module.execute("slash", None)
        await dispatch_command_result(interaction, embed, fallback="Unable to display the help menu.")
        return
    
    # For all other lookups, validate item_name
    cleaned_query = item_name.strip()
    if not cleaned_query:
        await send_text_response(interaction, "Please provide a name to search.", ephemeral=True)
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
        await dispatch_command_result(interaction, error_embed, ephemeral_override=True)
        return

    await dispatch_command_result(interaction, result, fallback=fallback)
