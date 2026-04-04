import os
import json
import discord
from collections.abc import Iterable
from src.utils.console import Console

class Permission:
    def __init__(self, user: discord.User = None, ids=None):
        self.user = user

        if ids is None:
            self.ids = set()
        elif isinstance(ids, (str, int)):
            self.ids = {int(ids)}
        elif isinstance(ids, dict):
            self.ids = {int(v) for v in ids.values()}
        elif isinstance(ids, Iterable):
            self.ids = {int(i) for i in ids}
        else:
            self.ids = {int(ids)}

    def get_permission(self, config=None):
        if config and os.path.exists(config):
            with open(config, "r") as f:
                return json.load(f)
        return {}

    def role(self):
        try:
            member = self.user
            if not hasattr(member, "roles"):
                return False
                
            return any(role.id in self.ids for role in member.roles)
        except Exception as e:
            Console.error(f"Error checking permissions: {e}", "PERMISSION")
            return False