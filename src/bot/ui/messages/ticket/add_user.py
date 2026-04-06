import discord
from discord import ui

class AddUserView(discord.ui.LayoutView):
    def __init__(self, data: dict):
        super().__init__()
        self.data = data

        container = ui.Container()

        container.add_item(
            ui.Section(
                ui.TextDisplay(
                    "### **NEW USER ADDED TO THE TICKET**\n\n"
                    f"**USER INFORMATION**\n"
                    f"Username: `{self.data.get('username', 'N/A')}`\n"
                    f"Platform ID: `{self.data.get('platform_id', 'N/A')}`\n"
                    f"Trust Score: `{self.data.get('trust_score', 'N/A')}/100`\n\n"

                    "-# If you believe this was a mistake, please contact the staff immediately.\n"
                    f"-# You can remove the user again using: `/remove user:@{self.data.get('platform_id', 'N/A')}`"
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