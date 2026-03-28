import os
import discord
from discord.ext import commands
from discord import app_commands

class Unclaim(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(int(os.getenv("MAIN_GUILD")))
    @app_commands.command(name="unclaim", description="Unclaim the ticket")
    async def unclaim(self, interaction: discord.Interaction):
        pass