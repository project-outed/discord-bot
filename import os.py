import os
import re
import time
from datetime import timedelta
from collections import defaultdict
from pathlib import Path

import aiohttp
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

import ids
from tickets.ai_support.process import (
    ai_channel_ids_for_debug,
    channel_is_ai_support,
    handle_ai_support_message,
)

load_dotenv(Path(__file__).resolve().parent / ".env")


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guild_messages = True
        super().__init__(command_prefix="!", intents=intents)
        self._status_i = 0
        self.ai_http: aiohttp.ClientSession | None = None
        self.message_times = defaultdict(list)
        self.link_regex = re.compile(r"(http[s]?://|discord\.gg/)", re.IGNORECASE)

    async def setup_hook(self) -> None:
        self.ai_http = aiohttp.ClientSession()
        if not os.getenv("OPENAI_API_KEY", "").strip():
            print(
                "WARNING: OPENAI_API_KEY missing in .env — AI support cannot reply."
            )
        await self.tree.sync()

    async def close(self) -> None:
        if self.ai_http and not self.ai_http.closed:
            await self.ai_http.close()
            self.ai_http = None
        await super().close()

    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot or not message.guild:
            return
            
        cat_id = getattr(message.channel, "category_id", None)
        if isinstance(message.channel, discord.Thread) and message.channel.parent:
            cat_id = getattr(message.channel.parent, "category_id", None)

        if cat_id != 1487210162388205638 and self.link_regex.search(message.content):
            try:
                await message.delete()
                await message.channel.send(f"⚠️ {message.author.mention}, you are not allowed to send links here!", delete_after=5)
            except discord.Forbidden:
                pass
            return

        now = time.time()
        uid = message.author.id
        times = [t for t in self.message_times[uid] if now - t < 10.0]
        times.append(now)
        self.message_times[uid] = times

        msg_count = len(times)
        if msg_count == 5:
            await message.channel.send(f"{message.author.mention}, warning: Type slower, or you will get timed out!", delete_after=5)
        elif msg_count >= 6:
            try:
                await message.author.timeout(timedelta(minutes=5), reason="Spam")
                await message.channel.send(f"{message.author.mention} has been timed out for 5 minutes due to spam.")
                self.message_times[uid] = []
                # Fall through to return if timeout successful
                return
            except discord.Forbidden:
                # If bot lacks permission to timeout this user (e.g. they are an admin), it will ignore the timeout but still send the warning if you prefer, 
                # or just pass and do nothing. Here we just print the warning to show it triggered.
                await message.channel.send(f"⚠️ {message.author.mention} spam detected, but I do not have permissions to timeout an admin!")
                self.message_times[uid] = []
                return

        await self.process_commands(message)
        ch = message.channel
        if not isinstance(ch, (discord.abc.GuildChannel, discord.Thread)):
            return
        if not channel_is_ai_support(ch):
            return
        if self.ai_http is None:
            return
        await handle_ai_support_message(self, message, http=self.ai_http)

    async def on_ready(self) -> None:
        print(f"Logged in as {self.user} (id: {self.user.id})")
        self._status_i = 0
        await self.change_presence(
            status=discord.Status.dnd,
            activity=discord.Game(name="outed.dev"),
        )
        if not self.rotate_status.is_running():
            self.rotate_status.start()

    @tasks.loop(seconds=10)
    async def rotate_status(self) -> None:
        texts = ("outed.dev", "gg./outed")
        self._status_i += 1
        await self.change_presence(
            status=discord.Status.dnd,
            activity=discord.Game(name=texts[self._status_i % 2]),
        )

    @rotate_status.before_loop
    async def before_rotate_status(self) -> None:
        await self.wait_until_ready()


bot = DiscordBot()


def _debug_category_id(ch: discord.abc.GuildChannel) -> int | None:
    if isinstance(ch, discord.Thread):
        parent = ch.parent
        return parent.category_id if parent else None
    return ch.category_id


@bot.tree.command(name="ping", description="Check that the bot responds")
async def ping(interaction: discord.Interaction) -> None:
    await interaction.response.send_message("Pong!")


