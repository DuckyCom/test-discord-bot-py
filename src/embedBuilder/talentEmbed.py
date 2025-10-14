import discord
import handlers.backbone as daten

def build_talent_embed(talent: dict) -> discord.Embed:
    data = talent.get("data", {})
    stats = data.get('base', {})
    weapons = data.get("weapons", {})
    attunements = data.get("attunements", {})
    exclusive_with = data.get("exclusive with", [])

    cat = daten.searchTableById("categories", data.get("category", "Unknown Category"))
    category_name = cat.get("name", "Unknown Category")

    embed = discord.Embed(
        title=f'{talent.get("name", "Unknown Talent")} - {cat}',
        description=data.get("desc", "No description available."),
        color=0xffffff
    )
    embed.add_field(name="ID", value=str(talent.get("id", "N/A")), inline=True)
    embed.add_field(name="Rarity", value=data.get("rarity", "Unknown"), inline=True)
    embed.add_field(name="Power", value=str(data.get("power", 0)), inline=True)
    if attunements:
        attune_text = "\n".join(f"{k.capitalize()}: {v}" for k, v in attunements.items())
        embed.add_field(name="Attunement Requirements", value=attune_text, inline=False)
    if stats:
        stats_text = "\n".join(f"{k.capitalize()}: {v}" for k, v in stats.items())
        embed.add_field(name="Base Requirements", value=stats_text, inline=False)
    if weapons:
        wep_text = "\n".join(f"{k.capitalize()}: {v}" for k, v in weapons.items())
        embed.add_field(name="Weapon Requirements", value=wep_text, inline=False)

    embed.add_field(name="Exclusive With", value="\n".join(exclusive_with), inline=False) if exclusive_with else None
    embed.add_field(name="Vaulted", value=str(data.get("vaulted", False)), inline=True)

    embed.set_footer(
        text=f"Does not count toward total: {data.get('dontcounttowardstotal', False)}"
    )
    return embed