import discord
from plugins.ehpbreakdown import plot_breakdown
import plugins._DWBAPIWRAPPER as dwb
from PIL import Image
import io
from utils.language_manager import language_manager
from _HANDLERS.dataManager import searchTableByName
from plugins.kitTools import calculate_kit_stats

def _aggregate_kit_stats(kit_data):
    """Aggregate total Health and Physical armor from kit_data structure."""
    total_health = 0
    total_phys_armor = 0
    for item in kit_data.get('kit_data', []) or []:
        stats = calculate_kit_stats(item)
        total_health += stats.get('Health', 0)
        total_phys_armor += stats.get('Physical armor', 0)
    return total_health, total_phys_armor


def execute(build, guild_id=None, kit_id=None):
    """
    Reply EHP command.
    - Default: render two charts (kithp=112/154, kitresis=33/4)
    - If kit_id is provided: compute kit totals and render a SINGLE chart using
      kithp = kit_total_health and kitresis = kit_total_physical_armor.
    """
    # If a kit is provided, compute its totals and render a single chart
    if kit_id:
        kit_data = searchTableByName('kits', kit_id, 'kit_share_id')
        if not kit_data:
            # Kit not found -> return a visible error embed similar to other commands
            title = language_manager.get_text(guild_id, 'kit_not_found')
            description = language_manager.get_text(guild_id, 'kit_not_found_description').format(kit_id=kit_id)
            embed = discord.Embed(title=f"{title}", description=description, color=0xED4245)
            return embed, None

        kit_hp, kit_phys = _aggregate_kit_stats(kit_data)
        buf = plot_breakdown(build, talentBase=dwb.talentBase, params={
            'dps': 100, 'pen': 50, 'kithp': kit_hp, 'kitresis': kit_phys
        })

        img = Image.open(buf)
        output_buf = io.BytesIO()
        img.save(output_buf, format="PNG")
        output_buf.seek(0)

        file = discord.File(fp=output_buf, filename="kit_breakdown.png")
        title = language_manager.get_text(guild_id, 'ehp_breakdown_title').format(name=build.name)
        subtitle = f" (Kit: +{kit_hp} HP, +{kit_phys}% Phys Armor)" if (kit_hp or kit_phys) else ""
        embed = discord.Embed(
            title=title + subtitle,
            color=discord.Color.blurple()
        )
        embed.set_image(url="attachment://kit_breakdown.png")
        return embed, file

    # Default behavior: two charts combined
    buf1 = plot_breakdown(build, talentBase=dwb.talentBase, params={'dps': 100, 'pen': 50, 'kithp': 112, 'kitresis': 33})
    buf2 = plot_breakdown(build, talentBase=dwb.talentBase, params={'dps': 100, 'pen': 50, 'kithp': 154, 'kitresis': 4})

    img1 = Image.open(buf1)
    img2 = Image.open(buf2)

    total_height = img1.height + img2.height
    max_width = max(img1.width, img2.width)
    combined = Image.new("RGBA", (max_width, total_height), (255,255,255,0))
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

    return embed, file
