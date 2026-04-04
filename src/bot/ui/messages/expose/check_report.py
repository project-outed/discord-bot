import discord
from discord import ui

from src.bot.ui.buttons.expose.report_manage import CheckReport

class CheckReportView(discord.ui.LayoutView):
    def __init__(self, bot: discord.Client, data: dict):
        super().__init__()
        self.bot = bot
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
                    f"Game Environment: `{self.data['game']}`\n"
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

        container.add_item(
            ui.ActionRow(
                *CheckReport(self.bot, report=self.data['id']).children
            )
        )

        self.add_item(container)