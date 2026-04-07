import os
import aiohttp
import discord
from discord.ext import commands
from discord import app_commands
from src.utils.console import Console

from src.bot.ui.messages.expose.create_report import CreateReportView

class CreateReport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_url = os.getenv("API_URI")

    @app_commands.command(name="report", description="Create a report for a user")
    @app_commands.describe(
        user="The user you are reporting", reason="The reason for the report", 
        game="The game where the incident occurred", evidence="Evidence for the report (image/video)"
    )
    async def report(self, interaction: discord.Interaction, user: discord.User, reason: str, game: str, evidence: discord.Attachment):
        await interaction.response.defer(ephemeral=True)

        try:
            data = aiohttp.FormData()
            data.add_field('target_username', str(user.name))
            data.add_field('target_user_id', str(user.id))
            data.add_field('reporter_username', str(interaction.user.name))
            data.add_field('reporter_user_id', str(interaction.user.id))
            data.add_field('game', game)
            data.add_field('reason', reason)
            
            evidence_bytes = await evidence.read()
            data.add_field(
                'evidence', 
                evidence_bytes, 
                filename=evidence.filename, 
                content_type=evidence.content_type
            )

            headers = {
                "x-api-key": os.getenv('API_KEY', '')
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/api/reports", data=data, headers=headers) as resp:
                    if resp.status in [200, 201]:
                        try:
                            result = await resp.json()
                        except:
                            result = {}

                        evidence_file = await evidence.to_file()

                        await interaction.followup.send(
                            view=CreateReportView(data={
                                "id": str(result.get('id', 'N/A')),
                                "target_username": user.name,
                                "target_user_id": str(user.id),
                                "cheat": reason,
                                "game": game,
                                "avatar_url": user.display_avatar.url,
                                "evidence": [evidence_file],
                                "evidence_url": evidence.url
                            }),
                            file=evidence_file,
                            ephemeral=True
                        )
                    else:
                        error_data = await resp.text()
                        await interaction.followup.send(
                            f"**Failed to submit report.**\n"
                            f"Backend returned status: `{resp.status}`\n"
                            f"Response: ```{error_data[:100]}...```", 
                            ephemeral=True
                        )

        except Exception as e:
            await interaction.followup.send(f"**An unexpected error occurred.**\nError: `{str(e)}`", ephemeral=True)
