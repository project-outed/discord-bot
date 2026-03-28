import os
import importlib
import discord
from discord.ext import commands
from src.utils.console import Console

bot: discord.Client = None

class CommandManager(commands.Cog):
    def __init__(self):
        self.bot = bot

    async def load(self):
        base_dir = os.path.join(os.path.dirname(__file__), "handlers")
        
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)
            Console.warning(f"Handlers directory '{base_dir}' created.", "COMMANDS")
            return

        command_files = [
            (root, filename)
            for root, _, files in os.walk(base_dir)
            for filename in files
            if filename.endswith(".py") and not filename.startswith("__")
        ]

        if not command_files:
            Console.info("No commands found in handlers directory.", "COMMANDS")
            return

        max_len = max((len(f[1][:-3]) for f in command_files), default=0) + 2

        for root, filename in command_files:
            rel_path = os.path.relpath(root, os.path.dirname(__file__))
            module_name = f"src.bot.commands.{rel_path.replace(os.sep, '.')}.{filename[:-3]}"

            try:
                module = importlib.import_module(module_name)
                importlib.reload(module)
                
                cog_class = None
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and issubclass(attr, commands.Cog) and attr is not commands.Cog:
                        cog_class = attr
                        break

                if cog_class:
                    cog_instance = cog_class(self.bot)
                    await self.bot.add_cog(cog_instance)

                    app_cmds = cog_instance.get_app_commands()
                    scope_label = "global"

                    try:
                        if app_cmds and hasattr(app_cmds[0], "_guild_ids") and app_cmds[0]._guild_ids:
                            scope_label = f"{len(app_cmds[0]._guild_ids)} guilds"
                    except:
                        pass

                    Console.info(f"✓ {filename[:-3].ljust(max_len)} | scope: {scope_label}", "COMMANDS")
                else:
                    Console.warning(f"✗ {filename[:-3].ljust(max_len)} | no Cog class found", "COMMANDS")

            except Exception as e:
                Console.error(
                    f"✗ {filename[:-3].ljust(max_len)} | failed to load ({e})", "COMMANDS"
                )

        try:
            synced_global = await self.bot.tree.sync()
            total_synced = len(synced_global)
            
            try:
                guild = discord.Object(id=int(os.getenv("MAIN_GUILD")))
                synced_guild = await self.bot.tree.sync(guild=guild)
                total_synced += len(synced_guild)
            except discord.HTTPException:
                pass

            Console.success(f"Successfully synced {total_synced} application commands.", "COMMANDS")
        except Exception as e:
            Console.error(f"✗ Tree sync failed ({e})", "COMMANDS")
