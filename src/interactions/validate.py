from plugins.legalityChecker import BuildLegalityChecker

def execute(build, _guild_id=None):
    checker = BuildLegalityChecker()
    result = checker.check_build(build)
    embed = checker.report_embed(result)
    return embed
