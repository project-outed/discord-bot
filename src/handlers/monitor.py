import asyncio
import os
import json
import discord

from src.utils.console import Console
from src.bot.ui.messages.expose.expose import ExposeView

bot: discord.Client = None

class Monitor:	
	def __init__(self):
		self.bot = bot
		self.config = self.__load_config()

	def __load_config(self):
		configPath = os.path.join("data", "config.json")
		with open(configPath, "r") as f:
			data = json.load(f)
			return data
		
	async def sendReport(self, data: dict):
		channel_id = self.config['expose']['channel_id']
		if not channel_id:
			Console.warning("No channel ID configured for expose reports.", module="MONITOR")
			return

		channel = self.bot.get_channel(int(channel_id)) or await self.bot.fetch_channel(int(channel_id))
		if not channel:
			Console.error(f"Channel with ID {channel_id} not found.", module="MONITOR")
			return
		

		user = await self.bot.fetch_user(int(data.get("target_user_id", 0)))

		guild_id = int(os.getenv("MAIN_GUILD"))
		guild = self.bot.get_guild(guild_id) or await self.bot.fetch_guild(guild_id)
		
		if guild:
			role_id = int(self.config['expose'].get('role_id', 0))
			role = guild.get_role(role_id)
			
			if role:
				member = guild.get_member(user.id) or await guild.fetch_member(user.id)
				if member:
					await member.add_roles(role, reason="User has been exposed")

		await channel.send(
            view=ExposeView(data={
				"target_username": user.display_name if user else "Unknown",
				"target_user_id": user.id if user else "Unknown",
				"cheat": data.get("reason", "No reason provided"),
				"game": data.get("game", "Unknown"),
				"trust_score": data.get("trust_score", "N/A"),
				"avatar_url": user.display_avatar.url if user else ""
			}),
        )
		
	async def websocketMessage(self, payload: dict):
		if payload.get("event") == str(self.config['expose']['websocket']['event']):
			data = payload.get("data", {})
			
			await self.sendReport(data={
				"target_user_id": data.get("target_user_id", "Unknown"),
				"reason": data.get("reason", "No reason provided"),
				"game": data.get("game", "Unknown"),
				"trust_score": data.get("trust_score", "N/A"),
			})