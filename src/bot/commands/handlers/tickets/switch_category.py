import os
import discord
from discord.ext import commands
from discord import app_commands
from typing import List

import json

from src.utils.console import Console
from src.utils.permission import Permission

class Category(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def category_autocomplete(self, interaction: discord.Interaction, current: str) -> List[app_commands.Choice[str]]:
        try:
            with open("data/tickets/config.json", "r") as f:
                config_data = json.load(f)
            categories = config_data.get('categories', [])
            
            ticket = await self.bot.db.tickets.get_ticket(interaction.channel.id)
            current_type = ticket.get('ticket_type') if ticket else None
        except Exception as e:
            Console.error(f"Failed to load ticket config or DB: {e}", module="TICKET")
            categories = []
            current_type = None
            
        return [
            app_commands.Choice(name=cat['title'], value=cat['value'])
            for cat in categories 
            if current.lower() in cat['title'].lower() and cat['value'] != current_type
        ][:25]


    @app_commands.guilds(int(os.getenv("MAIN_GUILD")))
    @app_commands.command(name="category", description="Switch the ticket category")
    @app_commands.autocomplete(new_category=category_autocomplete)
    async def category(self, interaction: discord.Interaction, new_category: str):
        permission_ids = Permission().get_permission(config=os.path.join("data", "tickets", "config.json"))
        access = Permission(user=interaction.user, ids=permission_ids['permission'][0]).role()

        if not access:
            return await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

        ticket = await self.bot.db.tickets.get_ticket(interaction.channel.id)
        if not ticket:
            return await interaction.response.send_message("This channel is not a ticket.", ephemeral=True)
            
        success = await self.bot.db.tickets.switch_category(interaction.channel.id, new_category)
        if success:
            await interaction.response.send_message(f"Ticket category has been switched to `{new_category}`.", ephemeral=False)
        else:
            await interaction.response.send_message("An error occurred while switching the category.", ephemeral=True)