from datetime import datetime
import os
import json
import discord
from discord import ui

from src.bot.ui.messages.ticket.channel import ChannelView

class PanelButtons(ui.View):
    def __init__(self, bot: discord.Client):
        super().__init__(timeout=None)
        self.data = self.__load_config()
        self.bot = bot
        
        self.addButtons()

    def __load_config(self):
        configPath = os.path.join("data", "tickets", "config.json")
        with open(configPath, "r") as f:
            data = json.load(f)
            return data
    
    def addButtons(self):
        for category in self.data['categories']:    
            button = ui.Button(
                label=category['title'],
                style=discord.ButtonStyle.gray,
                emoji=discord.PartialEmoji(name=f"ticket_{category['value']}", id=category['button_emote']),
                custom_id=f"ticket_panel_{category['value']}"
            )
            button.callback = self.callback
            self.add_item(button)

    async def callback(self, interaction: discord.Interaction):
        ticket_category = interaction.data.get('custom_id', 'support').replace('ticket_panel_', '').replace('_', ' ')
        await interaction.response.send_modal(TicketReasonModal(self.bot, ticket_category, self))

class TicketReasonModal(ui.Modal, title='Create Ticket'):
    reason = ui.TextInput(
        label='Reason for ticket creation', 
        style=discord.TextStyle.paragraph, 
        placeholder='Please describe your issue...', 
        required=True, 
        max_length=1000
    )

    def __init__(self, bot: discord.Client, ticket_category: str, panel_view: "PanelButtons"):
        super().__init__()
        self.bot = bot
        self.ticket_category = ticket_category
        self.panel_view = panel_view

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        category = self.bot.get_channel(int(self.panel_view.data['category_channel_id']))
        if not category:
            await interaction.followup.send("Error: Could not find the configured category channel.", ephemeral=True)
            return
        
        channel = await interaction.guild.create_text_channel(
            name=f"{self.ticket_category[:10]}-{interaction.user.name}".lower(),
            category=category,
            reason=f"Ticket created by {interaction.user} (ID: {interaction.user.id}) - Reason: {self.reason.value}",
            overwrites={
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.guild.get_role(int(self.panel_view.data['permission'][0])): discord.PermissionOverwrite(read_messages=True, send_messages=True),
            },
        )
        
        await self.bot.db.tickets.create_ticket(
            channel_id=channel.id,
            guild_id=interaction.guild.id,
            owner_id=interaction.user.id,
            ticket_type=self.ticket_category
        )

        data = await self.bot.db.fetch("SELECT trust_score FROM users WHERE user_id = $1", interaction.user.id, fetch_one=True)
        if not data:
            return await interaction.followup.send("User not found in database.", ephemeral=True)

        await interaction.followup.send(f"Ticket created successfully in {channel.mention}", ephemeral=True)
        
        await channel.send(
            view=ChannelView(data={
                "username": str(interaction.user.display_name),
                "platform_id": str(interaction.user.id),
                "trust_score": str(data['trust_score']),
                "avatar": interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url,
                "reason": self.reason.value,
                "category": self.ticket_category,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }), 
            files=[
                discord.File("images/banners/banner.webp", filename="banner_channel.webp")
            ]
        )