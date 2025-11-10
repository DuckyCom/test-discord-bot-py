import os
import importlib.util
import discord
from difflib import get_close_matches
from utils.language_manager import language_manager

class commandManager:
    def __init__(self, client):
        self.Client = client

        self.PREFIX = '.'
        # Get absolute path relative to this file's location
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.COMMANDPATH = os.path.join(current_dir, '..', 'commands')

    def loadCommands(self):
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

    def processCommand(self, message):
        # Check if there's a space immediately after the prefix (e.g., ". e" or ". weapon")
        after_prefix = message.content[len(self.PREFIX):]
        if after_prefix.startswith(' '):
            # Ignore commands with space after prefix to avoid false "Command not found"
            return None
        
        command_args = after_prefix.strip().split()
        command_body = after_prefix.strip()
        command_parts = command_body.split()
        if len(command_parts) == 0 or command_parts[0] == '':
            return None
        command_name = command_parts[0]
        command_body = command_body[len(command_name):].strip()
        
        # Filter meaningless input (only dots, spaces, or very short nonsense)
        # Examples: "...", "..", ".. .. a", ". . ."
        cleaned = command_name.replace('.', '').replace(' ', '').strip()
        if len(cleaned) == 0 or (len(cleaned) == 1 and not cleaned.isalnum()):
            return None
        
        print(command_body)

        command_file = os.path.join(self.COMMANDPATH, f"{command_name}.py")
        
        # Get guild (server) ID for language support
        guild_id = message.guild.id if message.guild else None

        # If no args after the command name for item lookup, show usage instead of attempting a lookup
        if command_name in ('talent', 'mantra', 'outfit', 'weapon', 'equipment', 'kit') and len(command_body.strip()) == 0:
            usage_map = {
                'talent': '.talent {talent name}',
                'mantra': '.mantra {mantra name}',
                'outfit': '.outfit {outfit name}',
                'weapon': '.weapon {weapon name}',
                'equipment': '.equipment {equipment name}',
                'kit': '.kit {kit_share_id}'
            }
            example = usage_map.get(command_name, f'.{command_name} {{name}}')
            title = language_manager.get_text(guild_id, 'usage')
            description = language_manager.get_text(guild_id, 'usage_description').format(example=example)
            embed = discord.Embed(title=f"{title}", description=description, color=0xffcc00)
            meta = {'auto_delete': True, 'delete_user_message': True, 'timeout': 10}
            return (embed, meta)
        if os.path.isfile(command_file):
            spec = importlib.util.spec_from_file_location(command_name, command_file)
            command_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(command_module)

            if hasattr(command_module, 'execute'):
                # Pass message object for commands that need guild_id (like help)
                # Pass command_body for commands that need arguments (like weapon, talent, etc.)
                if command_name == 'help':
                    return command_module.execute(message)
                else:
                    # For lookup commands, pass both command_body and guild_id
                    if command_name in ('talent', 'mantra', 'outfit', 'weapon', 'equipment', 'kit'):
                        return command_module.execute(command_body, guild_id)
                    else:
                        return command_module.execute(command_body)
            else:
                print(f"Command {command_name} does not have an execute function.")
        else:
            # provide suggestions for mistyped commands (pluralization and fuzzy matches)
            available = [f[:-3] for f in os.listdir(self.COMMANDPATH) if f.endswith('.py')]
            # try singular/plural correction
            candidates = set(available)
            # naive plural->singular by stripping trailing 's' if present
            if command_name.endswith('s'):
                candidates.add(command_name[:-1])
            # fuzzy match
            close = get_close_matches(command_name, list(candidates), n=3, cutoff=0.6)
            
            title = language_manager.get_text(guild_id, 'command_not_found')
            if close:
                suggestions = ', '.join(close)
                description = language_manager.get_text(guild_id, 'perhaps_you_meant').format(suggestions=suggestions)
            else:
                description = language_manager.get_text(guild_id, 'unknown_command').format(command=command_name)

            embed = discord.Embed(title={title}, description=description, color=0xffcc00)
            meta = {'auto_delete': True, 'delete_user_message': True, 'timeout': 10}
            return (embed, meta)