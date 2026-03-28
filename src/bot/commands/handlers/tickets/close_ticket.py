import os
import discord
from discord.ext import commands
from discord import app_commands

class Close(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(int(os.getenv("MAIN_GUILD")))
    @app_commands.command(name="close", description="Close the current ticket")
    async def close(self, interaction: discord.Interaction):
        pass