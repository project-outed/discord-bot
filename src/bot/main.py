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
        if self.db:
            await self.db.close()
            
        if self.redis:
            await self.redis.close()
            
        if self.websocket:
            await self.websocket.stop()
            
        await super().close()
