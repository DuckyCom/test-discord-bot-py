from _HANDLERS.spellCheckManager import find
from _HANDLERS import spellCheckManager
from _HANDLERS.dataManager import searchTableByName
import plugins.embedBuilder.mantraEmbed as emb

def execute(name, guild_id=None):
    # Ensure names are loaded
    spellCheckManager._ensure_names_loaded()
    name_list = spellCheckManager.mantra_names
    
    substring = name.lower()
    match = next((mname for mname in name_list if substring.lower() in mname.lower()), None)

    if match:
        mantra_data = searchTableByName('mantras', match)
        return emb.build_mantra_embed(mantra_data, guild_id)
    else:
        most_similar_name = find(name, 'mantra')
        mantra_data = searchTableByName('mantras', most_similar_name)
        return emb.build_mantra_embed(mantra_data, guild_id)