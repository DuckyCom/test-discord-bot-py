import discord
from plugins.embedBuilder.clopenEmbed import ClopenEmbedBuilder


def execute(command_body, message):
    clopen_manager = message.guild._state._get_client().clopen_manager

    if not message.guild:
        return (discord.Embed(
            description="This command can only be used in servers.",
            color=0xED4245
        ), None)

    if not message.author.guild_permissions.administrator:
        return (discord.Embed(
            description="Only administrators can configure the clopen system.",
            color=0xED4245
        ), None)

    parts = command_body.strip().split()

    if len(parts) == 0 or parts[0].lower() == "help":
        return (ClopenEmbedBuilder.help_embed(), None)

    subcommand = parts[0].lower()

    if subcommand == "setup":
        result = _setup(parts[1:], message, clopen_manager)
    elif subcommand == "register":
        result = _register(parts[1:], message, clopen_manager)
    elif subcommand == "unregister":
        result = _unregister(parts[1:], message, clopen_manager)
    elif subcommand == "timeout":
        result = _set_timeout(parts[1:], message, clopen_manager)
    elif subcommand == "closetime":
        result = _set_closetime(parts[1:], message, clopen_manager)
    elif subcommand == "userlimit":
        result = _set_userlimit(parts[1:], message, clopen_manager)
    elif subcommand == "minavailable":
        result = _set_min_available(parts[1:], message, clopen_manager)
    elif subcommand == "maxavailable":
        result = _set_max_available(parts[1:], message, clopen_manager)
    elif subcommand == "status":
        result = (_status(message, clopen_manager), None)
    elif subcommand == "list":
        result = (_list_channels(message, clopen_manager), None)
    else:
        result = (discord.Embed(
            description=f"Unknown subcommand: `{subcommand}`\nUse `.clopen help` for usage.",
            color=0xED4245
        ), None)

    return result


def _setup(args, message, clopen_manager):
    if len(args) < 2:
        return (discord.Embed(
            description="Usage: `.clopen setup <available_category_id> <used_category_id>`",
            color=0xED4245
        ), None)

    try:
        avail_cat_id = int(args[0])
        used_cat_id = int(args[1])
    except ValueError:
        return (discord.Embed(
            description="Category IDs must be valid numbers",
            color=0xED4245
        ), None)

    avail_cat = message.guild.get_channel(avail_cat_id)
    used_cat = message.guild.get_channel(used_cat_id)

    if not avail_cat or not isinstance(avail_cat, discord.CategoryChannel):
        return (discord.Embed(
            description=f"Available category not found: {avail_cat_id}",
            color=0xED4245
        ), None)

    if not used_cat or not isinstance(used_cat, discord.CategoryChannel):
        return (discord.Embed(
            description=f"Used category not found: {used_cat_id}",
            color=0xED4245
        ), None)

    async def setup_async():
        await clopen_manager.register_guild(
            message.guild.id,
            avail_cat_id,
            used_cat_id
        )
        embed = ClopenEmbedBuilder.setup_success(avail_cat, used_cat)
        await message.channel.send(embed=embed)

    return ("ASYNC", setup_async())


def _register(args, message, clopen_manager):
    if len(args) == 0:
        return (discord.Embed(
            description="Usage: `.clopen register [channel_id...]`",
            color=0xED4245
        ), None)

    config = clopen_manager.get_config(message.guild.id)
    if not config:
        return (discord.Embed(
            description="Please run `.clopen setup` first to configure the system.",
            color=0xED4245
        ), None)

    async def register_async():
        registered = []
        failed = []

        for channel_id_str in args:
            try:
                channel_id = int(channel_id_str)
                channel = message.guild.get_channel(channel_id)
                if not channel:
                    failed.append(f"{channel_id_str} (not found)")
                    continue
                if not isinstance(channel, discord.TextChannel):
                    failed.append(f"{channel_id_str} (not a text channel)")
                    continue

                await clopen_manager.register_channel(channel_id, message.guild.id)
                registered.append(f"<#{channel_id}>")
            except ValueError:
                failed.append(f"{channel_id_str} (invalid ID)")

        embed = ClopenEmbedBuilder.register_result(registered, failed)
        await message.channel.send(embed=embed)

    return ("ASYNC", register_async())


def _unregister(args, message, clopen_manager):
    if len(args) == 0:
        return (discord.Embed(
            description="Usage: `.clopen unregister <channel_id>`",
            color=0xED4245
        ), None)

    try:
        channel_id = int(args[0])
    except ValueError:
        return (discord.Embed(
            description="Channel ID must be a valid number",
            color=0xED4245
        ), None)

    async def unregister_async():
        if channel_id not in clopen_manager.channels:
            embed = ClopenEmbedBuilder.error("Channel Not Found",
                                           f"Channel `{channel_id}` is not registered")
        else:
            await clopen_manager.delete_channel(channel_id)
            embed = ClopenEmbedBuilder.unregister_success(channel_id)

        await message.channel.send(embed=embed)

    return ("ASYNC", unregister_async())