@bot.tree.command(
    name="ai_debug",
    description="Show channel and category ID (use to match ids.py)",
)
async def ai_debug(interaction: discord.Interaction) -> None:
    if not interaction.guild or not isinstance(
        interaction.channel, (discord.abc.GuildChannel, discord.Thread)
    ):
        await interaction.response.send_message(
            "Server channels only.", ephemeral=True
        )
        return
    ch = interaction.channel
    cat_id = _debug_category_id(ch)
    match = channel_is_ai_support(ch)
    await interaction.response.send_message(
        f"**channel_id:** `{ch.id}`\n"
        f"**category_id (resolved):** `{cat_id}`\n"
        f"**ids.py — AI_SUPPORT_CATEGORY_ID:** `{ids.AI_SUPPORT_CATEGORY_ID}`\n"
        f"**Channel-ID whitelist (ids.py + AI_CHANNEL_IDS_EXTRA):** `{ai_channel_ids_for_debug()}`\n"
        f"**The bot treats this channel as AI-support:** {'yes' if match else 'no'}\n"
        f"If **no**: set the correct channel-ID in `ids.py` or add it to `.env` as "
        f"`AI_CHANNEL_IDS_EXTRA=1234567890123456789` (comma separated). "
        f"Give the bot **Read Message History** + **Send Messages** in the channel.",
        ephemeral=True,
    )


from discord import app_commands

@bot.tree.command(name="clearchat", description="Clear messages in the channel (Management only)")
@app_commands.describe(amount="Amount of messages to delete (default: 100)")
async def clearchat(interaction: discord.Interaction, amount: int = 100) -> None:
    has_permission = False
    if interaction.user.id == ids.MANAGEMENT_ID:
        has_permission = True
    elif hasattr(interaction.user, 'roles'):
        if any(r.id == ids.MANAGEMENT_ID for r in interaction.user.roles):
            has_permission = True
            
    if not has_permission:
        await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
        return
        
    await interaction.response.defer(ephemeral=True)
    
    if not hasattr(interaction.channel, "purge"):
        await interaction.followup.send("Cannot delete messages in this type of channel.", ephemeral=True)
        return
        
    try:
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"✅ Deleted {len(deleted)} messages.", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("❌ I do not have permission to delete messages here. Check my 'Manage Messages' permissions.", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.followup.send(f"❌ Error during deletion: {e}", ephemeral=True)


@bot.tree.command(name="register-cheater", description="Register a suspected cheater to the database")
@app_commands.describe(
    target_id="Target's Discord ID or SteamID64",
    cheat="What cheat were they using? (e.g. Aimbot, ESP)",
    evidence="Upload an image or video outlining the cheat"
)
async def register_cheater(
    interaction: discord.Interaction, 
    target_id: str, 
    cheat: str, 
    evidence: discord.Attachment
) -> None:
    await interaction.response.defer(ephemeral=True)
    
    try:
        file_bytes = await evidence.read()
        
        data = aiohttp.FormData()
        data.add_field("target_id", target_id)
        data.add_field("reporter_id", str(interaction.user.id))
        data.add_field("cheat", cheat)
        
        # We need to pass evidence as a file-like object or bytes with filename
        data.add_field("evidence", file_bytes, filename=evidence.filename, content_type=evidence.content_type)
        
        headers = {
            "x-api-key": "lucas_secret_api_key_1337"
        }
        
        url = "http://localhost:3000/api/reports"
        
        session = bot.ai_http
        if not session:
            session = aiohttp.ClientSession()
            bot.ai_http = session

        async with session.post(url, data=data, headers=headers) as resp:
            if resp.status in (200, 201):
                await interaction.followup.send(f"✅ Successfully registered cheater `{target_id}`.")
            else:
                resp_text = await resp.text()
                await interaction.followup.send(f"❌ Failed to register cheater (HTTP {resp.status}):\n```\n{resp_text[:1000]}\n```")
    except Exception as e:
        await interaction.followup.send(f"❌ Could not reach the API: {e}")


def main() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise SystemExit(
            "Missing DISCORD_TOKEN. Copy .env.example to .env and set the token."
        )
    bot.run(token)


if __name__ == "__main__":
    main()
