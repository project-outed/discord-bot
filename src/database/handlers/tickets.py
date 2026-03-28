from __future__ import annotations
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from src.utils.console import Console

if TYPE_CHECKING:
    from src.database.main import Database

class TicketHandler:
    def __init__(self, db: "Database"):
        self.db = db
        self.table = "tickets"

    async def create_table(self):
        query = f"""
        CREATE TABLE IF NOT EXISTS {self.table} (
            channel_id BIGINT PRIMARY KEY,
            guild_id BIGINT NOT NULL,
            owner_id BIGINT NOT NULL,
            ticket_type VARCHAR(50) NOT NULL,
            claimed_by BIGINT DEFAULT NULL,
            status ENUM('open', 'closed') DEFAULT 'open',
            added_users JSON DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        await self.db.execute(query)
        Console.info(f"Ensured database table '{self.table}' exists.")

    async def create_ticket(self, channel_id: int, guild_id: int, owner_id: int, ticket_type: str) -> bool:
        query = f"INSERT INTO {self.table} (channel_id, guild_id, owner_id, ticket_type) VALUES (%s, %s, %s, %s)"
        try:
            await self.db.execute(query, channel_id, guild_id, owner_id, ticket_type)
            return True
        except Exception as e:
            Console.error(f"Failed to create ticket in DB: {e}")
            return False

    async def delete_ticket(self, channel_id: int) -> bool:
        query = f"DELETE FROM {self.table} WHERE channel_id = %s"
        return await self.db.execute(query, channel_id) > 0

    async def get_ticket(self, channel_id: int) -> Optional[Dict[str, Any]]:
        query = f"SELECT * FROM {self.table} WHERE channel_id = %s"
        return await self.db.fetch(query, channel_id, fetch_one=True)

    async def add_user(self, channel_id: int, user_id: int) -> bool:
        ticket = await self.get_ticket(channel_id)
        if not ticket: return False
        
        import json
        users = json.loads(ticket['added_users']) if ticket['added_users'] else []
        if user_id not in users:
            users.append(user_id)
            query = f"UPDATE {self.table} SET added_users = %s WHERE channel_id = %s"
            await self.db.execute(query, json.dumps(users), channel_id)
            return True
        return False

    async def remove_user(self, channel_id: int, user_id: int) -> bool:
        ticket = await self.get_ticket(channel_id)
        if not ticket: return False
        
        import json
        users = json.loads(ticket['added_users']) if ticket['added_users'] else []
        if user_id in users:
            users.remove(user_id)
            query = f"UPDATE {self.table} SET added_users = %s WHERE channel_id = %s"
            await self.db.execute(query, json.dumps(users), channel_id)
            return True
        return False

    async def switch_owner(self, channel_id: int, new_owner_id: int) -> bool:
        query = f"UPDATE {self.table} SET owner_id = %s WHERE channel_id = %s"
        return await self.db.execute(query, new_owner_id, channel_id) > 0

    async def switch_category(self, channel_id: int, new_type: str) -> bool:
        query = f"UPDATE {self.table} SET ticket_type = %s WHERE channel_id = %s"
        return await self.db.execute(query, new_type, channel_id) > 0

    async def claim_ticket(self, channel_id: int, staff_id: int) -> bool:
        query = f"UPDATE {self.table} SET claimed_by = %s WHERE channel_id = %s"
        return await self.db.execute(query, staff_id, channel_id) > 0

    async def unclaim_ticket(self, channel_id: int) -> bool:
        query = f"UPDATE {self.table} SET claimed_by = NULL WHERE channel_id = %s"
        return await self.db.execute(query, channel_id) > 0