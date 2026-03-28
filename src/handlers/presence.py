import discord
import itertools
from discord.ext import tasks

bot: discord.Client = None

presence_messages = [
    "🌐 Secured by Outed.dev",
    "📁 Managing {guild_count} active servers",
    "⚡ Powered by High-Speed Infrastructure",
]

_cycle = itertools.cycle(presence_messages)

@tasks.loop(minutes=5)
async def Presence():    
    if bot is None or not bot.is_ready():
        return

    raw_message = next(_cycle)
    
    message = raw_message.format(
        guild_count=len(bot.guilds)
    )

    try:
        await bot.change_presence(
            activity=discord.CustomActivity(name=message),
            status=discord.Status.online
        )
    except Exception as e:
        print(f"Error updating presence: {e}")
