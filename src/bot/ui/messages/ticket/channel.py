import discord
from discord import ui

class ChannelView(discord.ui.LayoutView):
    def __init__(self, data: dict):
        super().__init__()
        self.data = data

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
                    f"Reason: `{self.data.get('reason', 'N/A')}`\n"
                    f"Category: `{self.data.get('category', 'N/A')}`\n"
                    f"Created At: `{self.data.get('created_at', 'N/A')}`\n\n"

                    "-# Thank you for reaching out. Please remain on standby while our team reviews your request."
                ),
                accessory=ui.Thumbnail(self.data.get('avatar')) if self.data.get('avatar') else None
            )
        )

        container.add_item(
            ui.Separator(spacing=discord.SeparatorSpacing.small, visible=True)
        )

        container.add_item(ui.TextDisplay(
            '-# By using our services, you agree to our [Terms of Service](https://tos.outed.dev) and [Privacy Policy](https://privacy.outed.dev).'
        ))

        self.add_item(container)