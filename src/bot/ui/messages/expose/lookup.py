import discord
from discord import ui
from datetime import datetime

class LookupView(discord.ui.LayoutView):
    def __init__(self, data = None):
        super().__init__()
        self.data = data
        container = ui.Container()
        
        container.add_item(
            ui.Section(
                ui.TextDisplay(
                    "**USER INFORMATION**\n" \
                    "Username: `{username}`\n" \
                    "Platform ID: `{platform_id}`\n" \
                    "Trust Score: `{trust_score}/100`".format(
                        username=self.data['username'],
                        platform_id=self.data['platform_id'],
                        trust_score=self.data.get('trust_score', 'N/A')
                    )
                ),
                accessory=ui.Thumbnail(self.data['avatar'])
            )
        )

        container.add_item(
            ui.Separator(spacing=discord.SeparatorSpacing.small, visible=False)
        )

        container.add_item(
            ui.TextDisplay(
                "**REPORT HISTORY TIMELINE**\n"
                "A comprehensive overview of all reports associated with this account.\n"
                "Each record specifies the reported violation, the associated context, and the date of entry."
            )
        )

        reports = self.data.get("reports", [])
        if reports:
            container.add_item(
                ui.Separator(spacing=discord.SeparatorSpacing.small, visible=False)
            )

            for category in reports:           
                timestamp_obj = datetime.fromisoformat(category['created_at'].replace("Z", "+00:00"))

                container.add_item(
                    ui.TextDisplay(
                        "**%s**\n-# %s" % (
                            category['reason'],
                            f"Game: {category['game']} - Added on: {timestamp_obj.strftime('%Y-%m-%d %H:%M:%S')}"
                        )
                    )
                )

                container.add_item(
                    ui.Separator(spacing=discord.SeparatorSpacing.small, visible=True)
                )
        else:
            container.add_item(
                ui.TextDisplay(
                    "`-` **This account currently has no documented reports.**"
                )
            )

            container.add_item(
                ui.Separator(spacing=discord.SeparatorSpacing.small, visible=True)
            )

        container.add_item(
            ui.TextDisplay(
                '-# By using our services, you agree to our [Terms of Service](https://tos.outed.dev) and [Privacy Policy](https://privacy.outed.dev).'
            )
        )

        self.add_item(container)