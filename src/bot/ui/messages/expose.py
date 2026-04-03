import discord
from discord import ui

class ExposeView(discord.ui.LayoutView):
    def __init__(self, data: dict = None):
        super().__init__()
        self.data = data

        container = ui.Container()

        container.add_item(
            ui.TextDisplay(
                "### **RULE VIOLATION NOTICE**\n\n"
                "**TARGET IDENTIFICATION**\n"
                f"Name: `{self.data['target_username']}`\n"
                f"Platform ID: `{self.data['target_user_id']}`\n\n"
                "**VIOLATION DATA**\n"
                f"Software Detected: `{self.data['cheat']}`\n"
                f"Game Environment: `{self.data['game']}`\n"
                f"Calculated Trust Score: `{self.data['trust_score']}/100`\n\n"
            )
        )

        container.add_item(
            ui.Separator(spacing=discord.SeparatorSpacing.small, visible=False)
        )

        container.add_item( 
            ui.TextDisplay(
                '-# By using our services, you agree to our [Terms of Service](https://tos.outed.dev) and [Privacy Policy](https://privacy.outed.dev).'
            )
        )

        self.add_item(container)
