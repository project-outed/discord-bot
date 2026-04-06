import os
import discord
from discord.ext import commands
from discord import app_commands

from src.utils.console import Console
from src.utils.permission import Permission

class Close(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(int(os.getenv("MAIN_GUILD")))
    @app_commands.command(name="close", description="Close the current ticket")
    async def close(self, interaction: discord.Interaction):
        permission_ids = Permission().get_permission(config=os.path.join("data", "tickets", "config.json"))
        access = Permission(user=interaction.user, ids=permission_ids['permission'][0]).role()

        if not access:
            return await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

        from src.bot.ui.modals.ticket.close import TicketCloseReasonModal
        await interaction.response.send_modal(TicketCloseReasonModal(self.bot))