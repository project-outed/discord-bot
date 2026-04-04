import os
import aiohttp
import discord
from discord.ext import commands
from discord import app_commands

from src.bot.ui.messages.expose.lookup import LookupView

class Lookup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.baseURI = os.getenv('API_URI')

    @app_commands.command(name="lookup", description="Lookup a user")
    async def lookup(self, interaction: discord.Interaction, target: discord.User):
        await interaction.response.defer(ephemeral=True)
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.baseURI}/api/users/{target.id}", headers={ 
                "x-api-key": os.getenv('API_KEY', '')
            }) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    user = await self.bot.fetch_user(int(data['providers']['discord']['id']))

                    await interaction.followup.send(
                        view=LookupView(data={
                            "username": user.display_name if user else "Not Found",
                            "platform_id": user.id if user else "Not Found",
                            "avatar": user.display_avatar.url if user else "",
                            "trust_score": data.get("trust_score", 0),
                            "reports": data.get("reports", []),
                        })
                    )
                else:
                    await interaction.followup.send(
                        "User not found or an error occurred while fetching data.",
                    )
                return