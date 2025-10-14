from handlers.spellCheck import find
from handlers.spellCheck import talent_names as name_list
from handlers.backbone import searchTableByName
import embedBuilder.talentEmbed as emb

def execute(name):
    substring = name.lower()
    match = next((name for name in name_list if substring.lower() in name.lower()), None)

    if match:
        talent_data = searchTableByName('talents', match)
        return emb.build_talent_embed(talent_data)
    else:
        most_similar_name = find(name, 'talent')
        talent_data = searchTableByName('talents', most_similar_name)
        return emb.build_talent_embed(talent_data)