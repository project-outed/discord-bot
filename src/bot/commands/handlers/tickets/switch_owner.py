import os
import discord
from discord.ext import commands
from discord import app_commands

from src.utils.console import Console
from src.utils.permission import Permission

class Switch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(int(os.getenv("MAIN_GUILD")))
    @app_commands.command(name="switch", description="Switch the ticket owner")
    async def switch(self, interaction: discord.Interaction, new_owner: discord.Member):
        permission_ids = Permission().get_permission(config=os.path.join("data", "tickets", "config.json"))
        access = Permission(user=interaction.user, ids=permission_ids['permission'][0]).role()

        if not access:
            return await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

        ticket = await self.bot.db.tickets.get_ticket(interaction.channel.id)
        if not ticket:
            return await interaction.response.send_message("This channel is not a ticket.", ephemeral=True)
            
        if new_owner.id == ticket['owner_id']:
            return await interaction.response.send_message(f"{new_owner.mention} is already the owner of this ticket.", ephemeral=True)

        
        success = await self.bot.db.tickets.switch_owner(interaction.channel.id, new_owner.id)
        if success:
            await interaction.channel.set_permissions(new_owner, read_messages=True, send_messages=True)
            await interaction.response.send_message(f"Ticket owner has been switched to {new_owner.mention}.", ephemeral=False)
        else:
            await interaction.response.send_message("An error occurred while switching the owner.", ephemeral=True)