import matplotlib.pyplot as plt
from plugins.dwbapi import dwbBuild
from plugins.dwbapi import talentBase
import io

def ehp_breakdown(build, talentBase, params={'dps':100, 'pen':50, 'kithp': 0, 'kitresis':50}):
    breakdown = {}

    vitality_bonus = build.traits['Vitality'] * 10
    breakdown['Trait'] = vitality_bonus

    power_bonus = build.rawdata['stats']['power'] * 4
    breakdown['Power'] = power_bonus

    breakdown['Base HP'] = 196

    for stat in build.post['base']:
        
        if stat == 'Fortitude':
            f = build.post['base'][stat]
            fort_hp = f/2 if f <= 50 else (f - 50)/4 + 25
            breakdown['Fortitude'] = fort_hp

        
        stat_health_talents = 0
        for talent in build.talents:
            for tb in talentBase:
                if tb.get('name') == talent:
                    if tb.get('data', {}).get('stats', {}).get(stat, 0) != 0:
                        stat_health_talents += tb.get('data', {}).get('stats', {}).get('health', 0)
        if stat_health_talents:
            breakdown[f'{stat} health talents'] = stat_health_talents

    
    attunement_health = 0
    attunements = build.post.get('attunements', {})
    for attunement in attunements:
        
        for talent in build.talents:
            for tb in talentBase:
                if tb.get('name') == talent:
                    if tb.get('data', {}).get('attunements', {}).get(attunement, 0) != 0:
                        attunement_health += tb.get('data', {}).get('stats', {}).get('health', 0)
    if attunement_health:
        breakdown['Attunement health talents'] = attunement_health

    
    misc_health = 0
    for talent in build.talents:
        for tb in talentBase:
            if tb.get('name') == talent:
                health_value = tb.get('data', {}).get('stats', {}).get('health', 0)
                if health_value:
                    already_counted = False
                    for key in breakdown:
                        if key.endswith('health talents') and health_value in breakdown[key:]:
                            already_counted = True
                            break
                    if not already_counted:
                        misc_health += health_value
    if misc_health:
        breakdown['+HP Talents'] = misc_health

    total_health = sum(breakdown.values())
    breakdown['Total'] = total_health

    
    flags = build.flags
    scaledDps = params['dps'] * build.resisCoefficient(params['pen'], 10, 50) if flags[3] else params['dps']
    kitresis = params['kitresis']
    EHP = (scaledDps * (total_health + params['kithp']))/((scaledDps)*build.resisCoefficient(params['pen'], kitresis, flags[0]))
    EHP *= ((30/(100 - flags[1]) + 0.7) if flags[1] != 0 else 1) * ((25/(100 - flags[2]) + 0.75 if flags[2] != 0 else 1))
    breakdown['Final EHP'] = round(EHP)
    
    return breakdown


def plot_breakdown(build, talentBase, params={'dps':100, 'pen':50, 'kithp':0, 'kitresis':50}):
    breakdown = ehp_breakdown(build, talentBase, params)
    components = list(breakdown.keys())
    values = list(breakdown.values())

    if 'Final EHP' in breakdown:
        ehp_val = breakdown.pop('Final EHP')
        components = list(breakdown.keys())
        values = list(breakdown.values())
    else:
        ehp_val = None

    # Scale factor
    flags = build.flags
    kitresis = params['kitresis']
    mag_factor = 1 / build.resisCoefficient(params['pen'], kitresis, flags[0])
    mag_values = [v * mag_factor for v in values]

    plt.figure(figsize=(8, 3.8))
    bars1 = plt.barh(components, values, height=0.32, color="#f42307", label="Raw", edgecolor="#333333", linewidth=0.8)
    bars2 = plt.barh(components, mag_values, height=0.32, color='#3c5fa5', alpha=0.24, label="EHP w/ PEN/Resist", edgecolor="#333333", linewidth=0.6)

    max_value = max(max(mag_values), max(values)) if mag_values and values else 0
    
    if ehp_val:
        line_pos = max(ehp_val, max_value)
        plt.axvline(line_pos, color="#837C8A", linestyle='--', label=f'Final EHP = {ehp_val:.0f}', linewidth=1.2)

    for bar, value, magv in zip(bars1, values, mag_values):
        plt.text(value/2, bar.get_y() + bar.get_height() / 2,
                 f'{value:.0f}', va='center', ha='center', fontsize=9, color='white', weight='bold')
        plt.text(magv + 5, bar.get_y() + bar.get_height() / 2,
                 f'{magv:.0f}', va='center', ha='center', fontsize=8, color='#205375', weight='bold')

    plt.xlabel('Health Contribution', fontsize=10, weight='bold', labelpad=4)
    plt.xticks(fontsize=9)
    plt.yticks(fontsize=9)
    plt.title(f"EHP Breakdown — {build.name}", fontsize=11, weight='bold', pad=8)
    plt.legend(fontsize=8, loc='lower right', frameon=False)
    plt.grid(axis='x', color='#eeeeee', linewidth=0.65, alpha=0.6)
    
    if ehp_val:
        plt.xlim(0, max(max_value, ehp_val) * 1.15)
    
    plt.tight_layout(pad=1.7)
    plt.box(False)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf
