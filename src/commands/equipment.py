from _HANDLERS.spellCheckManager import find
from _HANDLERS import spellCheckManager
from _HANDLERS.dataManager import searchTableByName
import plugins.embedBuilder.equipmentEmbed as emb

def execute(name, guild_id=None):
    # Ensure names are loaded
    spellCheckManager._ensure_names_loaded()
    name_list = spellCheckManager.equipment_names
    
    substring = name.lower()
    match = next((ename for ename in name_list if substring.lower() in ename.lower()), None)

    if match:
        equipment_data = searchTableByName('equipment', match)
        return emb.build_equipment_embed(equipment_data, guild_id)
    else:
        most_similar_name = find(name, 'equipment')
        equipment_data = searchTableByName('equipment', most_similar_name)
        return emb.build_equipment_embed(equipment_data, guild_id)
    