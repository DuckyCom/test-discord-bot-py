import discord
from plugins.kitTools import calculate_kit_stats
from plugins.kitTools import STAT_ORDER, SLOT_ORDER


def format_item_field(item):
    name = item.get('name', 'Unknown')
    slot = item.get('slot', 'Unknown')
    stars = item.get('stars', 0)
    
    stats = calculate_kit_stats(item)
    
    # Build field value
    star_str = f" {'★' * stars}" if stars > 0 else ""
    value = f"**{slot}{star_str}**\n"
    
    # Stats
    stat_parts = [f"{'+' if v > 0 else ''}{v} {s}" for s in STAT_ORDER if (v := stats.get(s))]
    value += ' | '.join(stat_parts) if stat_parts else 'No stats'
    
    # Talents
    talents = item.get('talents', [])
    if talents:
        talent_names = [t.get('name', t) if isinstance(t, dict) else t for t in talents]
        value += f"\n`{', '.join(talent_names)}`"

    return name, value, stats


def build_kit_embed(kit_data, guild_id=None):
    embed = discord.Embed(
        title="Kit Stats",
        color=discord.Color.blurple()
    )
    
    total_stats = {}
    items = sorted(kit_data.get('kit_data', []), 
                  key=lambda x: SLOT_ORDER.index(x['slot']) if x['slot'] in SLOT_ORDER else 999)
    
    # Add items in rows of 3
    for i in range(0, len(items), 4):
        for j in range(4):
            if i + j < len(items):
                name, value, stats = format_item_field(items[i + j])
                for stat, val in stats.items():
                    total_stats[stat] = total_stats.get(stat, 0) + val
                embed.add_field(name=name, value=value, inline=True)
            else:
                embed.add_field(name="\u200b", value="\u200b", inline=True)
    
    embed.add_field(name="Total Stats", value="\u200b", inline=False)
    
    stat_displays = []
    for stat in STAT_ORDER:
        if stat in total_stats and total_stats[stat] != 0:
            stat_displays.append((stat, total_stats[stat]))
    
    # Add first 4 stats
    for i in range(4):
        if i < len(stat_displays):
            stat, val = stat_displays[i]
            embed.add_field(name=stat, value=f"**{val}**", inline=True)
        else:
            embed.add_field(name="\u200b", value="\u200b", inline=True)
    
    # Add remaining stats
    remaining = stat_displays[4:]
    for stat, val in remaining:
        embed.add_field(name=stat, value=f"**{val}**", inline=True)
    
    # Fill remaining slots to complete the row
    for _ in range(4 - len(remaining)):
        embed.add_field(name="\u200b", value="\u200b", inline=True)
    
    return embed
