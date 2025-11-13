import json

STAT_ORDER = ['Health', 'Ether', 'Physical armor', 'Elemental armor', 'Sanity', 'Posture']
SLOT_ORDER = ['Head', 'Face', 'Ears', 'Torso', 'Arms', 'Legs', 'Rings']

def load_pip_data():
    pip_file = 'data/pipvalues.json'
    with open(pip_file, 'r') as f:
        return json.load(f)

PIP_DATA = load_pip_data()

def calculate_kit_stats(item):
    stats = {}
    slot = item.get('slot', '')
    
    for i in range(1, 5):
        innate = item.get(f'innate_{i}', {})
        if innate.get('type') == 'none':
            continue
        stat_type = 'Health' if innate.get('type') == 'Hp' else innate.get('type')
        stats[stat_type] = stats.get(stat_type, 0) + innate.get('stat', 0)
    
    if item.get('stars', 0) == 3 and slot in PIP_DATA['star_hp_bonus']:
        stats['Health'] = stats.get('Health', 0) + PIP_DATA['star_hp_bonus'][slot]
    
    pip_values = PIP_DATA['pip_values']
    for rarity, selections in item.get('pipSelections', {}).items():
        for stat_type in selections:
            if stat_type in pip_values and slot in pip_values[stat_type]:
                if rarity in pip_values[stat_type][slot]:
                    stats[stat_type] = stats.get(stat_type, 0) + pip_values[stat_type][slot][rarity]
            
            if stat_type == 'Sanity' and rarity in PIP_DATA['sanity_ether_bonus']:
                stats['Ether'] = stats.get('Ether', 0) + PIP_DATA['sanity_ether_bonus'][rarity]
    
    return stats