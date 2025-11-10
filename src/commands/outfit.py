from handlers.spellCheckManager import find
from handlers import spellCheckManager
from handlers.dataManager import searchTableByName
import embedBuilder.outfitEmbed as emb

def execute(name, guild_id=None):
    # Ensure names are loaded
    spellCheckManager._ensure_names_loaded()
    name_list = spellCheckManager.outfit_names
    
    substring = name.lower()
    match = next((oname for oname in name_list if substring.lower() in oname.lower()), None)

    if match:
        outfit_data = searchTableByName('outfits', match)
        return emb.build_outfit_embed(outfit_data, guild_id)
    else:
        most_similar_name = find(name, 'outfit')
        outfit_data = searchTableByName('outfits', most_similar_name)
        return emb.build_outfit_embed(outfit_data, guild_id)