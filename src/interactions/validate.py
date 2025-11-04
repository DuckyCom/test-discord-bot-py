import discord
from plugins.legality import BuildLegalityChecker

def execute(build, guild_id=None):
    checker = BuildLegalityChecker()
    result = checker.check_build(build)
    embed = checker.report_embed(result)
    return embed
