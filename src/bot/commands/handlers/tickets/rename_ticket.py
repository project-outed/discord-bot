import os
import discord
from discord.ext import commands
from discord import app_commands

class Rename(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(int(os.getenv("MAIN_GUILD")))
    @app_commands.command(name="rename", description="Rename the ticket channel")
    async def rename(self, interaction: discord.Interaction, new_name: str):
        pass