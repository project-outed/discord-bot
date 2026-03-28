import os
import discord
from discord.ext import commands
from discord import app_commands
from typing import List

class Create(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def category_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        categories = await self.bot.db.settings.get_categories()
        return [
            app_commands.Choice(name=cat['name'], value=cat['value'])
            for cat in categories if current.lower() in cat['name'].lower()
        ]

    @app_commands.guilds(int(os.getenv("MAIN_GUILD")))
    @app_commands.command(name="create", description="Create a new ticket")
    @app_commands.autocomplete(ticket_type=category_autocomplete)
    async def create(self, interaction: discord.Interaction, ticket_type: str):
        pass