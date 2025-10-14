import discord
import handlers.backbone as daten

def build_outfit_embed(outfit: dict) -> discord.Embed:
    name = outfit.get('name', 'Unknown')
    materials = outfit.get('data', {}).get('mats', 'Unknown')
    rarity = outfit.get('data', {}).get('category', 'Unknown')
    requirements = outfit.get('data', {}).get('requirements', {})

    #functional stats
    durability = outfit.get('data', {}).get('durability', 'Unknown')
    resis = outfit.get('data', {}).get('resistances', {})
    etherRegen = outfit.get('data', {}).get('ether regen', 'Unknown')
    talents = outfit.get('data', {}).get('talents', 'None')

    embed = discord.Embed(
        title = f"{name} - {rarity}",
        color = 0xffffff
    )

    embed.add_field(name="Materials", value='\n'.join([f"{k}" for k in materials]) if materials else "None", inline=False)
    embed.add_field(name="Requirements", value='\n'.join([f"{k}: {v}" for k, v in requirements.items()]) if requirements else "None", inline=False)

    #functional display
    embed.add_field(name="Durability", value=str(durability), inline=True)
    embed.add_field(name="Ether Regen", value=str(etherRegen), inline=True)
    embed.add_field(name="Resistances", value='\n'.join(f"{k}: {v}" for k, v in resis.items()) if resis else "None", inline=False)
    embed.add_field(name="Talents", value='\n'.join([f"{k}" if type(k) != int else f"f{daten.fetch_talent_by_id(k)}" for k in talents]), inline = False) if talents else None

    return embed