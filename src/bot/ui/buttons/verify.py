import discord
from discord import ui

class VerificationButton(ui.View):
    def __init__(self, timeout: float = 180, link: str = "https://discord.toolera.xyz"):
        super().__init__(timeout=timeout)
        self.link = link
        self.addButtons()

    def addButtons(self):
        button = ui.Button(
            label="Verify",
            style=discord.ButtonStyle.link,
            emoji=discord.PartialEmoji(name="ticket_support", id=1487822599810711712),
            url=self.link
        )
        self.add_item(button)