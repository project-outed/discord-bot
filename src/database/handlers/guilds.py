from __future__ import annotations
from typing import Optional, Dict, Any, TYPE_CHECKING
from src.utils.console import Console
import json

if TYPE_CHECKING:
    from src.database.main import Database

class GuildsHandler:
    def __init__(self, db: "Database"):
        self.db = db
        self.table = "guilds"

    async def get_guild_settings(self, guild_id: int) -> Optional[Dict[str, Any]]:
        # Try to get from Redis first
        if self.db.redis:
            try:
                client = await self.db.redis.get_client()
                if client:
                    cached_data = await client.get(f"guild_settings:{guild_id}")
                    if cached_data:
                        return json.loads(cached_data)
            except Exception as e:
                Console.error(f"Failed to fetch guild settings from Redis for {guild_id}: {e}", module="REDIS")

        query = f"SELECT alert_channel, alert_role FROM {self.table} WHERE guild_id = $1"
        try:
            settings = await self.db.fetch(query, guild_id, fetch_one=True)
            if settings and self.db.redis:
                try:
                    client = await self.db.redis.get_client()
                    if client:
                        await client.setex(
                            f"guild_settings:{guild_id}",
                            3600,
                            json.dumps(settings)
                        )
                except Exception as e:
                    Console.error(f"Failed to cache guild settings in Redis for {guild_id}: {e}", module="REDIS")
            
            return settings
        except Exception as e:
            Console.error(f"Failed to fetch guild settings for {guild_id}: {e}", module="DATABASE")
            return None
    async def update_guild_settings(self, guild_id: int, **settings) -> bool:
        if not settings:
            return False

        # Ensure ID fields are integers if passed as strings
        id_fields = ['alert_channel', 'alert_role']
        for field in id_fields:
            if field in settings and isinstance(settings[field], str):
                try:
                    settings[field] = int(settings[field])
                except ValueError:
                    pass

        keys = list(settings.keys())
        values = list(settings.values())
        
        # Build UPDATE query: SET key1=$2, key2=$3 WHERE guild_id=$1
        set_clause = ", ".join([f"{key} = ${i+2}" for i, key in enumerate(keys)])
        query = f"UPDATE {self.table} SET {set_clause} WHERE guild_id = $1"
        
        try:
            # Update Database
            await self.db.execute(query, guild_id, *values)
            
            # Invalidate Redis cache
            if self.db.redis:
                try:
                    client = await self.db.redis.get_client()
                    if client:
                        await client.delete(f"guild_settings:{guild_id}")
                except Exception as e:
                    Console.error(f"Failed to invalidate Redis cache for {guild_id}: {e}", module="REDIS")
            
            return True
        except Exception as e:
            Console.error(f"Failed to update guild settings for {guild_id}: {e}", module="DATABASE")
            return False
