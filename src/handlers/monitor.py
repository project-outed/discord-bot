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

		try:
			channel = self.bot.get_channel(int(channel_id)) or await self.bot.fetch_channel(int(channel_id))
		except (discord.NotFound, discord.Forbidden):
			Console.error(f"Channel with ID {channel_id} not found or inaccessible.", module="MONITOR")
			return
		except Exception as e:
			Console.error(f"Error fetching channel: {e}", module="MONITOR")
			return

		target_user_id = data.get("target_user_id")
		if not target_user_id or str(target_user_id).lower() == "unknown":
			Console.error("Invalid target_user_id provided in report data.", module="MONITOR")
			return

		try:
			user = await self.bot.fetch_user(int(target_user_id))
		except discord.NotFound:
			Console.error(f"User with ID {target_user_id} not found.", module="MONITOR")
			return
		except Exception as e:
			Console.error(f"Error fetching user {target_user_id}: {e}", module="MONITOR")
			return

		guild_id = os.getenv("MAIN_GUILD")
		if guild_id:
			try:
				guild = self.bot.get_guild(int(guild_id)) or await self.bot.fetch_guild(int(guild_id))
				if guild:
					role_id = self.config['expose'].get('role_id')
					if role_id:
						role = guild.get_role(int(role_id))
						if role:
							try:
								member = guild.get_member(user.id) or await guild.fetch_member(user.id)
								await member.add_roles(role, reason="User has been exposed")
							except discord.NotFound:
								pass
							except discord.Forbidden:
								Console.warning(f"Bot lacks permissions to add role to {user.display_name} ({user.id}).", module="MONITOR")
							except Exception as e:
								Console.error(f"Error adding role to {user.id}: {e}", module="MONITOR")
			except Exception as e:
				Console.error(f"Error processing guild/role: {e}", module="MONITOR")

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