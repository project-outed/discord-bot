import discord
from discord import ui

from src.bot.ui.buttons.expose.report_manage import CheckReport

class CreateReportView(discord.ui.LayoutView):
    def __init__(self, data: dict):
        super().__init__()
        self.data = data

        container = ui.Container()
        
        container.add_item(
            ui.Section(
                ui.TextDisplay(
                    "**TARGET IDENTIFICATION**\n"
                    f"Name: `{self.data['target_username']}`\n"
                    f"Platform ID: `{self.data['target_user_id']}`\n\n"
                    "**VIOLATION DATA**\n"
                    f"Software Detected: `{self.data['cheat']}`\n"
                    f"Game Environment: `{self.data['game']}`\n\n"
                    "-# Thank you for submitting this report. Your vigilance helps us maintain the integrity of our community and ensures a fair environment for all players."
                ),
                accessory=ui.Thumbnail(self.data['avatar_url'])
            )
        )

        evidence_list = self.data.get('evidence', [])
        
        if evidence_list:
            container.add_item(
                ui.Separator(spacing=discord.SeparatorSpacing.small, visible=False)
            )

            container.add_item(
                ui.TextDisplay(
                    "**ATTACHED EVIDENCE**\n"
                    "-# Distribution of these materials is strictly prohibited without authorization."
                )
            )

            for evidence_file in evidence_list:
                container.add_item(
                    ui.MediaGallery(
                        discord.MediaGalleryItem(
                            media=evidence_file,
                            spoiler=True
                        )
                    )
                )
                
        else:
            container.add_item(
                ui.TextDisplay("`-` **No evidence files provided.**")
            )

        self.add_item(container)