import os
import json
import discord
from discord import ui
import aiohttp

class CheckReport(ui.View):
    def __init__(self, bot: discord.Client, report: str = ""):
        super().__init__(timeout=None)
        self.config_data = self.__load_config()
        self.report = report
        self.bot = bot
        self.baseURI = os.getenv('API_URI')
        
        self.addButtons()

    def __load_config(self):
        configPath = os.path.join("data", "expose", "config.json")
        with open(configPath, "r") as f:
            return json.load(f)
    
    def addButtons(self):
        for entry in self.config_data['buttons']:    
            button = ui.Button(
                label=entry['title'],
                style=discord.ButtonStyle.gray,
                emoji=discord.PartialEmoji(name="ticket_suppport", id=entry['button_emote']),
                custom_id=f"expose_manage_panel_{entry['value']}"
            )
            button.callback = self.callback
            self.add_item(button)

    async def callback(self, interaction: discord.Interaction):
        custom_id = interaction.data.get('custom_id', '')
        action = custom_id.replace('expose_manage_panel_', '') 

        await interaction.response.defer(ephemeral=True)

        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.baseURI}/api/reports/{self.report}/{action}"
                headers = {"x-api-key": os.getenv('API_KEY', '')}
                
                async with session.post(url, headers=headers) as resp:                    
                    if resp.status == 200:
                        await interaction.followup.send(
                            f"Report **{self.report}** successfully set to **{action}**.", 
                            ephemeral=True
                        )
                    else:
                        await interaction.followup.send(
                            f"API Error ({resp.status})", 
                            ephemeral=True
                        )
        except Exception as e:
            print(f"Error: {e}")
            await interaction.followup.send("Failed to connect to the API.", ephemeral=True)