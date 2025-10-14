from handlers.spellCheck import find
from handlers.spellCheck import weapon_names as name_list
from handlers.backbone import searchTableByName
import embedBuilder.weaponEmbed as emb

def execute(name):
    substring = name.lower()
    match = next((name for name in name_list if substring.lower() in name.lower()), None)

    if match:
        weapon_data = searchTableByName('weapons', match)
        return emb.build_weapon_embed(weapon_data)
    else:
        most_similar_name = find(name, 'weapon')
        weapon_data = searchTableByName('weapons', most_similar_name)
        return emb.build_weapon_embed(weapon_data)