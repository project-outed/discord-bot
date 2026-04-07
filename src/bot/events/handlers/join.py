import os
import json
import discord
from discord.ext import commands
from src.utils.console import Console

class JoinEvent(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.__load_config()

    def __load_config(self):
        config_path = os.path.join("data", "config.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
        return {}

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        try:
            self.config = self.__load_config()

            expose_query = "SELECT id FROM reports WHERE target_user_id = $1 AND status = 'accepted'"
            exposed_rows = await self.bot.db.fetch(expose_query, int(member.id), fetch_one=True)

            if exposed_rows:
                role_id = self.config['expose']['role_id']
                if role_id:
                    role = member.guild.get_role(int(role_id))
                    if role:
                        await member.add_roles(role, reason="Exposed user re-joined")
                        Console.info(f"Re-assigned exposed role to {member.name}", "JOIN")

            user_query = "SELECT 1 FROM users WHERE user_id = $1"
            verified_data = await self.bot.db.fetch(user_query, int(member.id), fetch_one=True)
            
            if verified_data:
                role_id = self.config['verification']['role_id']
                if role_id:
                    role = member.guild.get_role(int(role_id))
                    if role:
                        await member.add_roles(role, reason="Verified user re-joined")
                        Console.info(f"Re-assigned verified role to {member.name}", "JOIN")

        except Exception as e:
            Console.error(f"Failed to check joining member {member.id}: {e}", "JOIN")
