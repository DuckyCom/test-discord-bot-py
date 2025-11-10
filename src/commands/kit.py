from handlers.dataManager import searchTableByName
import embedBuilder.kitEmbed as emb
import discord
from utils.language_manager import language_manager

def execute(kit_id, guild_id=None):
    # Search for kit by ID
    kit_data = searchTableByName('kits', kit_id, 'kit_share_id')
    
    if not kit_data:
        # Return error embed with Spanish/English translation and auto-delete meta
        title = language_manager.get_text(guild_id, 'kit_not_found')
        description = language_manager.get_text(guild_id, 'kit_not_found_description').format(kit_id=kit_id)
        embed = discord.Embed(title=f"{title}", description=description, color=0xED4245)
        meta = { 'auto_delete': True, 'delete_user_message': True, 'timeout': 10 }
        return (embed, meta)
    
    return emb.build_kit_embed(kit_data, guild_id)
