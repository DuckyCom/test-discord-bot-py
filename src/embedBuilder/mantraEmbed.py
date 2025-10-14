import discord
import handlers.backbone as daten

def build_mantra_embed(mantra: dict) -> discord.Embed:
    name = mantra.get('name', 'Unknown')
    description = mantra.get('description', 'No description available.')
    stars = mantra.get('stars', 'N/A')
    category = mantra.get('category', 'N/A')
    mantra_type = mantra.get('mantra_type', 'N/A')
    attributes = ', '.join(mantra.get('attribute', [])) if mantra.get('attribute') else 'None'
    gif_url = mantra.get('gif', '')

    reqs = mantra.get('reqs', {})
    attunement_reqs = ', '.join(f"{k}: {v}" for k, v in reqs.get('attunement', {}).items()) if reqs.get('attunement') else 'None'
    base_reqs = ', '.join(f"{k}: {v}" for k, v in reqs.get('base', {}).items()) if reqs.get('base') else 'None'
    weapon_reqs = ', '.join(f"{k}: {v}" for k, v in reqs.get('weapon', {}).items()) if reqs.get('weapon') else 'None'

    embed = discord.Embed(
        title=f"{name} {'★' * int(stars) if str(stars).isdigit() else ''}",
        description=description,
        color=0xffffff
    )
    embed.add_field(name="Category", value=category, inline=True)
    embed.add_field(name="Type", value=mantra_type, inline=True)
    embed.add_field(name="Attribute", value=attributes, inline=True)
    embed.add_field(name="Attunement Requirement", value=attunement_reqs, inline=False) if attunement_reqs != 'None' else None
    embed.add_field(name="Base Requirement", value=base_reqs, inline=False) if base_reqs != 'None' else None
    embed.add_field(name="Weapon Requirement", value=weapon_reqs, inline=False) if weapon_reqs != 'None' else None

    if gif_url:
        embed.set_image(url=gif_url)
    return embed