"""
/ehp slash command - Calculate Effective Health Points for a Deepwoken build
"""
import discord
from discord import app_commands
from typing import Optional
import io
from PIL import Image

from .helpers import extract_build_id, get_build_link_from_reply, send_missing_link_error
import plugins._DWBAPIWRAPPER as dwb
from _HANDLERS.dataManager import searchTableByName
from plugins.ehpbreakdown import plot_breakdown


async def execute(interaction: discord.Interaction, kit_id: Optional[str] = None, build_link: Optional[str] = None):
    """Execute the /ehp command."""
    # Import here to avoid circular dependency
    from bot import _dispatch_command_result
    
    if not interaction.response.is_done():
        try:
            await interaction.response.defer(thinking=True, ephemeral=False)
        except Exception:
            pass

    # Try to get build link from parameter or replied message
    final_build_link = await get_build_link_from_reply(interaction, build_link)
    
    if not final_build_link:
        await send_missing_link_error(interaction, "ehp")
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
        await _dispatch_command_result(interaction, error_embed, ephemeral_override=True)
        return

    # Handle optional kit
    extra_hp = 0
    if kit_id:
        kit_id_clean = kit_id.strip()
        kit_data = searchTableByName('kits', kit_id_clean, 'kit_share_id')
        if kit_data:
            # Sum HP from kit items
            for item in kit_data.get('data', {}).get('items', []):
                extra_hp += item.get('hp', 0)

    try:
        # Adjust kithp params for both phys and hp builds
        params_phys = {'dps': 100, 'pen': 50, 'kithp': 112 + extra_hp, 'kitresis': 33}
        params_hp = {'dps': 100, 'pen': 50, 'kithp': 154 + extra_hp, 'kitresis': 4}
        
        buf1 = plot_breakdown(build, talentBase=dwb.talentBase, params=params_phys)
        buf2 = plot_breakdown(build, talentBase=dwb.talentBase, params=params_hp)

        img1 = Image.open(buf1)
        img2 = Image.open(buf2)

        total_height = img1.height + img2.height
        max_width = max(img1.width, img2.width)
        combined = Image.new("RGBA", (max_width, total_height), (255, 255, 255, 0))
        combined.paste(img1, (0, 0))
        combined.paste(img2, (0, img1.height))

        output_buf = io.BytesIO()
        combined.save(output_buf, format="PNG")
        output_buf.seek(0)

        file = discord.File(fp=output_buf, filename="kit_breakdown.png")

        title = f"Physical EHP Breakdown — {build.name}"
        if kit_id and extra_hp > 0:
            title += f" (+{extra_hp} HP from kit {kit_id_clean})"
        
        embed = discord.Embed(
            title=title,
            description="Top image: Phys Kit\nBottom image: HP Kit",
            color=discord.Color.blurple()
        )
        embed.set_image(url="attachment://kit_breakdown.png")

        if not interaction.response.is_done():
            await interaction.response.defer(thinking=False, ephemeral=False)
        await interaction.followup.send(embed=embed, file=file, ephemeral=False)

    except Exception as exc:
        error_embed = discord.Embed(
            title="EHP Calculation Failed",
            description=f"An error occurred while calculating EHP.\n\nError: {exc}",
            color=0xED4245,
        )
        await _dispatch_command_result(interaction, error_embed, ephemeral_override=True)
