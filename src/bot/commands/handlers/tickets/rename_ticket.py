import os
import discord
from discord.ext import commands
from discord import app_commands

from src.utils.console import Console
from src.utils.permission import Permission

class Rename(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(int(os.getenv("MAIN_GUILD")))
    @app_commands.command(name="rename", description="Rename the ticket channel")
    async def rename(self, interaction: discord.Interaction, new_name: str):
        permission_ids = Permission().get_permission(config=os.path.join("data", "tickets", "config.json"))
        access = Permission(user=interaction.user, ids=permission_ids['permission'][0]).role()

        if not access:
            return await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

        ticket = await self.bot.db.tickets.get_ticket(interaction.channel.id)
        if not ticket:
            return await interaction.response.send_message("This channel is not a ticket.", ephemeral=True)
            
        await interaction.channel.edit(name=new_name)
        await interaction.response.send_message(f"Ticket renamed to `{new_name}`.", ephemeral=False)