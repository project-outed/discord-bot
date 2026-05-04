import os
import json
import discord
from discord.ext import commands
from src.utils.console import Console

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
        if not guild_settings or not guild_settings.get('alert_channel'):
            Console.warning(f"No alert channel configured for guild {member.guild.name} ({member.guild.id})", module="MEMBER_MONITOR")
            return

        channel_id = guild_settings['alert_channel']
        try:
            channel = member.guild.get_channel(int(channel_id)) or await member.guild.fetch_channel(int(channel_id))
            if channel:
                embed = discord.Embed(
                    title="🚨 Flagged Member Joined",
                    description=f"A member with **{len(reports)}** accepted report(s) has joined the server.",
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow()
                )
                embed.set_author(name=member.display_name, icon_url=member.display_avatar.url)
                embed.add_field(name="User", value=f"{member.mention} ({member.id})", inline=True)
                embed.add_field(name="Reports", value=f"`{len(reports)}`", inline=True)
                
                # Add information about the latest report if available
                if reports:
                    latest = reports[0] # Assuming first in list for now
                    embed.add_field(name="Latest Reason", value=latest.get('reason', 'N/A'), inline=False)
                    embed.add_field(name="Game", value=latest.get('game', 'N/A'), inline=True)

                await channel.send(embed=embed)
                Console.success(f"Sent alert for {member.display_name} to channel {channel.name}", module="MEMBER_MONITOR")
        except Exception as e:
            Console.error(f"Failed to send alert to channel {channel_id}: {e}", module="MEMBER_MONITOR")