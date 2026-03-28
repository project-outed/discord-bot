import os
import aiohttp
import discord
from discord.ext import commands
from discord import app_commands

class Lookup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.baseURI = os.getenv('API_URI')

    @app_commands.command(name="lookup", description="Lookup a user")
    async def lookup(self, interaction: discord.Interaction, target_id: str):
        headers = {"x-api-key": str(os.getenv("API_KEY"))}
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.baseURI}/reports/lookup?target_id={target_id}", headers=headers) as resp:
                print(f"Response: {resp}")
                if resp.status == 200:
                    data = await resp.json()
                    await interaction.response.send_message(f"User found: {data}", ephemeral=True)
                else:
                    await interaction.response.send_message("User not found.", ephemeral=True)