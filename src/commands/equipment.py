from handlers.spellCheck import find
from handlers.spellCheck import equipment_names as name_list
from handlers.backbone import searchTableByName
import embedBuilder.equipmentEmbed as emb

def execute(name):
    substring = name.lower()
    match = next((name for name in name_list if substring.lower() in name.lower()), None)

    if match:
        equipment_data = searchTableByName('equipment', match)
        print(equipment_data)
        return emb.build_equipment_embed(equipment_data)
    else:
        most_similar_name = find(name, 'equipment')
        equipment_data = searchTableByName('equipment', most_similar_name)
        return emb.build_equipment_embed(equipment_data)
    