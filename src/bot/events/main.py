import os
import discord
import importlib
from discord.ext import commands
from src.utils.console import Console

bot: discord.Client = None

class EventManager:
    def __init__(self):
        self.bot = bot
        self.events_dir = os.path.join(os.path.dirname(__file__), "handlers")

    async def load(self):
        if not os.path.exists(self.events_dir):
            os.makedirs(self.events_dir)
            Console.warning(f"Handlers directory '{self.events_dir}' created.", "EVENTS")
            return

        event_files = [
            (root, filename)
            for root, _, files in os.walk(self.events_dir)
            for filename in files
            if filename.endswith(".py") and not filename.startswith("__")
        ]

        if not event_files:
            Console.info("No events found in handlers directory.", "EVENTS")
            return

        max_len = max((len(f[1][:-3]) for f in event_files), default=0) + 2

        for root, filename in event_files:
            rel_path = os.path.relpath(root, os.path.dirname(__file__))
            module_name = f"src.bot.events.{rel_path.replace(os.sep, '.')}.{filename[:-3]}"

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
                    Console.info(f"✓ {filename[:-3].ljust(max_len)} | loaded event", "EVENTS")
                else:
                    Console.warning(f"✗ {filename[:-3].ljust(max_len)} | no Cog class found", "EVENTS")

            except Exception as e:
                Console.error(f"✗ {filename[:-3].ljust(max_len)} | failed to load ({e})", "EVENTS")

        Console.success(f"Successfully loaded {len(event_files)} events.", "EVENTS")
