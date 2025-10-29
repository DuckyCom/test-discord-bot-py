import discord
import handlers.backbone as daten
from utils.language_manager import language_manager


def build_equipment_embed(equipment: dict, guild_id=None) -> discord.Embed:
    # Accept either {'data': {...}} or flat {...}
    payload = equipment.get('data') if isinstance(equipment.get('data'), dict) else equipment

    name = payload.get('name', language_manager.get_text(guild_id, 'unknown'))
    equipmenttype = payload.get('type', language_manager.get_text(guild_id, 'unknown'))
    equipmentstats = payload.get('stats', {})
    equipmenttalents = payload.get('talents', [])
    pips = payload.get('rarities', {})

    embed = discord.Embed(
        title=f"{name} ({equipmenttype})",
        color=discord.Color.blurple()
    )

    none_text = language_manager.get_text(guild_id, 'none')
    embed.add_field(name=language_manager.get_text(guild_id, 'stats'), value='\n'.join([f"{k}: {v}" for k, v in equipmentstats.items()]) if equipmentstats else none_text, inline=False)
    if equipmenttalents:
        talent_lines = []
        for k in equipmenttalents:
            if isinstance(k, int):
                # try to resolve talent by id using backbone helper
                try:
                    tal = daten.searchTableById('talents', k)
                    # tal may be { 'id': ..., 'data': {...} } or flat dict
                    if isinstance(tal, dict):
                        tname = tal.get('data', {}).get('name') or tal.get('name') or f"talent {k}"
                    else:
                        tname = f"talent {k}"
                except Exception:
                    tname = f"talent {k}"
                talent_lines.append(str(tname))
            else:
                talent_lines.append(str(k))
        embed.add_field(name=language_manager.get_text(guild_id, 'talents'), value='\n'.join(talent_lines), inline=False)
    
    pips_text = language_manager.get_text(guild_id, 'pips_text')
    embed.add_field(name=language_manager.get_text(guild_id, 'pips'), value=', '.join([f"{k}: {v} {pips_text}" for k, v in pips.items()]) if pips else none_text, inline=False)

    return embed