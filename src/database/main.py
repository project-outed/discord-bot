import aiomysql
import asyncio
import os

from src.utils.console import Console
from src.database.handlers.tickets import TicketHandler
from src.database.handlers.transcript import TranscriptHandler

class Database:
    def __init__(self):
        self.pool = None
        self.host = os.getenv("DATABASE_HOST")
        self.port = int(os.getenv("DATABASE_PORT", 5743))
        self.db_name = os.getenv("DATABASE_NAME")

        self.tickets = TicketHandler(self)
        self.transcripts = TranscriptHandler(self)
    
    async def connect(self):
        try:
            self.pool = await aiomysql.create_pool(
                host=self.host,
                port=self.port,
                user=os.getenv("DATABASE_USER"),
                password=os.getenv("DATABASE_PASS"),
                db=self.db_name,
                loop=asyncio.get_event_loop(),
                minsize=1,
                maxsize=10,
            )

            return self.pool
        except Exception as e:
            Console.error(f"Failed to connect to database: {e}", module="Database")
    

    async def close(self):
        try:
            if self.pool.closed:    
                return
            
            self.pool.close()
            await self.pool.wait_closed()
            Console.info("Closed database connection successfully", module="Database")
        except Exception as e:
            Console.error(f"Failed to close database connection: {e}", module="Database")
    
    async def getPool(self):
        if self.pool is None:
            await self.connect()
        return self.pool

    async def execute(self, query: str, *args) -> int:
        pool = await self.getPool()
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, args)
                await conn.commit()
                return cur.rowcount

    async def fetch(self, query: str, *args, fetch_one=False):
        pool = await self.getPool()
        async with pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(query, args)
                if fetch_one:
                    return await cur.fetchone()
                return await cur.fetchall()