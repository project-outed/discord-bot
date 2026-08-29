import os
import json
import discord
from collections.abc import Iterable
from src.utils.console import Console

CONFIGUREATION_PATH = ("", "", "")


class CommandPermissions:
    def __init__(self, user: discord.User):
        self.user = user
        self.config = os.e

    def access(command: str):
        if not command:
            Console.error("Couldn't check command permissions: command name missing.", module="CMD PERMISSIONS")
            return
        
