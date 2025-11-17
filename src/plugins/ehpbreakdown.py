import io

def ehp_breakdown(build, talentBase, params={'dps':100, 'pen':50, 'kithp': 112, 'kitresis':33}):
    breakdown = {}

    vitality_bonus = build.traits['Vitality'] * 10
    breakdown['Trait'] = vitality_bonus

    power_bonus = build.rawdata['stats']['power'] * 4
    breakdown['Power'] = power_bonus

    breakdown['Base HP'] = 200

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
    kitresis = build.scalePhys(params['kitresis'], build.talents, build.outfit)
    EHP = (scaledDps * (total_health + params['kithp']))/((scaledDps)*build.resisCoefficient(params['pen'], kitresis, flags[0]))
    EHP *= ((30/(100 - flags[1]) + 0.7) if flags[1] != 0 else 1) * ((25/(100 - flags[2]) + 0.75 if flags[2] != 0 else 1))
    breakdown['Final EHP'] = round(EHP)
    
    return breakdown


def plot_breakdown(build, talentBase, params={'dps':100, 'pen':50, 'kithp':112, 'kitresis':33}):
    breakdown = ehp_breakdown(build, talentBase, params)
    
    # Extract Final EHP
    if 'Final EHP' in breakdown:
        ehp_val = breakdown.pop('Final EHP')
    else:
        ehp_val = None
    
    # Calculate resistance multiplier
    flags = build.flags
    kitresis = build.scalePhys(params['kitresis'], build.talents, build.outfit)
    mag_factor = 1 / build.resisCoefficient(params['pen'], kitresis, flags[0])
    
    # Apply additional multipliers from flags
    flag_mult = 1.0
    flag_mult *= ((30/(100 - flags[1]) + 0.7) if flags[1] != 0 else 1)
    flag_mult *= ((25/(100 - flags[2]) + 0.75) if flags[2] != 0 else 1)
    
    total_mag_factor = mag_factor * flag_mult
    
    components = list(breakdown.keys())
    values = list(breakdown.values())
    
    # Scale all values by the resistance and flag multipliers for EHP display
    mag_values = [v * total_mag_factor for v in values]
    
    # Calculate kit HP contribution to EHP
    kit_ehp = params['kithp'] * total_mag_factor

    # Lazy import matplotlib
    import matplotlib
    matplotlib.use('Agg')
    # Reduce matplotlib logging noise in some environments
    try:
        matplotlib.set_loglevel("error")
    except Exception:
        pass
    import matplotlib.pyplot as plt
    
    # Register custom fonts
    try:
        from utils.font_manager import _fonts_registered
    except Exception:
        pass
    
    plt.figure(figsize=(8, 3.8))
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams.update({
        'font.family': 'Helvetica Neue',
        'axes.edgecolor': 'gray',
        'axes.linewidth': 0.7
    })
    
    # Plot raw HP values and EHP values
    bars1 = plt.barh(components, values, height=0.32, color="#f42307", 
                     label="Raw", edgecolor="#333333", linewidth=0.8)
    bars2 = plt.barh(components, mag_values, height=0.32, color='#3c5fa5', 
                     alpha=0.24, label="EHP w/ PEN/Resist", edgecolor="#333333", linewidth=0.6)
    
    # Add Final EHP line at the actual calculated position
    if ehp_val:
        plt.axvline(ehp_val, color="#837C8A", linestyle='--', 
                   label=f'Final EHP = {ehp_val:.0f}', linewidth=1.2)
    
    # Add value labels
    for bar, value, magv in zip(bars1, values, mag_values):
        # Raw value label (centered in red bar)
        plt.text(value/2, bar.get_y() + bar.get_height() / 2,
                 f'{value:.0f}', va='center', ha='center', 
                 fontsize=9, color='white', weight='bold')
        
        # EHP value label (to the right of blue bar)
        if magv > value:  # Only show if visible
            plt.text(magv + 8, bar.get_y() + bar.get_height() / 2,
                     f'{magv:.0f}', va='center', ha='left', 
                     fontsize=8, color='#205375', weight='bold')
    
    plt.xlabel('Health Contribution', fontsize=10, weight='bold', labelpad=4)
    plt.xticks(fontsize=9)
    plt.yticks(fontsize=9)
    plt.legend(fontsize=8, loc='lower right', frameon=False)
    plt.grid(axis='x', color='#eeeeee', linewidth=0.65, alpha=0.6)
    
    # Fixed x-axis scale of 800
    plt.xlim(0, 800)
    
    plt.tight_layout(pad=1.7)
    plt.box(False)
    
    buf = io.BytesIO()
    try:
        plt.savefig(buf, format='png', bbox_inches='tight')
    finally:
        buf.seek(0)
        plt.close()
    
    return buf
