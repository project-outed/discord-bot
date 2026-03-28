import os
import discord
from discord.ext import commands
from discord import app_commands

class Claim(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(int(os.getenv("MAIN_GUILD")))
    @app_commands.command(name="claim", description="Claim the ticket")
    async def claim(self, interaction: discord.Interaction):
        pass