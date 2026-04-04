import os 
import discord
from discord import ui

from src.bot.ui.buttons.verify import VerificationButton

class VerificationView(discord.ui.LayoutView):
    def __init__(self, data = None):
        super().__init__()
        self.data = data
            
        container = ui.Container()

        container.add_item(
            ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="attachment://banner_verification.webp",
                )
            )
        )

        container.add_item(
            ui.Separator(spacing=discord.SeparatorSpacing.small, visible=False)
        )

        container.add_item(
            ui.TextDisplay(
                "Welcome! To access the server, please complete the verification process.\n\n"
                "`-` This step ensures only real members join the server.\n"
                "`-` It helps keep our community safe from bots, spam, and abuse.\n\n"
                "Click the button below to start the verification.\n"
                "Your personal data is securely stored and protected."
            )
        )

        container.add_item(
            ui.Separator(spacing=discord.SeparatorSpacing.small, visible=False)
        )

        container.add_item(
            ui.ActionRow(
                *VerificationButton(timeout=180, link=self.data["verification"]["oauth_url"] if self.data and "verification" in self.data else "https://discord.toolera.xyz").children
            )
        )

        container.add_item( 
            ui.TextDisplay(
                '-# By using our services, you agree to our [Terms of Service](https://tos.outed.dev) and [Privacy Policy](https://privacy.outed.dev).'
            )
        )

        self.add_item(container)
