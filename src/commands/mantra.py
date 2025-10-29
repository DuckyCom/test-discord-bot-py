from handlers.spellCheck import find
from handlers import spellCheck
from handlers.backbone import searchTableByName
import embedBuilder.mantraEmbed as emb

def execute(name, guild_id=None):
    # Ensure names are loaded
    spellCheck._ensure_names_loaded()
    name_list = spellCheck.mantra_names
    
    substring = name.lower()
    match = next((mname for mname in name_list if substring.lower() in mname.lower()), None)

    if match:
        mantra_data = searchTableByName('mantras', match)
        return emb.build_mantra_embed(mantra_data, guild_id)
    else:
        most_similar_name = find(name, 'mantra')
        mantra_data = searchTableByName('mantras', most_similar_name)
        return emb.build_mantra_embed(mantra_data, guild_id)