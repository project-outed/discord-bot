from __future__ import annotations
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from src.utils.console import Console

if TYPE_CHECKING:
    from src.database.main import Database

class ReportsHandler:
    def __init__(self, db: "Database"):
        self.db = db
        self.table = "reports"

    async def has_accepted_report(self, user_id: int) -> bool:
        query = f"SELECT count(*) FROM {self.table} WHERE target_user_id = $1 AND status = 'accepted'"
        try:
            result = await self.db.fetch(query, user_id, fetch_one=True)
            if result and result.get('count', 0) > 0:
                return True
            return False
        except Exception as e:
            Console.error(f"Failed to check reports in DB: {e}")
            return False

    async def get_accepted_reports(self, user_id: int) -> List[Dict[str, Any]]:
        query = f"SELECT * FROM {self.table} WHERE target_user_id = $1 AND status = 'accepted'"
        try:
            return await self.db.fetch(query, user_id)
        except Exception as e:
            Console.error(f"Failed to fetch reports from DB: {e}")
            return []
