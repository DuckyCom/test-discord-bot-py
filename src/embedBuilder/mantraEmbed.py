import discord
import handlers.dataManager as daten
from utils.language_manager import language_manager


def build_mantra_embed(mantra: dict, guild_id=None) -> discord.Embed:
    payload = mantra.get('data') if isinstance(mantra.get('data'), dict) else mantra

    name = payload.get('name', language_manager.get_text(guild_id, 'unknown'))
    description = payload.get('description', language_manager.get_text(guild_id, 'no_description'))
    stars = payload.get('stars', 'N/A')
    category = payload.get('category', 'N/A')
    mantra_type = payload.get('mantra_type', 'N/A')
    attributes = ', '.join(payload.get('attribute', [])) if payload.get('attribute') else language_manager.get_text(guild_id, 'none')
    gif_url = payload.get('gif', '')

    reqs = payload.get('reqs', {})
    none_text = language_manager.get_text(guild_id, 'none')
    attunement_reqs = ', '.join(f"{k}: {v}" for k, v in reqs.get('attunement', {}).items()) if reqs.get('attunement') else none_text
    base_reqs = ', '.join(f"{k}: {v}" for k, v in reqs.get('base', {}).items()) if reqs.get('base') else none_text
    weapon_reqs = ', '.join(f"{k}: {v}" for k, v in reqs.get('weapon', {}).items()) if reqs.get('weapon') else none_text

    embed = discord.Embed(
        title=f"{name} {'★' * int(stars) if str(stars).isdigit() else ''}",
        description=description,
        color=discord.Color.blurple()
    )
    embed.add_field(name=language_manager.get_text(guild_id, 'category'), value=category, inline=True)
    embed.add_field(name=language_manager.get_text(guild_id, 'type'), value=mantra_type, inline=True)
    embed.add_field(name=language_manager.get_text(guild_id, 'attribute'), value=attributes, inline=True)
    if attunement_reqs != none_text:
        embed.add_field(name=language_manager.get_text(guild_id, 'attunement_requirement'), value=attunement_reqs, inline=False)
    if base_reqs != none_text:
        embed.add_field(name=language_manager.get_text(guild_id, 'base_requirement'), value=base_reqs, inline=False)
    if weapon_reqs != none_text:
        embed.add_field(name=language_manager.get_text(guild_id, 'weapon_requirement'), value=weapon_reqs, inline=False)

    if gif_url:
        embed.set_image(url=gif_url)
    return embed