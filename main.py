import asyncio

from src.bot.main import Bot
from src.utils.console import Console

from src.database.main import Database
from src.websocket.main import WebSocket
from src.redis.main import Redis
from src.bot.commands.main import CommandManager
from src.bot.events.main import EventManager

import src.handlers.presence as presence

import os
from dotenv import load_dotenv
load_dotenv()

database: Database = Database()
websocket: WebSocket = WebSocket()
redis: Redis = Redis()

command_manager: CommandManager = CommandManager()
events_manager: EventManager = EventManager()

bot = Bot(database=database, redis=redis, websocket=websocket)
presence.bot = bot
command_manager.bot = bot
events_manager.bot = bot

@bot.event
async def on_ready():
    try:
        await bot.wait_until_ready()

        if database:
            pool = await database.connect()
            if pool:
                Console.success(f'Connected to database: "{os.getenv("DATABASE_NAME")}" (IP: {os.getenv("DATABASE_HOST")})', "DATABASE")
        
        if redis:
            await redis.connect()
            Console.success(f'Connected to redis: "{os.getenv("REDIS_HOST")}" (Port: {os.getenv("REDIS_PORT")})', "REDIS")

        if websocket:
            asyncio.create_task(websocket.start())
            Console.success(f'Connected to websocket: "ws://{os.getenv("WEBSOCKET_HOST")}:{os.getenv("WEBSOCKET_PORT")}" (Path: {os.getenv("WEBSOCKET_PATH")})', "WEBSOCKET")

        Console.success(f'Connected to "{bot.user.name}" (ID: {bot.user.id})', "BOT")
        if not presence.Presence.is_running():
            presence.Presence.start()
            Console.info("Presence rotation task started.", "PRESENCE")

        await command_manager.load()
        await events_manager.load()

        Console.success("All startup tasks completed successfully", "STARTUP")
    except Exception as e:
        Console.error(f"An unexpected error occurred during startup: {e}", "STARTUP")

if __name__ == "__main__":
    try:
        bot.run(os.getenv("BOT_TOKEN"), log_handler=None)
    except KeyboardInterrupt:
        pass
