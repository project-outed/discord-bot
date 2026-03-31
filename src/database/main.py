import asyncpg
import asyncio
import os
import json

from src.utils.console import Console
from src.database.handlers.tickets import TicketHandler
from src.database.handlers.transcript import TranscriptHandler

class Database:
    def __init__(self):
        self.pool = None
        self.host = os.getenv("DATABASE_HOST")
        self.port = int(os.getenv("DATABASE_PORT", 5432))
        self.db_name = os.getenv("DATABASE_NAME", "postgres")
        self.user = os.getenv("DATABASE_USER", "postgres")
        self.password = os.getenv("DATABASE_PASS")


        self.tickets = TicketHandler(self)
        self.transcripts = TranscriptHandler(self)
    
    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.db_name,
                min_size=1,
                max_size=10,
                ssl='require'
            )

            return self.pool
        except Exception as e:
            Console.error(f"Failed to connect to PostgreSQL: {e}", module="DATABASE")
    

    async def close(self):
        try:
            if self.pool:
                await self.pool.close()
                Console.info("Closed PostgreSQL connection successfully", module="DATABASE")
        except Exception as e:
            Console.error(f"Failed to close PostgreSQL connection: {e}", module="DATABASE")
    
    async def getPool(self):
        if self.pool is None:
            await self.connect()
        return self.pool

    async def execute(self, query: str, *args) -> int:
        pool = await self.getPool()
        async with pool.acquire() as conn:
            # asyncpg returns a status string like "DELETE 1" or "UPDATE 5"
            status = await conn.execute(query, *args)
            try:
                # The count is usually the last word in the status string
                return int(status.split()[-1])
            except (ValueError, IndexError):
                return 0

    async def fetch(self, query: str, *args, fetch_one=False):
        pool = await self.getPool()
        async with pool.acquire() as conn:
            if fetch_one:
                row = await conn.fetchrow(query, *args)
                return dict(row) if row else None
            
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]