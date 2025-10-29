import discord
from utils.language_manager import language_manager

def execute(message):
    guild_id = message.guild.id if message.guild else None
    
    embed = discord.Embed(
        title=language_manager.get_text(guild_id, 'help_menu'),
        description=language_manager.get_text(guild_id, 'help_description'),
        color=discord.Color.blurple()
    )

    embed.add_field(
        name=language_manager.get_text(guild_id, 'lookup_commands'),
        value=language_manager.get_text(guild_id, 'help_lookup_value'),
        inline=False
    )

    embed.add_field(
        name=language_manager.get_text(guild_id, 'analytics_commands'),
        value=language_manager.get_text(guild_id, 'help_analytics_value'),
        inline=False
    )

    embed.set_footer(text=language_manager.get_text(guild_id, 'help_footer'))
    return embed