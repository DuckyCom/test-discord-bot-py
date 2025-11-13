import os
import importlib.util
import discord
from difflib import get_close_matches
from utils.language_manager import language_manager

PREFIX = '.'

class commandManager:
    def __init__(self, client):
        self.Client = client
        self.PREFIX = PREFIX
        self.clopen_manager = None  # Will be set by bot.py
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.COMMANDPATH = os.path.join(current_dir, '..', 'commands')

    def loadCommands(self):
        """Load all command modules"""
        commands = {}
        for filename in os.listdir(self.COMMANDPATH):
            if filename.endswith('.py'):
                command_name = filename[:-3]
                command_file = os.path.join(self.COMMANDPATH, filename)
                
                spec = importlib.util.spec_from_file_location(command_name, command_file)
                command_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(command_module)
                
                commands[command_name] = command_module
        return commands

    async def processCommand(self, message):
        after_prefix = message.content[len(self.PREFIX):]
        if after_prefix and after_prefix[0] == ' ':
            guild_id = message.guild.id if message.guild else None
            lang = language_manager.get_language(guild_id)
            
            embed = discord.Embed(
                title="Invalid Command Format" if lang == 'en' else "Formato de Comando Inválido",
                description=(
                    f"Commands must not have a space after '{self.PREFIX}'"
                    if lang == 'en' else
                    f"Los comandos no deben tener un espacio después de '{self.PREFIX}'"
                ),
                color=0xED4245
            )
            return (embed, {'auto_delete': True, 'timeout': 10, 'delete_user_message': True})
        
        # Parse command and arguments
        content = message.content[len(self.PREFIX):]
        space_index = content.find(' ')
        
        if space_index != -1:
            command_name = content[:space_index].lower()
            command_body = content[space_index+1:].strip()
        else:
            command_name = content.lower()
            command_body = ""
        
        commands = self.loadCommands()
        
        # Check if command exists
        if command_name not in commands:
            close_matches = get_close_matches(command_name, commands.keys(), n=3, cutoff=0.6)
            
            guild_id = message.guild.id if message.guild else None
            lang = language_manager.get_language(guild_id)
            
            embed = discord.Embed(
                title="Command Not Found" if lang == 'en' else "Comando No Encontrado",
                description=(
                    f"Command `{self.PREFIX}{command_name}` does not exist."
                    if lang == 'en' else
                    f"El comando `{self.PREFIX}{command_name}` no existe."
                ),
                color=0xED4245
            )
            
            if close_matches:
                suggestion_text = "Did you mean:" if lang == 'en' else "¿Quisiste decir:"
                suggestions = '\n'.join([f"`{self.PREFIX}{match}`" for match in close_matches])
                embed.add_field(name=suggestion_text, value=suggestions, inline=False)
            
            help_text = f"Use `{self.PREFIX}help` for available commands"
            embed.set_footer(text=help_text)
            
            return (embed, {'auto_delete': True, 'timeout': 10, 'delete_user_message': True})
        
        # Execute command
        command_module = commands[command_name]
        
        try:
            result = command_module.execute(command_body, message)
            
            # Handle async commands
            if isinstance(result, tuple) and len(result) == 2 and result[0] == "ASYNC":
                # Execute the coroutine and await it
                # The command is responsible for sending its own messages
                await result[1]
                return None  # Signal to handler: don't send another message
            
            # Return sync command result
            return result
            
        except Exception as e:
            guild_id = message.guild.id if message.guild else None
            lang = language_manager.get_language(guild_id)
            
            error_embed = discord.Embed(
                title="Command Error" if lang == 'en' else "Error de Comando",
                description=(
                    f"An error occurred while executing `{self.PREFIX}{command_name}`"
                    if lang == 'en' else
                    f"Ocurrió un error al ejecutar `{self.PREFIX}{command_name}`"
                ),
                color=0xED4245
            )
            error_embed.add_field(
                name="Error Details" if lang == 'en' else "Detalles del Error",
                value=f"```{str(e)[:500]}```",
                inline=False
            )
            
            return (error_embed, {'auto_delete': True, 'timeout': 15})
