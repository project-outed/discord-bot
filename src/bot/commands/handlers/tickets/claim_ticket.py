import os
import discord
from discord.ext import commands
from discord import app_commands

from src.utils.console import Console
from src.utils.permission import Permission

class Claim(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(int(os.getenv("MAIN_GUILD")))
    @app_commands.command(name="claim", description="Claim the ticket")
    async def claim(self, interaction: discord.Interaction):
        permission_ids = Permission().get_permission(config=os.path.join("data", "tickets", "config.json"))
        access = Permission(user=interaction.user, ids=permission_ids['permission'][0]).role()

        if not access:
            return await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

        ticket = await self.bot.db.tickets.get_ticket(interaction.channel.id)
        if not ticket:
            return await interaction.response.send_message("This channel is not a ticket.", ephemeral=True)
        if ticket.get('claimed_by'):
            return await interaction.response.send_message(f"Ticket is already claimed by <@{ticket['claimed_by']}>.", ephemeral=True)
            
        await self.bot.db.tickets.claim_ticket(interaction.channel.id, interaction.user.id)
        await interaction.response.send_message(f"Ticket has been claimed by {interaction.user.mention}.", ephemeral=False)