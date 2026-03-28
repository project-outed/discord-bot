import os
import discord
from discord.ext import commands
from discord import app_commands

class Remove(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(int(os.getenv("MAIN_GUILD")))
    @app_commands.command(name="remove", description="Remove a user from the ticket")
    async def remove(self, interaction: discord.Interaction, user: discord.Member):
        pass