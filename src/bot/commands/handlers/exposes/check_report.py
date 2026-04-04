import os
import io
from typing import List
import discord
import aiohttp
from discord.ext import commands
from discord import app_commands

from src.utils.permission import Permission

from src.bot.ui.messages.expose.check_report import CheckReportView 

class CheckReport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.base_url = os.getenv('API_URI') 

    async def reports_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        reports = await self.bot.db.fetch("SELECT id, target_username FROM reports WHERE status = 'pending'")
        choices = []
        for report in reports:
            report_display = f"ID: {report['id']} - {report['target_username']}"
            if current.lower() in report_display.lower():
                choices.append(app_commands.Choice(name=report_display, value=str(report['id'])))
        return choices[:25]

    @app_commands.guilds(int(os.getenv("MAIN_GUILD")))
    @app_commands.command(name="check_report", description="Check a user's report")
    @app_commands.autocomplete(report=reports_autocomplete)
    async def check_report(self, interaction: discord.Interaction, report: str):        
        await interaction.response.defer(ephemeral=True)

        permission_ids = Permission().get_permission(config=os.path.join("data", "expose", "config.json"))
        access = Permission(user=interaction.user, ids=permission_ids['permission']).role()

        if not access:
            return await interaction.followup.send("You don't have permission to use this command.", ephemeral=True)
        
        report_id = int(report)
        rows = await self.bot.db.fetch("SELECT * FROM reports WHERE id = $1", report_id)
        
        if not rows:
            return await interaction.followup.send("Report not found.", ephemeral=True)
        
        report_data = rows[0]
        headers = {"x-api-key": os.getenv('API_KEY')} 
        files_to_send = []

        async with aiohttp.ClientSession() as session:                
            evidence_url = f"{self.base_url}/api/reports/{report_id}/evidence"
            async with session.get(evidence_url, headers=headers) as resp:
                if resp.status == 200:
                    evidence_list = await resp.json()

                    for evidence in evidence_list:
                        evidence_id = evidence["id"]
                        file_url = f"{self.base_url}/api/reports/{report_id}/evidence/{evidence_id}"
                        
                        async with session.get(file_url, headers=headers) as file_resp:
                            if file_resp.status == 200:
                                image_bytes = await file_resp.read()
                                filename = evidence.get("url", f"file_{evidence_id}.png").split("/")[-1]
                                
                                files_to_send.append(discord.File(
                                    fp=io.BytesIO(image_bytes), 
                                    filename=f"report_{report_id}_{filename}"
                                ))

            target_id = report_data.get('target_user_id') or report_data.get('target_discord_id')
            user = await self.bot.fetch_user(int(target_id))

            view_data = {
                "id": str(report_data['id']),
                "target_username": user.display_name if user else report_data.get('target_username', 'Unknown'),
                "target_user_id": str(user.id) if user else str(target_id),
                "cheat": report_data.get('reason', report_data.get('cheat', 'N/A')),
                "game": report_data.get('game', 'N/A'),
                "avatar_url": user.display_avatar.url if user else "",
                "evidence": files_to_send
            }
            
            await interaction.followup.send(
                view=CheckReportView(bot=self.bot, data=view_data),
                files=files_to_send,
                ephemeral=True
            )