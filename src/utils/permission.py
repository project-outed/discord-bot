
from collections.abc import Iterable
from src.utils.console import Console

class Permission:
    def __init__(self, user, ids):
        self.user = user
        if isinstance(ids, dict):
            ids = ids.values()
        
        if isinstance(ids, Iterable) and not isinstance(ids, (str, bytes)):
            self.ids = {set(i) for i in ids}
        else:
            self.ids = {set(ids)}
    

    def role(self):
        try:    
            roles = getattr(getattr(self.user, "guild", None), "roles", [])
            return any(any(role.id == id for role in roles) for id in self.ids)
        except Exception as e:
            Console.error(
                f"Error checking role permission for user {getattr(self.user, 'id', 'UNKNOWN')} "
                f"in guild {getattr(getattr(self.user, 'guild', None), 'id', 'UNKNOWN')}: {e}",
                "PERMISSION"
            )
            return False