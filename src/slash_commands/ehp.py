"""
/ehp slash command - Calculate Effective Health Points for a Deepwoken build
"""
import discord
from typing import Optional
import io
from PIL import Image

from .helpers import extract_build_id, get_build_link_from_reply, send_missing_link_error
from .shared import dispatch_command_result
import plugins._DWBAPIWRAPPER as dwb
from _HANDLERS.dataManager import searchTableByName
from plugins.ehpbreakdown import plot_breakdown
from plugins.kitTools import calculate_kit_stats
from utils.language_manager import language_manager


async def execute(interaction: discord.Interaction, kit_id: Optional[str] = None, build_link: Optional[str] = None):
    """Execute the /ehp command."""
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
        await dispatch_command_result(interaction, error_embed, ephemeral_override=True)
        return

    try:
        guild_id = interaction.guild.id if interaction.guild else None

        # If a kit is provided, compute totals (HP and Physical armor) and render a single chart
        if kit_id:
            kit_id_clean = kit_id.strip()
            kit_data = searchTableByName('kits', kit_id_clean, 'kit_share_id')
            if not kit_data:
                title = language_manager.get_text(guild_id, 'kit_not_found')
                description = language_manager.get_text(guild_id, 'kit_not_found_description').format(kit_id=kit_id_clean)
                error_embed = discord.Embed(title=title, description=description, color=0xED4245)
                await dispatch_command_result(interaction, error_embed, ephemeral_override=True)
                return

            # Aggregate kit totals with calculate_kit_stats, supporting possible shapes
            items = None
            # Common shapes observed in repo
            for key_path in (
                ('kit_data',),
                ('data', 'items'),
                ('items',),
            ):
                node = kit_data
                try:
                    for k in key_path:
                        node = node.get(k, None)
                    if isinstance(node, list):
                        items = node
                        break
                except Exception:
                    continue

            total_health = 0
            total_phys = 0
            if items:
                for item in items:
                    stats = calculate_kit_stats(item)
                    total_health += stats.get('Health', 0)
                    total_phys += stats.get('Physical armor', 0)

            buf = plot_breakdown(build, talentBase=dwb.talentBase, params={
                'dps': 100, 'pen': 50, 'kithp': total_health, 'kitresis': total_phys
            })

            img = Image.open(buf)
            output_buf = io.BytesIO()
            img.save(output_buf, format="PNG")
            output_buf.seek(0)

            file = discord.File(fp=output_buf, filename="kit_breakdown.png")

            title = language_manager.get_text(guild_id, 'ehp_breakdown_title_single').format(name=build.name)
            subtitle = f" (Kit: +{total_health} HP, +{total_phys}% Phys Armor)" if (total_health or total_phys) else ""
            embed = discord.Embed(
                title=title + subtitle,
                color=discord.Color.blurple()
            )
            embed.set_image(url="attachment://kit_breakdown.png")

            if not interaction.response.is_done():
                await interaction.response.defer(thinking=False, ephemeral=False)
            await interaction.followup.send(embed=embed, file=file, ephemeral=False)
            return

        # Default: two combined charts (Phys kit defaults and HP kit defaults)
        params_phys = {'dps': 100, 'pen': 50, 'kithp': 112, 'kitresis': 33}
        params_hp = {'dps': 100, 'pen': 50, 'kithp': 154, 'kitresis': 4}

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

        title = language_manager.get_text(guild_id, 'ehp_breakdown_title').format(name=build.name)
        embed = discord.Embed(
            title=title,
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
        await dispatch_command_result(interaction, error_embed, ephemeral_override=True)