def _set_timeout(args, message, clopen_manager):
    if len(args) == 0:
        return (discord.Embed(
            description="Usage: `.clopen timeout <seconds>`",
            color=0xED4245
        ), None)

    try:
        timeout = int(args[0])
        if timeout < 60:
            return (discord.Embed(
                description="Timeout must be at least 60 seconds",
                color=0xED4245
            ), None)
    except ValueError:
        return (discord.Embed(
            description="Timeout must be a valid number",
            color=0xED4245
        ), None)

    async def set_timeout_async():
        config = clopen_manager.get_config(message.guild.id)
        if not config:
            embed = ClopenEmbedBuilder.error("Not Configured",
                                            "Please run `.clopen setup` first")
        else:
            config.activity_timeout = timeout
            clopen_manager.save_guild(config)
            embed = ClopenEmbedBuilder.timeout_updated(timeout)

        await message.channel.send(embed=embed)

    return ("ASYNC", set_timeout_async())


def _set_closetime(args, message, clopen_manager):
    if len(args) == 0:
        return (discord.Embed(
            description="Usage: `.clopen closetime <seconds>`",
            color=0xED4245
        ), None)

    try:
        timeout = int(args[0])
        if timeout < 5:
            return (discord.Embed(
                description="Close time must be at least 5 seconds",
                color=0xED4245
            ), None)
    except ValueError:
        return (discord.Embed(
            description="Close time must be a valid number",
            color=0xED4245
        ), None)

    async def set_closetime_async():
        config = clopen_manager.get_config(message.guild.id)
        if not config:
            embed = ClopenEmbedBuilder.error("Not Configured",
                                            "Please run `.clopen setup` first")
        else:
            config.close_timeout = timeout
            clopen_manager.save_guild(config)
            embed = ClopenEmbedBuilder.closetime_updated(timeout)

        await message.channel.send(embed=embed)

    return ("ASYNC", set_closetime_async())


def _set_userlimit(args, message, clopen_manager):
    if len(args) == 0:
        return (discord.Embed(
            description="Usage: `.clopen userlimit <limit>`",
            color=0xED4245
        ), None)

    try:
        limit = int(args[0])
        if limit < 1 or limit > 10:
            return (discord.Embed(
                description="User limit must be between 1 and 10",
                color=0xED4245
            ), None)
    except ValueError:
        return (discord.Embed(
            description="User limit must be a valid number",
            color=0xED4245
        ), None)

    async def set_userlimit_async():
        config = clopen_manager.get_config(message.guild.id)
        if not config:
            embed = ClopenEmbedBuilder.error("Not Configured",
                                            "Please run `.clopen setup` first")
        else:
            config.max_per_user = limit
            clopen_manager.save_guild(config)
            embed = ClopenEmbedBuilder.userlimit_updated(limit)

        await message.channel.send(embed=embed)

    return ("ASYNC", set_userlimit_async())


def _set_min_available(args, message, clopen_manager):
    if len(args) == 0:
        return (discord.Embed(
            description="Usage: `.clopen minavailable <count>`",
            color=0xED4245
        ), None)

    try:
        min_avail = int(args[0])
        if min_avail < 1:
            return (discord.Embed(
                description="Minimum available must be at least 1",
                color=0xED4245
            ), None)
    except ValueError:
        return (discord.Embed(
            description="Minimum available must be a valid number",
            color=0xED4245
        ), None)

    async def set_min_available_async():
        config = clopen_manager.get_config(message.guild.id)
        if not config:
            embed = ClopenEmbedBuilder.error("Not Configured",
                                            "Please run `.clopen setup` first")
        else:
            config.min_available = min_avail
            clopen_manager.save_guild(config)
            embed = ClopenEmbedBuilder.min_available_updated(min_avail)

        await message.channel.send(embed=embed)

    return ("ASYNC", set_min_available_async())


def _set_max_available(args, message, clopen_manager):
    if len(args) == 0:
        return (discord.Embed(
            description="Usage: `.clopen maxavailable <count>`",
            color=0xED4245
        ), None)

    try:
        max_avail = int(args[0])
        if max_avail < 1:
            return (discord.Embed(
                description="Maximum available must be at least 1",
                color=0xED4245
            ), None)
    except ValueError:
        return (discord.Embed(
            description="Maximum available must be a valid number",
            color=0xED4245
        ), None)

    async def set_max_available_async():
        config = clopen_manager.get_config(message.guild.id)
        if not config:
            embed = ClopenEmbedBuilder.error("Not Configured",
                                            "Please run `.clopen setup` first")
        else:
            config.max_available = max_avail
            clopen_manager.save_guild(config)
            embed = ClopenEmbedBuilder.max_available_updated(max_avail)

        await message.channel.send(embed=embed)

    return ("ASYNC", set_max_available_async())


def _status(message, clopen_manager):
    config = clopen_manager.get_config(message.guild.id)
    if not config:
        return ClopenEmbedBuilder.error("Clopen Not Configured",
                                       "Run `.clopen setup` to initialize the system")

    guild_channels = [c for c in clopen_manager.channels.values()
                     if c.guild_id == message.guild.id]

    return ClopenEmbedBuilder.status_embed(config, guild_channels, message.guild)


def _list_channels(message, clopen_manager):
    config = clopen_manager.get_config(message.guild.id)
    if not config:
        return ClopenEmbedBuilder.error("Clopen Not Configured",
                                       "Run `.clopen setup` to initialize the system")

    guild_channels = [c for c in clopen_manager.channels.values()
                     if c.guild_id == message.guild.id]

    if not guild_channels:
        return discord.Embed(
            title="No Registered Channels",
            description="Use `.clopen register <channel_id>` to add channels",
            color=0xFFCC00
        )

    return ClopenEmbedBuilder.list_embed(guild_channels, message.guild)