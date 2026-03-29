import discord
from discord import ui

class RemoveUserView(discord.ui.LayoutView):
    def __init__(self):
        super().__init__()

        container = ui.Container()

        container.add_item(ui.MediaGallery(discord.MediaGalleryItem(
            media="attachment://banner_remove_user.webp",
        )))
        
        container.add_item(
            ui.Separator(spacing=discord.SeparatorSpacing.large, visible=False)
        )

        self.add_item(container)