from _HANDLERS.spellCheckManager import find
from _HANDLERS import spellCheckManager
from _HANDLERS.dataManager import searchTableByName
import plugins.embedBuilder.talentEmbed as emb

def execute(name, guild_id=None):
    # Ensure names are loaded
    spellCheckManager._ensure_names_loaded()
    name_list = spellCheckManager.talent_names
    
    substring = name.lower()
    match = next((tname for tname in name_list if substring.lower() in tname.lower()), None)

    if match:
        talent_data = searchTableByName('talents', match)
        return emb.build_talent_embed(talent_data, guild_id)
    else:
        most_similar_name = find(name, 'talent')
        talent_data = searchTableByName('talents', most_similar_name)
        return emb.build_talent_embed(talent_data, guild_id)