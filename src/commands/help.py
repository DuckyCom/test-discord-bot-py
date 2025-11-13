import discord
from utils.language_manager import language_manager

def execute(message, guild_id = None):
    # Accept both message object or string (no error)
    if isinstance(message, str):
        # If accidentally called with string (shouldn't, but fails gracefully)
        guild_id = None
    else:
        guild_id = message.guild.id if hasattr(message, 'guild') and message.guild else None

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
    embed.add_field(
        name=language_manager.get_text(guild_id, 'admin_commands'),
        value=language_manager.get_text(guild_id, 'help_admin_value'),
        inline=False
    )
    embed.add_field(
        name=language_manager.get_text(guild_id, 'clopen_commands'),
        value=language_manager.get_text(guild_id, 'help_clopen_value'),
        inline=False
    )
    embed.set_footer(text=language_manager.get_text(guild_id, 'help_footer'))
    return embed
