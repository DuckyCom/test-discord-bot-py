import discord


class ClopenEmbedBuilder:
    COLOR_SUCCESS = 0x43B581
    COLOR_ERROR = 0xED4245
    COLOR_WARNING = 0xFFCC00
    COLOR_INFO = 0x5865F2
    COLOR_PRIMARY = 0x7CB342
    
    @staticmethod
    def help_embed():
        embed = discord.Embed(
            title="Clopen System Configuration",
            description="Automatic help channel rotation system",
            color=ClopenEmbedBuilder.COLOR_PRIMARY
        )
        
        embed.add_field(
            name="Setup Commands",
            value=(
                "`.clopen setup <available_cat_id> <used_cat_id>` - Initialize clopen system\n"
                "`.clopen register <channel_id> [channel_id...]` - Add channels to pool\n"
                "`.clopen unregister <channel_id>` - Remove channel from pool"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Configuration Commands",
            value=(
                "`.clopen timeout <seconds>` - Set activity timeout (default: 300s)\n"
                "`.clopen closetime <seconds>` - Set close delay (default: 20s)\n"
                "`.clopen userlimit <number>` - Max channels per user (default: 1)\n"
                "`.clopen minavailable <number>` - Min available channels (default: 2)\n"
                "`.clopen maxavailable <number>` - Max available channels (default: 5)"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Information Commands",
            value=(
                "`.clopen status` - View current configuration and statistics\n"
                "`.clopen list` - List all registered channels\n"
                "`.clopen help` - Show this help message"
            ),
            inline=False
        )
        
        embed.add_field(
            name="User Commands",
            value="`.close [reason]` - Close your active channel",
            inline=False
        )
        
        return embed
    
    @staticmethod
    def setup_success(available_cat, used_cat):
        embed = discord.Embed(
            title="Clopen System Configured",
            description="Help channel rotation is now active",
            color=ClopenEmbedBuilder.COLOR_SUCCESS
        )
        
        embed.add_field(
            name="Available Category",
            value=f"{available_cat.name} (`{available_cat.id}`)",
            inline=True
        )
        
        embed.add_field(
            name="Used Category",
            value=f"{used_cat.name} (`{used_cat.id}`)",
            inline=True
        )
        
        embed.add_field(
            name="Next Steps",
            value=(
                "1. Use `.clopen register <channel_id>` to add help channels\n"
                "2. Adjust timeouts with `.clopen timeout <seconds>`\n"
                "3. Check status with `.clopen status`"
            ),
            inline=False
        )
        
        return embed
    
    @staticmethod
    def register_result(registered, failed):

        embed = discord.Embed(
            title="Channel Registration Results",
            color=ClopenEmbedBuilder.COLOR_SUCCESS if len(failed) == 0 else ClopenEmbedBuilder.COLOR_WARNING
        )
        
        if registered:
            embed.add_field(
                name="Registered",
                value="\n".join(registered),
                inline=False
            )
        
        if failed:
            embed.add_field(
                name="Failed",
                value="\n".join(failed),
                inline=False
            )
        
        if registered:
            embed.set_footer(text="Channels will now participate in automatic rotation")
        
        return embed
    
    @staticmethod
    def unregister_success(channel_id):
        return discord.Embed(
            title="Channel Unregistered",
            description=f"<#{channel_id}> has been removed from the clopen system",
            color=ClopenEmbedBuilder.COLOR_SUCCESS
        )
    
    @staticmethod
    def timeout_updated(timeout):
        minutes = timeout // 60
        return discord.Embed(
            title="Activity Timeout Updated",
            description=f"Channels will prompt for closure after **{timeout}s** ({minutes} min) of inactivity",
            color=ClopenEmbedBuilder.COLOR_SUCCESS
        )
    
    @staticmethod
    def closetime_updated(timeout):
        return discord.Embed(
            title="Close Timeout Updated",
            description=f"Channels will return to available after **{timeout}s** of being closed",
            color=ClopenEmbedBuilder.COLOR_SUCCESS
        )
    
    @staticmethod
    def userlimit_updated(limit):
        return discord.Embed(
            title="User Limit Updated",
            description=f"Users can now claim up to **{limit}** channels simultaneously",
            color=ClopenEmbedBuilder.COLOR_SUCCESS
        )
    
    @staticmethod
    def min_available_updated(min_avail):
        return discord.Embed(
            title="Minimum Available Channels Updated",
            description=f"System will maintain at least **{min_avail}** available channels",
            color=ClopenEmbedBuilder.COLOR_SUCCESS
        )
    
    @staticmethod
    def max_available_updated(max_avail):
        return discord.Embed(
            title="Maximum Available Channels Updated",
            description=f"System will maintain at most **{max_avail}** available channels",
            color=ClopenEmbedBuilder.COLOR_SUCCESS
        )
    
    @staticmethod
    def status_embed(config, guild_channels, guild):
        available = sum(1 for c in guild_channels if c.state == "available")
        claimed = sum(1 for c in guild_channels if c.state == "claimed")
        used = sum(1 for c in guild_channels if c.state == "used")
        closing = sum(1 for c in guild_channels if c.state == "closing")
        
        embed = discord.Embed(
            title="Clopen System Status",
            color=ClopenEmbedBuilder.COLOR_INFO
        )
        
        available_cat = guild.get_channel(config.available_category_id)
        used_cat = guild.get_channel(config.used_category_id)
        
        embed.add_field(
            name="Configuration",
            value=(
                f"**Available Category:** {available_cat.name if available_cat else 'Not found'}\n"
                f"**Used Category:** {used_cat.name if used_cat else 'Not found'}\n"
                f"**Activity Timeout:** {config.activity_timeout}s ({config.activity_timeout // 60} min)\n"
                f"**Close Timeout:** {config.close_timeout}s\n"
                f"**Max Per User:** {config.max_per_user} channels\n"
                f"**Min Available:** {config.min_available} channels\n"
                f"**Max Available:** {config.max_available} channels"
            ),
            inline=False
        )
        
        embed.add_field(
            name="Channel Statistics",
            value=(
                f"**Available:** {available}\n"
                f"**Claimed:** {claimed}\n"
                f"**In Use:** {used}\n"
                f"**Closing:** {closing}\n"
                f"**Total:** {len(guild_channels)}"
            ),
            inline=False
        )
        
        if used > 0 or claimed > 0:
            active_channels = [c for c in guild_channels if c.state in ["claimed", "used"]]
            active_list = []
            
            for chan in active_channels[:5]:
                channel = guild.get_channel(chan.channel_id)
                owner = f"<@{chan.owner_id}>" if chan.owner_id else "Unknown"
                state_emoji = "[C]" if chan.state == "claimed" else "[U]"
                active_list.append(f"{state_emoji} <#{chan.channel_id}> - {owner}")
            
            if len(active_channels) > 5:
                active_list.append(f"... and {len(active_channels) - 5} more")
            
            embed.add_field(
                name="Active Channels",
                value="\n".join(active_list) if active_list else "None",
                inline=False
            )
        
        embed.set_footer(text="Use .clopen help for configuration commands")
        
        return embed
    
    @staticmethod
    def list_embed(guild_channels, guild):
        embed = discord.Embed(
            title="Registered Channels",
            description=f"Total: {len(guild_channels)} channels",
            color=ClopenEmbedBuilder.COLOR_INFO
        )
        
        by_state = {
            "available": [],
            "claimed": [],
            "used": [],
            "closing": []
        }
        
        for chan in guild_channels:
            channel = guild.get_channel(chan.channel_id)
            if channel:
                if chan.owner_id:
                    by_state[chan.state].append(f"<#{chan.channel_id}> - <@{chan.owner_id}>")
                else:
                    by_state[chan.state].append(f"<#{chan.channel_id}>")
        
        if by_state["available"]:
            embed.add_field(
                name=f"Available ({len(by_state['available'])})",
                value="\n".join(by_state["available"][:10]) + 
                      (f"\n... and {len(by_state['available']) - 10} more" if len(by_state['available']) > 10 else ""),
                inline=False
            )
        
        if by_state["claimed"]:
            embed.add_field(
                name=f"Claimed ({len(by_state['claimed'])})",
                value="\n".join(by_state["claimed"][:10]) + 
                      (f"\n... and {len(by_state['claimed']) - 10} more" if len(by_state['claimed']) > 10 else ""),
                inline=False
            )
        
        if by_state["used"]:
            embed.add_field(
                name=f"In Use ({len(by_state['used'])})",
                value="\n".join(by_state["used"][:10]) + 
                      (f"\n... and {len(by_state['used']) - 10} more" if len(by_state['used']) > 10 else ""),
                inline=False
            )
        
        if by_state["closing"]:
            embed.add_field(
                name=f"Closing ({len(by_state['closing'])})",
                value="\n".join(by_state["closing"][:10]) + 
                      (f"\n... and {len(by_state['closing']) - 10} more" if len(by_state['closing']) > 10 else ""),
                inline=False
            )
        
        return embed
    
    @staticmethod
    def error(title, description):
        return discord.Embed(
            title=title,
            description=description,
            color=ClopenEmbedBuilder.COLOR_ERROR
        )
    
    @staticmethod
    def channel_claimed(user):
        return discord.Embed(
            title="Channel Claimed",
            description=f"This channel has been claimed by {user.mention}",
            color=ClopenEmbedBuilder.COLOR_SUCCESS
        )
    
    @staticmethod
    def channel_closed(reason):
        return discord.Embed(
            title="Channel Closed",
            description=f"{reason}\nThis channel will be available for others soon.",
            color=0x000000
        )
    
    @staticmethod
    def available_channel_prompt():
        return discord.Embed(
            title="Available Help Channel!",
            description=(
                "Send your question here to claim this channel.\n"
                "**Remember:**\n"
                "• Ask your question clearly and concisely\n"
                "• Use `.close` when you're done\n"
            ),
            color=ClopenEmbedBuilder.COLOR_PRIMARY
        )
    
    @staticmethod
    def inactivity_prompt(owner_id):
        return discord.Embed(
            description=f"<@{owner_id}> Is your question resolved?\nReact with ✅ to close or ❌ to keep open.",
            color=ClopenEmbedBuilder.COLOR_WARNING
        )
    
    @staticmethod
    def max_channels_reached(max_per_user):
        return discord.Embed(
            description=f"You already have {max_per_user} active help channels. Please close one first.",
            color=ClopenEmbedBuilder.COLOR_ERROR
        )