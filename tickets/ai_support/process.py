import json
import os
from typing import Any

import aiohttp
import discord
from discord.ext import commands

import ids

from .prompt import OUTED_SYSTEM_PROMPT


def _ai_channel_id_set() -> frozenset[int]:
    out: set[int] = set(ids.AI_SUPPORT_CHANNEL_IDS)
    raw = os.getenv("AI_CHANNEL_IDS_EXTRA", "").strip()
    for part in raw.split(","):
        p = part.strip()
        if p.isdigit():
            out.add(int(p))
    return frozenset(out)


def ai_channel_ids_for_debug() -> tuple[int, ...]:
    return tuple(sorted(_ai_channel_id_set()))


def resolve_category_id(channel: discord.abc.GuildChannel | discord.Thread) -> int | None:
    if isinstance(channel, discord.Thread):
        parent = channel.parent
        return parent.category_id if parent else None
    return channel.category_id


def channel_is_ai_support(channel: discord.abc.GuildChannel | discord.Thread) -> bool:
    if getattr(channel, "id", None) == 1487186775729504280:
        return False
    cat = resolve_category_id(channel)
    if cat == ids.AI_SUPPORT_CATEGORY_ID:
        return True
    whitelist = _ai_channel_id_set()
    if not whitelist:
        return False
    if channel.id in whitelist:
        return True
    if isinstance(channel, discord.Thread):
        pid = channel.parent_id
        if pid is not None and pid in whitelist:
            return True
    return False


def _parse_ai_response(data: Any) -> str:
    if isinstance(data, dict):
        choices = data.get("choices")
        if isinstance(choices, list) and choices:
            c0 = choices[0]
            if isinstance(c0, dict):
                msg = c0.get("message")
                if isinstance(msg, dict) and msg.get("content"):
                    return str(msg["content"]).strip()
                if c0.get("text"):
                    return str(c0["text"]).strip()
        for key in ("response", "message", "output", "text", "content", "reply"):
            v = data.get(key)
            if isinstance(v, str) and v.strip():
                return v.strip()
    return ""


def _chunk_send(text: str, size: int = 1990) -> list[str]:
    if not text:
        return []
    return [text[i : i + size] for i in range(0, len(text), size)]


OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"


async def _complete_chat(
    session: aiohttp.ClientSession,
    *,
    url: str,
    headers: dict[str, str],
    payload: dict[str, Any],
) -> tuple[int, str, dict[str, Any] | None]:
    async with session.post(
        url,
        json=payload,
        headers=headers,
        timeout=aiohttp.ClientTimeout(total=120),
    ) as resp:
        raw = await resp.read()
        data: dict[str, Any] | None = None
        try:
            data = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            pass
        text_out = raw.decode("utf-8", errors="replace").strip()
        if data is not None:
            parsed = _parse_ai_response(data)
            if parsed:
                text_out = parsed
        return resp.status, text_out, data


async def handle_ai_support_message(
    bot: commands.Bot,
    message: discord.Message,
    *,
    http: aiohttp.ClientSession,
) -> None:
    text = (message.content or "").strip()
    if not text:
        await message.channel.send(
            "Skriv dit spørgsmål som almindelig tekst. "
            "(Hvis du allerede gjorde det: slå **Message Content Intent** til for botten i Discord Developer Portal og genstart botten.)"
        )
        return
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not openai_key:
        await message.channel.send(
            "AI support is not configured (missing OPENAI_API_KEY)."
        )
        return
    collected: list[dict[str, str]] = []
    try:
        async for msg in message.channel.history(limit=25, oldest_first=True):
            if msg.author.bot and msg.author.id != bot.user.id:
                continue
            part = (msg.content or "").strip()
            if not part:
                continue
            role = "assistant" if msg.author.id == bot.user.id else "user"
            collected.append({"role": role, "content": part})
    except discord.HTTPException:
        collected = [{"role": "user", "content": text}]
    else:
        if not collected:
            collected = [{"role": "user", "content": text}]
    messages = [{"role": "system", "content": OUTED_SYSTEM_PROMPT}] + collected[-20:]
    try:
        async with message.channel.typing():
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"
            status, reply, data = await _complete_chat(
                http,
                url=OPENAI_CHAT_URL,
                headers={
                    "Authorization": f"Bearer {openai_key}",
                    "Content-Type": "application/json",
                },
                payload={"model": model, "messages": messages},
            )
            if isinstance(data, dict) and data.get("error"):
                err = data["error"]
                detail = err.get("message", str(err)) if isinstance(err, dict) else str(err)
                await message.channel.send(f"OpenAI error (HTTP {status}): {detail[:500]}")
                return
            if not reply:
                await message.channel.send(
                    f"No reply text from the AI (HTTP {status})."
                )
                return
            if status >= 400:
                await message.channel.send(
                    f"AI error (HTTP {status}). First part of reply:\n{reply[:500]}"
                )
                return
    except (aiohttp.ClientError, TimeoutError, OSError) as e:
        await message.channel.send(f"Could not reach the AI: {e!s}")
        return
    chunks = _chunk_send(reply)
    for i, piece in enumerate(chunks):
        try:
            if i == 0:
                await message.reply(piece, mention_author=False)
            else:
                await message.channel.send(piece)
        except discord.HTTPException:
            await message.channel.send(piece)
