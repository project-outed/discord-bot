from typing import List, Dict, Any
import json
from src.utils.console import Console

class TranscriptHandler:
    def __init__(self, db):
        self.db = db
        self.table = "transcript"

    async def save_message(self, channel_id: int, message_id: int, author_id: int, author_tag: str, content: str, attachments: List[Dict[str, str]] = None) -> bool:
        query = f"""
            INSERT INTO {self.table} (channel_id, message_id, author_id, author_tag, content, attachments)
            VALUES ($1, $2, $3, $4, $5, $6)
        """
        try:
            attachments_json = json.dumps(attachments) if attachments else None
            await self.db.execute(query, channel_id, message_id, author_id, author_tag, content, attachments_json)
            return True
        except Exception as e:
            Console.error(f"Failed to save message to transcript: {e}", "DATABASE")
            return False

    async def get_transcript(self, channel_id: int) -> List[Dict[str, Any]]:
        query = f"""
            SELECT * FROM {self.table} WHERE channel_id = $1 ORDER BY created_at ASC
        """
        return await self.db.fetch(query, channel_id)
    
    async def delete_transcript(self, channel_id: int) -> bool:
        query = f"""
            DELETE FROM {self.table} WHERE channel_id = $1
        """
        return await self.db.execute(query, channel_id) > 0