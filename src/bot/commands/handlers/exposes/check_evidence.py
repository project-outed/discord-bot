import os
import discord
from discord.ext import commands
from discord import app_commands

class CheckEvidence(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(int(os.getenv("MAIN_GUILD")))
    @app_commands.command(name="check_evidence", description="Check a user's evidence")
    async def check_evidence(self, interaction: discord.Interaction, user: discord.Member):
        pass