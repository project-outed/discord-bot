import os
import discord
from discord.ext import commands
from discord import app_commands

class Add(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(int(os.getenv("MAIN_GUILD")))
    @app_commands.command(name="add", description="Add a user to the ticket")
    async def add(self, interaction: discord.Interaction, user: discord.Member):
        pass