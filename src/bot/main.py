import discord
from discord.ext import commands

from src.database.main import Database
from src.websocket.main import WebSocket
from src.redis.main import Redis

from src.utils.console import Console

class Bot(commands.Bot):
    def __init__(self, database: Database, redis: Redis, websocket: WebSocket):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        self.db = database
        self.redis = redis
        self.websocket = websocket
        
        super().__init__(command_prefix=".", intents=intents)

    async def close(self):
        Console.info("Initiating cleanup sequence...", "SHUTDOWN")
        
        tasks = []
        if self.db:
            tasks.append(self.db.close())
        if self.redis:
            tasks.append(self.redis.close())
        if self.websocket:
            tasks.append(self.websocket.stop())
            
        if tasks:
            import asyncio
            await asyncio.gather(*tasks, return_exceptions=True)
            
        await super().close()
        Console.success("All connections closed. Bot shut down.", "SHUTDOWN")
