import os
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

    async def setup_hook(self) -> None:
        self.ai_http = aiohttp.ClientSession()
        if not os.getenv("OPENAI_API_KEY", "").strip():
            print(
                "WARNING: OPENAI_API_KEY mangler i .env — AI support kan ikke svare."
            )
        await self.tree.sync()

    async def close(self) -> None:
        if self.ai_http and not self.ai_http.closed:
            await self.ai_http.close()
            self.ai_http = None
        await super().close()

    async def on_message(self, message: discord.Message) -> None:
        await self.process_commands(message)
        if message.author.bot:
            return
        if not message.guild:
            return
        ch = message.channel
        if not isinstance(ch, (discord.abc.GuildChannel, discord.Thread)):
            return
        if not channel_is_ai_support(ch):
            return
        if self.ai_http is None:
            return
        await handle_ai_support_message(self, message, http=self.ai_http)

    async def on_ready(self) -> None:
        print(f"Logget ind som {self.user} (id: {self.user.id})")
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


@bot.tree.command(name="ping", description="Tjek at botten svarer")
async def ping(interaction: discord.Interaction) -> None:
    await interaction.response.send_message("Pong!")


@bot.tree.command(
    name="ai_debug",
    description="Vis kanal- og kategori-ID (brug til at matche ids.py)",
)
async def ai_debug(interaction: discord.Interaction) -> None:
    if not interaction.guild or not isinstance(
        interaction.channel, (discord.abc.GuildChannel, discord.Thread)
    ):
        await interaction.response.send_message(
            "Kun i en server-kanal.", ephemeral=True
        )
        return
    ch = interaction.channel
    cat_id = _debug_category_id(ch)
    match = channel_is_ai_support(ch)
    await interaction.response.send_message(
        f"**channel_id:** `{ch.id}`\n"
        f"**category_id (løst):** `{cat_id}`\n"
        f"**ids.py — AI_SUPPORT_CATEGORY_ID:** `{ids.AI_SUPPORT_CATEGORY_ID}`\n"
        f"**Kanal-ID whitelist (ids.py + AI_CHANNEL_IDS_EXTRA):** `{ai_channel_ids_for_debug()}`\n"
        f"**Botten behandler denne kanal som AI-support:** {'ja' if match else 'nej'}\n"
        f"Hvis **nej**: sæt rigtigt kanal-ID i `ids.py` eller tilføj det i `.env` som "
        f"`AI_CHANNEL_IDS_EXTRA=1234567890123456789` (kommasepareret). "
        f"Giv botten **Read Message History** + **Send Messages** i kanalen.",
        ephemeral=True,
    )


from discord import app_commands

@bot.tree.command(name="clearchat", description="Slet beskeder i kanalen (Kun for Management)")
@app_commands.describe(amount="Antal beskeder der skal slettes (standard: 100)")
async def clearchat(interaction: discord.Interaction, amount: int = 100) -> None:
    has_permission = False
    if interaction.user.id == ids.MANAGEMENT_ID:
        has_permission = True
    elif hasattr(interaction.user, 'roles'):
        if any(r.id == ids.MANAGEMENT_ID for r in interaction.user.roles):
            has_permission = True
            
    if not has_permission:
        await interaction.response.send_message("Du har ikke tilladelse til at bruge denne kommando.", ephemeral=True)
        return
        
    await interaction.response.defer(ephemeral=True)
    
    if not hasattr(interaction.channel, "purge"):
        await interaction.followup.send("Kan ikke slette beskeder i denne type kanal.", ephemeral=True)
        return
        
    try:
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"✅ Slettede {len(deleted)} beskeder.", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("❌ Jeg har ikke tilladelse til at slette beskeder her. Tjek mine 'Manage Messages' rettigheder.", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.followup.send(f"❌ Fejl under sletning: {e}", ephemeral=True)


def main() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise SystemExit(
            "Mangler DISCORD_TOKEN. Kopiér .env.example til .env og sæt token."
        )
    bot.run(token)


if __name__ == "__main__":
    main()
