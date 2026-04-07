from src.bot.ui.buttons.ticket.delete import DeleteTicketButton
import discord
from discord import ui
import asyncio

class CloseTicketView(discord.ui.LayoutView):
    def __init__(self, data: dict, bot: discord.Client):
        super().__init__(timeout=None)
        self.data = data
        self.bot = bot

        container = ui.Container()

        container.add_item(ui.MediaGallery(discord.MediaGalleryItem(
            media="attachment://banner_channel.webp",
        )))
        
        container.add_item(
            ui.Section(
                ui.TextDisplay(
                    "**USER INFORMATION**\n"
                    f"Username: `{self.data.get('username', 'N/A')}`\n"
                    f"Platform ID: `{self.data.get('platform_id', 'N/A')}`\n"
                    f"Trust Score: `{self.data.get('trust_score', 'N/A')}/100`\n\n"

                    "**TICKET INFORMATION**\n"
                    f"Category: `{self.data.get('category', 'N/A')}`\n"
                    f"Closed By: `{self.data.get('closed_by', 'N/A')}`\n"
                    f"Closed Reason: `{self.data.get('reason', 'N/A')}`\n"
                    f"Closed At: `{self.data.get('closed_at', 'N/A')}`\n\n"

                    "-# This ticket has been closed. You may press the button to delete the channel."
                ),
                accessory=ui.Thumbnail(self.data.get('avatar')) if self.data.get('avatar') else None
            )
        )

        container.add_item(
            ui.Separator(spacing=discord.SeparatorSpacing.small, visible=True)
        )

        container.add_item(
            ui.ActionRow(
                *DeleteTicketButton(self.bot).children
            )
        )

        container.add_item(ui.TextDisplay(
            '-# By using our services, you agree to our [Terms of Service](https://tos.outed.dev) and [Privacy Policy](https://privacy.outed.dev).'
        ))

        self.add_item(container)