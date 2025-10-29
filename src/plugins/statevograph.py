from plugins.shrineoforder import order
import io

def statevograph(build, guild_id=None):
    # Lazy import matplotlib - only loads when actually generating graphs (~70MB RAM saved on startup)
    import matplotlib
    matplotlib.use('Agg')  # Headless backend - saves ~5-10MB RAM
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from utils.language_manager import language_manager
    
    # Register custom fonts (optional). If unavailable, we'll use a safe default font.
    try:
        from utils.font_manager import _fonts_registered  # side-effect: registers fonts if present
    except Exception:
        pass  # Continue with matplotlib's bundled fonts
    
    playerStats = {"Race": build.race, "PointsSpent": 0}
    flatpre = build.flatpre
    flatpost = build.flatpost
    ordered_stats = order(build.flatpre.copy(), playerStats)

    base_stats = {
        "Strength", "Fortitude", "Agility", "Intelligence", "Willpower", "Charisma"
    }
    weapon_stats = {"Medium Wep.", "Light Wep.", "Heavy Wep."}
    attunement_stats = {
        "Frostdraw", "Flamecharm", "Shadowcast", "Galebreathe", "Thundercall", "Bloodrend", "Ironsing"
    }

    # Correct: use set union
    highlight_stats = attunement_stats | weapon_stats | {"Fortitude"}

    all_stats = []
    all_stats += [stat for stat in base_stats if stat in flatpre]
    all_stats += [stat for stat in weapon_stats if stat in flatpre]
    all_stats += [stat for stat in attunement_stats if stat in flatpre]
    others = [k for k in flatpre.keys() if k not in all_stats]
    all_stats += others

    categories = [
        key for key in all_stats
        if flatpre[key] != 0 or ordered_stats[key] != 0 or flatpost[key] != 0
    ]

    splits = []
    idx = 0
    for group in [base_stats, weapon_stats, attunement_stats]:
        n = len([s for s in group if s in categories])
        if n:
            idx += n
            splits.append(idx)
    splits = splits[:-1] 

    gap = 12   
    block_gap = 22  
    y = []
    current_y = 0
    y_pos = {}
    for i, cat in enumerate(categories):
        y.append(current_y)
        y_pos[cat] = current_y
        if i+1 in splits:
            current_y += block_gap
        else:
            current_y += gap

    pre_values = [flatpre[key] for key in categories]
    ord_values = [ordered_stats[key] for key in categories]
    post_values = [flatpost[key] for key in categories]

    plt.style.use('seaborn-v0_8-whitegrid')
    # Use a robust default font to ensure consistent sizing/layout across systems.
    # Keep translations intact; only font family is adjusted for readability.
    plt.rcParams.update({
        'font.family': 'DejaVu Sans',
        'axes.edgecolor': 'gray',
        'axes.linewidth': 0.7
    })

    plt.figure(figsize=(13, current_y*0.1 + 5))
    color_pre = "#DC143C"
    color_ord = "#444444"
    color_post = "#13282B"
    color_reinvest = "#297ec3cc"
    color_reinvest_gray = "#9D9D9D88"
    offset = 2.5
    lw = 2.3

    ys_pre  = [yy - offset for yy in y]
    ys_ord  = y
    ys_post = [yy + offset for yy in y]

    new_categories = [
        f"{cat} ({postval})" for cat, postval in zip(categories, post_values)
    ]

    plt.grid(axis='x', alpha=0.19, linewidth=1.1)

    for yy, val in zip(ys_pre, pre_values):
        if val != 0:
            plt.hlines(yy, 0, val, color=color_pre, linewidth=lw)
            plt.plot(val, yy, 'o', color=color_pre, markersize=9, markeredgewidth=1.5)
            plt.text(val + 1.5, yy, str(val), va='center', ha='left', color=color_pre, fontsize=13, weight='semibold')
    for yy, val in zip(ys_ord, ord_values):
        if val != 0:
            plt.hlines(yy, 0, val, color=color_ord, linewidth=lw)
            plt.plot(val, yy, '^', color=color_ord, markersize=9, markeredgewidth=1.5)
            plt.text(val + 2.5, yy, str(val), va='center', ha='left', color=color_ord, fontsize=13, weight='semibold')
    for yy, val in zip(ys_post, post_values):
        if val != 0:
            plt.hlines(yy, 0, val, color=color_post, linewidth=lw)
            plt.plot(val, yy, 's', color=color_post, markersize=9, markeredgewidth=1.5)
            plt.text(val + 3.4, yy, str(val), va='center', ha='left', color=color_post, fontsize=13, weight='semibold')

    for key, yy, ordv, postv in zip(categories, ys_ord, ord_values, post_values):
        if ordv != postv:
            x0, x1 = sorted([ordv, postv])
            shade = color_reinvest_gray if key in highlight_stats else color_reinvest
            plt.plot([x0, x1], [yy, yy], color=shade, linewidth=11, alpha=0.92, solid_capstyle='projecting')

    for split_idx in splits:
        if split_idx < len(y):
            plt.axhline((y[split_idx-1]+y[split_idx])/2, color="#AAAAAA", lw=2, linestyle="--", alpha=0.8, zorder=0)

    plt.yticks(y, new_categories, fontsize=15, fontweight='medium')
    plt.ylim(min(ys_pre)-gap*1.0, max(ys_post)+gap*1.5)
    plt.xlabel(language_manager.get_text(guild_id, 'stat_value'), fontsize=16, fontweight='semibold', labelpad=8)
    plt.xlim(-8, max(pre_values+ord_values+post_values) + 18)

    handles = [
        Line2D([0], [0], color=color_pre, marker='o', linestyle='-', linewidth=lw, markersize=9, label=language_manager.get_text(guild_id, 'pre_shrine')),
        Line2D([0], [0], color=color_ord, marker='^', linestyle='-', linewidth=lw, markersize=9, label=language_manager.get_text(guild_id, 'order')),
        Line2D([0], [0], color=color_post, marker='s', linestyle='-', linewidth=lw, markersize=9, label=language_manager.get_text(guild_id, 'post_shrine')),
        Line2D([0], [0], color=color_reinvest,  linestyle='-', linewidth=8, alpha=0.92, label=language_manager.get_text(guild_id, 'reinvest_interval')),
        Line2D([0], [0], color=color_reinvest_gray, linestyle='-', linewidth=8, alpha=0.92, label=language_manager.get_text(guild_id, 'reinvest_key_stat')),
    ]
    plt.legend(handles=handles, loc='lower right', frameon=False, fontsize=13, ncol=1)
    plt.tight_layout(pad=2)
    plt.box(False)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', dpi=144)
    buf.seek(0)
    plt.close()
    return buf
