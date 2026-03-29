import os
import json
import discord
from src.bot.ui.buttons.ticket.panel import PanelButtons

bot: discord.Client = None

class UIManager:
    def __init__(self):
        self.bot = bot

    async def load(self):
        self.bot.add_view(PanelButtons(self.bot))