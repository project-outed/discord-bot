import discord
from discord import ui

class RenameTicketView(discord.ui.LayoutView):
    def __init__(self):
        super().__init__()

        container = ui.Container()

        container.add_item(ui.MediaGallery(discord.MediaGalleryItem(
            media="attachment://banner_rename_ticket.webp",
        )))
        
        container.add_item(
            ui.Separator(spacing=discord.SeparatorSpacing.large, visible=False)
        )

        self.add_item(container)