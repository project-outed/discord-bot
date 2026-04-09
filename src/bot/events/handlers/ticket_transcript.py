import discord
from discord.ext import commands

class TranscriptEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        ticket = await self.bot.db.tickets.get_ticket(message.channel.id)
        if not ticket:
            return

        import os
        import aiohttp
        from datetime import datetime
        
        base_dir = os.path.join("data", "tickets", "transcripts", str(message.channel.id))
        attachments_dir = os.path.join(base_dir, "attachments")
        os.makedirs(attachments_dir, exist_ok=True)

        journal_path = os.path.join(base_dir, "journal.txt")
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with open(journal_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message.author}: {message.content or ''}\n")

        attachments = []
        for attachment in message.attachments:
            file_ext = os.path.splitext(attachment.filename)[1]
            local_filename = f"{message.id}_{attachment.id}{file_ext}"
            local_path = os.path.join(attachments_dir, local_filename)

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(attachment.url) as resp:
                        if resp.status == 200:
                            with open(local_path, "wb") as f:
                                f.write(await resp.read())
                            
                            attachments.append({
                                "filename": attachment.filename,
                                "local_path": local_path.replace("\\", "/"),
                                "content_type": str(attachment.content_type)
                            })
                            
                            with open(journal_path, "a", encoding="utf-8") as f:
                                f.write(f"[{timestamp}] {message.author} attached file: {attachment.filename}\n")
            except Exception as e:
                from src.utils.console import Console
                Console.error(f"Failed to download attachment {attachment.filename}: {e}", "TRANSCRIPT")

        await self.bot.db.transcripts.save_message(
            channel_id=message.channel.id,
            message_id=message.id,
            author_id=message.author.id,
            author_tag=str(message.author),
            content=message.content,
            attachments=attachments
        )
