import os
import json
import aiohttp
import discord
from discord.ext import commands
from discord import app_commands
from src.utils.console import Console
from typing import List

from src.bot.ui.messages.expose.create_report import CreateReportView

class CreateReport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_url = os.getenv("API_URI")
        self.config = self.__load_config()

    def __load_config(self):
        configPath = os.path.join("data", "exposes", "config.json")
        with open(configPath, "r") as f:
            return json.load(f)

    async def game_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        try:
            games = self.config.get('games', [])
        except Exception as e:
            Console.error(f"Failed to load expose config: {e}", module="EXPOSE")
            games = []
            
        return [
            app_commands.Choice(name=game, value=game)
            for game in games 
            if current.lower() in game.lower()
        ][:25]

    async def reason_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        try:
            reasons = self.config.get('cheats', [])
        except Exception as e:
            Console.error(f"Failed to load expose config: {e}", module="EXPOSE")
            reasons = []
            
        return [
            app_commands.Choice(name=reason, value=reason)
            for reason in reasons 
            if current.lower() in reason.lower()
        ][:25]

    @app_commands.guilds(int(os.getenv("MAIN_GUILD")))
    @app_commands.command(name="report", description="Create a report for a user")
    @app_commands.describe(
        user="The user you are reporting", reason="The reason for the report", 
        game="The game where the incident occurred", evidence="Evidence for the report (image/video)"
    )
    @app_commands.autocomplete(game=game_autocomplete, reason=reason_autocomplete)
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

            async with self.bot.session.post(f"{self.base_url}/api/reports", data=data, headers=headers) as resp:
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