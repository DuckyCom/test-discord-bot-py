from handlers.spellCheck import find
from handlers.spellCheck import mantra_names as name_list
from handlers.backbone import searchTableByName
import embedBuilder.mantraEmbed as emb

def execute(name):
    substring = name.lower()
    match = next((name for name in name_list if substring.lower() in name.lower()), None)

    if match:
        mantra_data = searchTableByName('mantras', match)
        return emb.build_mantra_embed(mantra_data)
    else:
        most_similar_name = find(name, 'mantra')
        mantra_data = searchTableByName('mantras', most_similar_name)
        return emb.build_mantra_embed(mantra_data)