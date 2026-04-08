import os
import discord
from discord.ext import commands
from discord import app_commands

from src.utils.console import Console
from src.utils.permission import Permission

class Remove(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.guilds(int(os.getenv("MAIN_GUILD")))
    @app_commands.command(name="remove", description="Remove a user from the ticket")
    async def remove(self, interaction: discord.Interaction, user: discord.Member):
        permission_ids = Permission().get_permission(config=os.path.join("data", "tickets", "config.json"))
        access = Permission(user=interaction.user, ids=permission_ids['permission'][0]).role()

        if not access:
            return await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)

        await interaction.response.defer(ephemeral=False)
        ticket = await self.bot.db.tickets.get_ticket(interaction.channel.id)
        if not ticket:
            return await interaction.followup.send("This channel is not a ticket.", ephemeral=True)
            
        if user.id == ticket['owner_id']:
            return await interaction.followup.send("You cannot remove the owner of the ticket.", ephemeral=True)

        added_users = ticket.get('added_users') or []
        if isinstance(added_users, str):
            try:
                import json
                added_users = json.loads(added_users)
            except:
                added_users = []
        
        added_user_ids = [str(uid) for uid in added_users]
        target_id = str(user.id)
        
        if target_id not in added_user_ids:
            return await interaction.followup.send(f"The user is not in the ticket. Registered IDs: `{added_user_ids}`", ephemeral=True)


            
        data = await self.bot.db.fetch("SELECT trust_score FROM users WHERE user_id = $1", user.id, fetch_one=True)
        if not data:
            return await interaction.followup.send("User not found in database.", ephemeral=True)
        
        success = await self.bot.db.tickets.remove_user(interaction.channel.id, user.id)
        if success:
            await interaction.channel.set_permissions(user, overwrite=None)
            
            from src.bot.ui.messages.ticket.remove_user import RemoveUserView
            await interaction.followup.send(
                view=RemoveUserView(data={
                    "username": str(user.display_name),
                    "platform_id": str(user.id),
                    "trust_score": str(data['trust_score']),
                    "avatar": user.avatar.url if user.avatar else user.default_avatar.url
                })
            )
        else:
            await interaction.followup.send("User is not in the ticket or an error occurred.", ephemeral=True)