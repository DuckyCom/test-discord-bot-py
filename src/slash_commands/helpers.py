"""
Helper utilities for slash commands
"""
import discord
from typing import Optional
from .shared import dispatch_command_result


def extract_build_id(build_link: str) -> str:
    """Extract build ID from a Deepwoken builder URL."""
    if 'deepwoken.co/builder?id=' in build_link:
        return build_link.split('id=')[-1].split('&')[0].strip()
    return build_link.strip()


async def get_build_link_from_reply(interaction: discord.Interaction, build_link: Optional[str]) -> Optional[str]:
    """
    Get build link from either the command parameter or the message being replied to.
    
    In Discord, when you right-click a message and use "Apps > Command",
    the target message is available in interaction.data['resolved']['messages']
    
    Returns None if neither is provided.
    """
    # Check if build_link parameter was provided
    if build_link:
        return build_link
    
    # Check if this command was used on a message (right-click > Apps > Command)
    # or if used via reply context
    if hasattr(interaction, 'data') and isinstance(interaction.data, dict):
        resolved = interaction.data.get('resolved', {})
        messages = resolved.get('messages', {})
        
        # Get the first message (target message)
        if messages:
            for msg_id, msg_data in messages.items():
                content = msg_data.get('content', '')
                if 'https://deepwoken.co/builder?id=' in content:
                    return content
    
    return None


async def send_missing_link_error(interaction: discord.Interaction, command_name: str):
    """Send a helpful error when no build link is found."""
    error_embed = discord.Embed(
        title="Missing Build Link",
        description=(
            f"Please provide a build link using one of these methods:\n\n"
            f"1️⃣ **Right-click a message** with a Deepwoken builder link → Apps → {command_name}\n"
            f"2️⃣ **Provide the link directly**: `/{command_name} build_link: https://deepwoken.co/builder?id=...`"
        ),
        color=0xED4245,
    )
    await dispatch_command_result(interaction, error_embed, ephemeral_override=True)

