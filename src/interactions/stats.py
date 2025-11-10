from plugins.statEvo import statevograph
import discord
from utils.language_manager import language_manager

def execute(build, guild_id=None):
    buf = statevograph(build, guild_id)
    file = discord.File(buf, filename="evo_plot.png")
    
    title = language_manager.get_text(guild_id, 'stat_evolution_title')
    embed = discord.Embed(
        title = title,
        color=discord.Color.blurple()
    )
    embed.set_image(url="attachment://evo_plot.png")
    return embed, file