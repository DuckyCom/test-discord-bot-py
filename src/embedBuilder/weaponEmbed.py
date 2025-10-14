import discord
import handlers.backbone as daten

def build_weapon_embed(weapon: dict) -> discord.Embed:
    name = weapon.get('name', 'Unknown')
    weptype = weapon.get('type', 'Unknown')

    pen = weapon.get('details', {}).get('pen', 0)
    damage = weapon.get('details', {}).get('damage', 0)
    weight = weapon.get('details', {}).get('weight', 0)
    speed = weapon.get('details', {}).get('speed', 0)
    endlag = weapon.get('details', {}).get('endlag', 0)
    scaling = weapon.get('details', {}).get('scaling', {})
    reqs = weapon.get('details', {}).get('reqs', {})

    embed = discord.Embed(
        title = f"{name} - {weptype}",
        color = 0xffffff
    )

    embed.add_field(name="Requirements", value='\n'.join([f"{k}: {v}" for k, v in reqs.items()]) if reqs else "None", inline=True)
    embed.add_field(name="Base Damage", value=str(damage), inline=True)
    embed.add_field(name="Penetration", value=str(pen), inline=True)
    embed.add_field(name="Weight", value=str(weight), inline=True)
    embed.add_field(name="Speed", value=str(speed), inline=True)
    embed.add_field(name="Endlag", value=str(endlag), inline=True)
    embed.add_field(
        name="Scaling",
        value='\n'.join([f"{k}: {v}" for k, v in scaling.items()]) if scaling else "None",
        inline=False
    )

    return embed