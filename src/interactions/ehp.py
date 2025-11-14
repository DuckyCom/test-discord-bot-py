import discord
from plugins.ehpbreakdown import plot_breakdown
import plugins._DWBAPIWRAPPER as dwb
from PIL import Image
import io
from utils.language_manager import language_manager

def execute(build, guild_id=None):
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
