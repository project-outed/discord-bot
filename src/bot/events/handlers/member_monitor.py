import discord
from discord.ext import commands
from src.utils.console import Console
from src.bot.ui.messages.member_monitor import MemberMonitorView

class MemberMonitor(commands.Cog):
    def __init__(self, bot: discord.Client):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        Console.info(f"Member {member.display_name} ({member.id}) joined {member.guild.name} ({member.guild.id})", module="MEMBER_MONITOR")
        
        reports = await self.bot.db.reports.get_accepted_reports(member.id)

        if not reports:
            Console.info(f"No accepted reports found for member {member.display_name} ({member.id})", module="MEMBER_MONITOR")
            return

        Console.info(f"Found {len(reports)} accepted reports for member {member.display_name} ({member.id})", module="MEMBER_MONITOR")

        guild_settings = await self.bot.db.guilds.get_guild_settings(member.guild.id)
        trust_score = await self.bot.db.fetch("SELECT trust_score FROM users WHERE user_id = $1", member.id)

        if not guild_settings or not guild_settings.get('alert_channel'):
            Console.warning(f"No alert channel configured for guild {member.guild.name} ({member.guild.id})", module="MEMBER_MONITOR")
            return

        channel_id = guild_settings['alert_channel']
        try:
            channel = member.guild.get_channel(int(channel_id)) or await member.guild.fetch_channel(int(channel_id))
            if channel:
                view_data = {
                    "username": member.display_name,
                    "platform_id": str(member.id),
                    "avatar": member.display_avatar.url,
                    "trust_score": trust_score[0]['trust_score'] if trust_score else None,
                    "reports": [
                        {
                            "id": r.get("id"),
                            "reason": r.get("reason", "N/A"),
                            "game": r.get("game", "N/A"),
                            "created_at": r.get("created_at", ""),
                        }
                        for r in reports
                    ],
                }

                await channel.send(view=MemberMonitorView(bot=self.bot, data=view_data))
        except Exception as e:
            Console.error(f"Failed to send alert to channel {channel_id}: {e}", module="MEMBER_MONITOR")