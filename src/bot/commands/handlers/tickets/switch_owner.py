import os
import discord
from discord.ext import commands
from discord import app_commands

class Switch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(int(os.getenv("MAIN_GUILD")))
    @app_commands.command(name="switch", description="Switch the ticket owner")
    async def switch(self, interaction: discord.Interaction, new_owner: discord.Member):
        pass