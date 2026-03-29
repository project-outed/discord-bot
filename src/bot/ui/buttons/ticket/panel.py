import os
import json
import discord
from discord import ui

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
                emoji=discord.PartialEmoji(name=f"ticket_{category['value']}", id=category['big_emote']),
                custom_id=f"ticket_panel_{category['value']}"
            )
            button.callback = self.callback
            self.add_item(button)

    async def callback(self, interaction: discord.Interaction):
        ticket_category = interaction.data.get('custom_id', 'support').replace('ticket_panel_', '').replace('_', ' ')
        category = self.bot.get_channel(int(self.data['category_channel_id']))
        if not category:
            await interaction.response.send_message("Error: Could not find the configured category channel.", ephemeral=True)
            return
        
        
        channel = await interaction.guild.create_text_channel(
            name=f"{ticket_category}-{interaction.user.name}".lower(),
            category=category,
            reason=f"Ticket created by {interaction.user} (ID: {interaction.user.id}) in category {category}",
            overwrites={
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                interaction.guild.get_role(int(self.data['staff_role_id'])): discord.PermissionOverwrite(read_messages=True, send_messages=True),
            },
        )

        await interaction.response.send_message(f"Ticket created successfully in {channel.mention}", ephemeral=True)