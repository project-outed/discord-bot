import os
import json
import aiohttp
import discord
from discord.ext import commands
from discord import app_commands

from src.bot.ui.messages.verify import VerificationView

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.__load_config()

    def __load_config(self):
        configPath = os.path.join("data", "config.json")
        with open(configPath, "r") as f:
            data = json.load(f)
            return data

    @app_commands.guilds(int(os.getenv("MAIN_GUILD")))
    @app_commands.command(name="verification", description="Send the verification panel")
    async def verification(self, interaction: discord.Interaction):
        channel_id = int(self.config["verification"]["channel_id"])
        channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
        
        if not channel:
            await interaction.response.send_message("Error: Could not find the configured panel channel.", ephemeral=True)
            return

        await channel.send(
            view=VerificationView(),
            files=[
                discord.File("images/banners/banner.webp", filename="banner_verification.webp")
            ]
        )
        await interaction.response.send_message(f"Panel sent successfully to {channel.mention}", ephemeral=True)
