import os
import json
import discord
from discord.ext import commands
from discord import app_commands

from src.bot.ui.messages.ticket.panel import PanelView
from src.utils.permission import Permission

class TicketPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.__load_config()

    def __load_config(self):
        configPath = os.path.join("data", "tickets", "config.json")
        with open(configPath, "r") as f:
            data = json.load(f)
            return data

    @app_commands.guilds(int(os.getenv("MAIN_GUILD")))
    @app_commands.command(name="panel", description="Send the main ticket creation panel")
    async def panel(self, interaction: discord.Interaction):
        permission_ids = Permission().get_permission(config=os.path.join("data", "tickets", "config.json"))
        access = Permission(user=interaction.user, ids=permission_ids['panel']['permissions']).role()

        if not access:
            return await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)



        channel_id = int(self.config["panel"]["channel_id"])
        channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
        
        if not channel:
            await interaction.response.send_message("Error: Could not find the configured panel channel.", ephemeral=True)
            return

        await channel.send(
            view=PanelView(self.bot, data={
                "categories": self.config["categories"]
            }),
            files=[
                discord.File("images/banners/banner.webp", filename="banner_ticket_panel.webp")
            ]
        )
        await interaction.response.send_message(f"Panel sent successfully to {channel.mention}", ephemeral=True)
