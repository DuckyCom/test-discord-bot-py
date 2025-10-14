import discord
import handlers.backbone as daten

def build_equipment_embed(equipment: dict) -> discord.Embed:
    name = equipment.get('data', {}).get('name', 'Unknown')
    equipmenttype = equipment.get('data', {}).get('type', 'Unknown')
    equipmentstats = equipment.get('data', {}).get('stats', {})
    equipmenttalents = equipment.get('data', {}).get('talents', [])
    pips = equipment.get('data', {}).get('rarities', {})

    embed = discord.Embed(
        title = f"{name} ({equipmenttype})",
        color = 0xffffff
    )

    embed.add_field(name="Stats", value='\n'.join([f"{k}: {v}" for k, v in equipmentstats.items()]) if equipmentstats else "None", inline=False)
    embed.add_field(name="Talents", value='\n'.join([f"{k}" if type(k) != int else f"f{daten.fetch_talent_by_id(k)}" for k in equipmenttalents]), inline = False) if equipmenttalents else None
    embed.add_field(name="Pips", value=', '.join([f"{k}: {v} pips" for k, v in pips.items()]) if pips else "None", inline=False)

    return embed