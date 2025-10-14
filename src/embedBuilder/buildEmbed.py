import discord
import plugins.dwbapi as dwb
import handlers.backbone as daten

def get_deepwoken_build_embed(build_id: str):
    build = dwb.dwbBuild(build_id)
    stats = build.rawdata
    meta = stats['stats']['meta']
    pre_shrine = stats.get('preShrine', {})
    
    embed_meta = discord.Embed(
        title=f"**{getattr(build, 'name', '')}**\n{getattr(build, 'desc', '')}",
        color=0xffffff,
        url = f"https://deepwoken.co/builder?id={build_id}",
    )

    embed_meta.add_field(name="Race", value=meta.get('Race', 'Unknown'), inline=True)
    embed_meta.add_field(name="Outfit", value=meta.get('Outfit', 'Unknown'), inline=True)
    embed_meta.add_field(name="Origin", value=meta.get('Origin', 'Unknown'), inline=True)
    embed_meta.add_field(name="Oath", value=meta.get('Oath', 'None'), inline=True)
    embed_meta.add_field(name="Murmur", value=meta.get('Murmur', 'None'), inline=True)
    embed_meta.add_field(name="Bell", value=meta.get('Bell', 'None'), inline=True)
    traits = stats.get('traits', {})
    traits_str = '\n'.join([f"{v} {k}" for k, v in traits.items() if v > 0]) or "None"
    embed_meta.add_field(name="Traits", value=traits_str, inline=False)

    weapon_names = ['Heavy Wep.', 'Medium Wep.', 'Light Wep.']
    base_names = ['Strength', 'Fortitude', 'Agility', 'Intelligence', 'Willpower', 'Charisma']
    attunement_names = ['Flamecharm', 'Frostdraw', 'Thundercall', 'Galebreathe', 'Shadowcast', 'Ironsing', 'Bloodrend']

    display_wep = ['HVY', 'MED', 'LHT']
    display_base = ['STR', 'FOR', 'AGI', 'INT', 'WIL', 'CHA']
    display_att = ['FLM', 'ICE', 'LTN', 'WND', 'SDW', 'MTL', 'BLD']

    def stat_blockline(names, curr, pre):
        if names == weapon_names:
            dispnames = display_wep
        elif names == base_names:
            dispnames = display_base
        elif names == attunement_names:
            dispnames = display_att
        else:
            dispnames = names  # fallback if names doesn't match any predefined group

        lines = [
            f"{disp:<5}({pre.get(name, 0):>1}){curr.get(name, 0)}"
            for disp, name in zip(dispnames, names)
        ]
        return '```' + '\n'.join(lines) + '```'


    embed_stats = discord.Embed(
        title="Stats",
        color=0xffffff
    )
    # Correct field construction
    embed_stats.add_field(
        name="Weapon",
        value=stat_blockline(
            weapon_names,
            stats.get('attributes', {}).get('weapon', {}),
            pre_shrine.get('weapon', {})
        ),
        inline=True
    )
    embed_stats.add_field(
        name="Base",
        value=stat_blockline(
            base_names,
            stats.get('attributes', {}).get('base', {}),
            pre_shrine.get('base', {})
        ),
        inline=True
    )
    embed_stats.add_field(
        name="Attunements",
        value=stat_blockline(
            attunement_names,
            stats.get('attributes', {}).get('attunement', {}),
            pre_shrine.get('attunement', {})
        ),
        inline=True
    )

    embeds = [embed_meta, embed_stats]

    return embeds