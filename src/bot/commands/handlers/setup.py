import discord
from discord.ext import commands
from discord import app_commands
from src.utils.console import Console

class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setup_alerts", description="Setup the alert channel for the member monitor")
    @app_commands.describe(channel="The channel where alerts should be sent")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_alerts(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.defer(ephemeral=True)
        
        success = await self.bot.db.guilds.update_guild_settings(
            interaction.guild.id, 
            alert_channel=str(channel.id)
        )
        
        if success:
            await interaction.followup.send(f"✅ Successfully set the alert channel to {channel.mention}")
            Console.success(f"Guild {interaction.guild.name} updated alert channel to {channel.id}", "SETUP")
        else:
            await interaction.followup.send("❌ Failed to update guild settings in the database.")

async def setup(bot):
    await bot.add_cog(Setup(bot))
