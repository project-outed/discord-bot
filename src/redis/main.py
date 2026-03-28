import os
import redis.asyncio as redis
from src.utils.console import Console

class Redis:
    def __init__(self):
        self.client = None
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", 6379))
        self.db = int(os.getenv("REDIS_DB", 0))
    
    async def connect(self):
        try:
            self.client = redis.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                password=os.getenv("REDIS_PASS", None) or None,
                db=int(os.getenv("REDIS_DB", 0)),
                decode_responses=True
            )
            
            await self.client.ping()
            return self.client
        except Exception as e:
            Console.error(f"Failed to establish Redis connection: {e}", "REDIS")
            self.client = None
            return None

    async def close(self):
        try:
            if self.client:
                await self.client.close()
                Console.info("Redis connection closed successfully", "REDIS")
                self.client = None
        except Exception as e:
            Console.error(f"Error while closing Redis connection: {e}", "REDIS")

    async def get_client(self) -> redis.Redis:
        if self.client is None:
            await self.connect()
        return self.client
