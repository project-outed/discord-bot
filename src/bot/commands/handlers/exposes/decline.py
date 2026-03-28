import os
import discord
from discord.ext import commands
from discord import app_commands

class Decline(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(int(os.getenv("MAIN_GUILD")))
    @app_commands.command(name="decline", description="Decline a user's request")
    async def decline(self, interaction: discord.Interaction, user: discord.Member):
        pass