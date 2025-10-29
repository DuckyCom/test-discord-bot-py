import discord
import handlers.backbone as daten
from utils.language_manager import language_manager


def build_talent_embed(talent: dict, guild_id=None) -> discord.Embed:
    payload = talent.get('data') if isinstance(talent.get('data'), dict) else talent
    data = payload or {}
    stats = data.get('base', {})
    weapons = data.get('weapons', {})
    attunements = data.get('attunements', {})
    exclusive_with = data.get('exclusive with', [])

    cat = daten.searchTableById("categories", data.get("category", language_manager.get_text(guild_id, 'unknown_category')))
    category_name = cat.get("name", language_manager.get_text(guild_id, 'unknown_category')) if isinstance(cat, dict) else str(cat)

    embed = discord.Embed(
        title=f'{talent.get("name", "Unknown Talent")} - {category_name}',
        description=data.get("desc", language_manager.get_text(guild_id, 'no_description')),
        color=discord.Color.blurple()
    )
    embed.add_field(name=language_manager.get_text(guild_id, 'id'), value=str(talent.get("id", "N/A")), inline=True)
    embed.add_field(name=language_manager.get_text(guild_id, 'rarity'), value=data.get("rarity", language_manager.get_text(guild_id, 'unknown')), inline=True)
    embed.add_field(name=language_manager.get_text(guild_id, 'power'), value=str(data.get("power", 0)), inline=True)
    if attunements:
        attune_text = "\n".join(f"{k.capitalize()}: {v}" for k, v in attunements.items())
        embed.add_field(name=language_manager.get_text(guild_id, 'attunement_requirements'), value=attune_text, inline=False)
    if stats:
        stats_text = "\n".join(f"{k.capitalize()}: {v}" for k, v in stats.items())
        embed.add_field(name=language_manager.get_text(guild_id, 'base_requirements'), value=stats_text, inline=False)
    if weapons:
        wep_text = "\n".join(f"{k.capitalize()}: {v}" for k, v in weapons.items())
        embed.add_field(name=language_manager.get_text(guild_id, 'weapon_requirements'), value=wep_text, inline=False)

    if exclusive_with:
        embed.add_field(name=language_manager.get_text(guild_id, 'exclusive_with'), value="\n".join(exclusive_with), inline=False)
    embed.add_field(name=language_manager.get_text(guild_id, 'vaulted'), value=str(data.get("vaulted", False)), inline=True)

    # Invert the 'dontcounttowardstotal' value and present it as 'Count toward total'
    raw_flag = data.get('dontcounttowardstotal', False)
    # Interpret non-bool values as truthy/falsey
    try:
        flag_bool = bool(raw_flag)
    except Exception:
        flag_bool = False
    inverted = not flag_bool
    embed.set_footer(
        text=f"{language_manager.get_text(guild_id, 'count_toward_total')}: {inverted}"
    )
    return embed