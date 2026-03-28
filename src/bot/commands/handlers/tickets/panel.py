import os
import discord
from discord.ext import commands
from discord import app_commands
from typing import List, Dict

class TicketPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(int(os.getenv("MAIN_GUILD")))
    @app_commands.command(name="setup_panel", description="Send the main ticket creation panel")
    async def setup_panel(self, interaction: discord.Interaction):
        pass