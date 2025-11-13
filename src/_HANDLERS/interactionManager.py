import os
import importlib.util
import plugins._DWBAPIWRAPPER as dwb

class interactionManager:
    def __init__(self, client):
        self.Client = client
        # Get absolute path relative to this file's location
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.COMMANDPATH = os.path.join(current_dir, '..', 'interactions')

    def processReply(self, message):
        reply = message.content.strip()
        command_file = os.path.join(self.COMMANDPATH, f"{reply}.py")

        # Get guild_id for language support
        guild_id = message.guild.id if message.guild else None

        referenced = message.reference
        replied_msg = referenced.resolved
        try:
            link = replied_msg.content.split('https://deepwoken.co/builder?id=')[1].split()[0]
            build_id = link.split('&')[0]
            build = dwb.dwbBuild(build_id)
        except Exception as e:
            print(f"Error extracting build id: {e}")
            return (None, None)

        if os.path.isfile(command_file):
            spec = importlib.util.spec_from_file_location(reply, command_file)
            command_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(command_module)

            if hasattr(command_module, 'execute'):
                result = command_module.execute(build, guild_id)
                # If the result is already a tuple, return as is; else wrap in (result, None)
                if isinstance(result, tuple) and len(result) == 2:
                    return result
                elif result is not None:
                    return (result, None)
                else:
                    return (None, None)
            else:
                print(f"Command {reply} does not have an execute function.")
                return (None, None)
        else:
            print(f"Command file {command_file} does not exist.")
            return (None, None)