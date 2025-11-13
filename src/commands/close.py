import discord

def execute(command_body, message):
    clopen_manager = message.guild._state._get_client().clopen_manager
    meta = { 'auto_delete': True, 'delete_user_message': True, 'timeout': 10 }

    if not message.guild:
        return (discord.Embed(
            description="This command can only be used in servers.",
            color=0xED4245
        ), meta)

    # Check if this channel is in the system
    if message.channel.id not in clopen_manager.channels:
        return (discord.Embed(
            description="This is not a clopen-managed channel.",
            color=0xED4245
        ), meta)
    
    chan_data = clopen_manager.channels[message.channel.id]
    
    # Check if channel is in use
    if chan_data.state != "used":
        return (discord.Embed(
            description="This channel is not currently in use.",
            color=0xED4245
        ), meta)
    
    # Check if user owns the channel or is admin
    is_owner = chan_data.owner_id == message.author.id
    is_admin = message.author.guild_permissions.administrator
    
    if not is_owner and not is_admin:
        return (discord.Embed(
            description=f"Only <@{chan_data.owner_id}> or administrators can close this channel.",
            color=0xED4245
        ), meta)
    
    # Parse reason
    reason = command_body.strip() if command_body else "Channel closed"
    close_reason = f"{reason} (by <@{message.author.id}>)"
    
    # Return async operation - this will handle its own message sending
    async def close_async():
        await clopen_manager.close_channel(message.channel, close_reason)
    
    return ("ASYNC", close_async())