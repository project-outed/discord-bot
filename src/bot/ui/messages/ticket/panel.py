import discord
from discord import ui
from src.bot.ui.buttons.ticket.panel import PanelButtons

class PanelView(discord.ui.LayoutView):
    def __init__(self, bot: discord.Client, data = None):
        super().__init__()
        self.bot = bot
        self.data = data

        container = ui.Container()

        container.add_item(
            ui.MediaGallery(
                discord.MediaGalleryItem(
                    media="attachment://banner_ticket_panel.webp",
                )
            )
        )
        
        container.add_item(
            ui.Separator(spacing=discord.SeparatorSpacing.large, visible=False)
        )

        categories = self.data["categories"]
        for index, category in enumerate(categories):
            emotes = category.get('emotes', ["", "", "", ""])
            
            container.add_item(
                ui.TextDisplay(
                    "%s%s   **%s**\n%s%s   %s" % (
                        f"<:a:{emotes[0]}>" if emotes[0] else "",
                        f"<:a:{emotes[1]}>" if emotes[1] else "",
                        category['title'].replace("**", ""),
                        f"<:a:{emotes[2]}>" if emotes[2] else "",
                        f"<:a:{emotes[3]}>" if emotes[3] else "",
                        category['description']
                    )
                )
            )

            if index < len(categories) - 1:
                container.add_item(
                    ui.Separator(spacing=discord.SeparatorSpacing.small, visible=True)
                )

        container.add_item(
            ui.Separator(spacing=discord.SeparatorSpacing.large, visible=False)
        )

        container.add_item(
            ui.ActionRow(
                *PanelButtons(self.bot).children
            )
        )
        container.add_item(ui.TextDisplay(
            '-# By using our services, you agree to our [Terms of Service](https://tos.outed.dev) and [Privacy Policy](https://privacy.outed.dev).'
        ))

        self.add_item(container)