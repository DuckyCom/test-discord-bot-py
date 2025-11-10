from handlers.dataManager import searchTableByName
import embedBuilder.kitEmbed as emb

def execute(kit_id, guild_id=None):
    # Search for kit by ID
    kit_data = searchTableByName('kits', kit_id, 'kit_share_id')
    
    if not kit_data:
        return None  # Handle error in main bot logic
    
    return emb.build_kit_embed(kit_data, guild_id)
