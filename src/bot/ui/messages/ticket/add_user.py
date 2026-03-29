import discord
from discord import ui

class AddUserView(discord.ui.LayoutView):
    def __init__(self, data = None):
        super().__init__()
        self.data = data

        container = ui.Container()

        container.add_item(ui.MediaGallery(discord.MediaGalleryItem(
            media="attachment://banner_add_user.webp",
        )))
        
        container.add_item(
            ui.Separator(spacing=discord.SeparatorSpacing.large, visible=False)
        )

        self.add_item(container)