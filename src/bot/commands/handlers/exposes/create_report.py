import os
import aiohttp
import discord
from discord.ext import commands
from discord import app_commands
from src.utils.console import Console

class CreateReport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Using the base URI from env if available, or the one provided by user
        self.base_url = "https://backend.outed.dev"

    @app_commands.guilds(int(os.getenv("MAIN_GUILD")))
    @app_commands.command(name="report", description="Create a report for a user")
    @app_commands.describe(
        user="The user you are reporting",
        reason="The reason for the report",
        game="The game where the incident occurred",
        evidence="Evidence for the report (image/video)"
    )
    async def report(
        self, 
        interaction: discord.Interaction, 
        user: discord.User, 
        reason: str, 
        game: str, 
        evidence: discord.Attachment
    ):
        """Creates a new report for a suspected cheater."""
        await interaction.response.defer(ephemeral=True)

        try:
            # Prepare multipart/form-data
            data = aiohttp.FormData()
            data.add_field('target_user_name', str(user.name))
            data.add_field('target_userid', str(user.id))
            data.add_field('reporter_username', str(interaction.user.name))
            data.add_field('reporter_user_id', str(interaction.user.id))
            data.add_field('game', game)
            data.add_field('reason', reason)
            
            # Read the attachment data
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
                        embed = discord.Embed(
                            title="✅ Report Submitted",
                            description=f"Your report regarding **{user.name}** has been successfully recorded.\nOur moderation team will review the evidence provided.",
                            color=discord.Color.green(),
                            timestamp=discord.utils.utcnow()
                        )
                        embed.set_footer(text="Thank you for keeping outed clean!")
                        
                        await interaction.followup.send(embed=embed, ephemeral=True)
                        Console.success(f"Report submitted by {interaction.user.name} ({interaction.user.id}) for {user.name} ({user.id})", "EXPOSE")
                    else:
                        error_data = await resp.text()
                        await interaction.followup.send(
                            f"❌ **Failed to submit report.**\n"
                            f"Backend returned status: `{resp.status}`\n"
                            f"Response: ```{error_data[:100]}...```", 
                            ephemeral=True
                        )
                        Console.error(f"Failed to submit report. Status: {resp.status}, Response: {error_data}", "EXPOSE")

        except Exception as e:
            await interaction.followup.send(f"❌ **An unexpected error occurred.**\nError: `{str(e)}`", ephemeral=True)
            Console.error(f"Error in /report command: {str(e)}", "EXPOSE")
