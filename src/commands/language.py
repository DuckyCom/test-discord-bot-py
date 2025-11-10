import discord
from utils.language_manager import language_manager


def execute(args):
    args = args.strip().lower()
    
    # Show current language and help if no args
    if not args:
        embed = discord.Embed(
            title="🌐 Language Settings",
            description="Change the bot's language for this server.\n\n"
                       "**Available languages:**\n"
                       "• `en` - English\n"
                       "• `es` - Español\n\n"
                       "**Usage:** `.language en` or `.language es`\n"
                       "**Uso:** `.language en` o `.language es`",
            color=0x5865F2
        )
        return embed
    
    # Validate language code
    if args not in ['en', 'es']:
        embed = discord.Embed(
            title="Invalid Language",
            description="Please use `en` (English) or `es` (Español).\n"
                       "Por favor usa `en` (English) o `es` (Español).",
            color=0xED4245
        )
        return embed
    
    # Language names for confirmation
    lang_names = {'en': 'English', 'es': 'Español'}
    
    embed = discord.Embed(
        title="Language Updated" if args == 'en' else "Idioma Actualizado",
        description=f"Bot language for this server set to **{lang_names[args]}**.\n"
                   f"Idioma del bot para este servidor configurado a **{lang_names[args]}**.",
        color=0x57F287
    )
    
    return embed


def set_language_for_guild(guild_id, language):
    """Helper function to set language (called from message handler with permissions check)."""
    return language_manager.set_language(guild_id, language)
