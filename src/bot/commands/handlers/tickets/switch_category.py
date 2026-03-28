import os
import discord
from discord.ext import commands
from discord import app_commands
from typing import List

class Category(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def category_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        categories = await self.bot.db.settings.get_categories()
        return [
            app_commands.Choice(name=cat['name'], value=cat['value'])
            for cat in categories if current.lower() in cat['name'].lower()
        ]

    @app_commands.guilds(int(os.getenv("MAIN_GUILD")))
    @app_commands.command(name="category", description="Switch the ticket category")
    @app_commands.autocomplete(new_category=category_autocomplete)
    async def category(self, interaction: discord.Interaction, new_category: str):
        pass