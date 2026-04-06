from datetime import datetime
import os
import json
import discord
from discord import ui

from src.bot.ui.messages.ticket.channel import ChannelView

class DeleteTicketButton(ui.View):
    def __init__(self, bot: discord.Client):
        super().__init__(timeout=None)
        self.bot = bot
        self.addButtons()
    
    def addButtons(self):
        button = ui.Button(
            label="Delete",
            style=discord.ButtonStyle.gray,
            emoji="🗑️",
            custom_id="delete_ticket_btn"
        )
        button.callback = self.callback
        self.add_item(button)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("Deleting ticket in 5 seconds...", ephemeral=False)
        await self.bot.db.tickets.delete_ticket(interaction.channel.id)
        
        import asyncio
        await asyncio.sleep(5)
        
        try:
            await interaction.channel.delete()
        except discord.NotFound:
            pass