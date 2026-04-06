import discord
from discord import ui
import json
from datetime import datetime
from src.bot.ui.messages.ticket.close_ticket import CloseTicketView
from src.utils.console import Console

class TicketCloseReasonModal(ui.Modal, title="Close Ticket"):
    reason = ui.TextInput(
        label="Reason for closing",
        style=discord.TextStyle.paragraph,
        placeholder="Enter the reason for closing this ticket...",
        required=True,
        max_length=1000
    )

    def __init__(self, bot: discord.Client):
        super().__init__()
        self.bot = bot

    async def on_submit(self, interaction: discord.Interaction):
        Console.debug(f"TicketCloseReasonModal submitted by {interaction.user.id} in channel {interaction.channel.id}", module="TICKET")
        await interaction.response.defer(ephemeral=False)
        Console.debug("Interaction deferred successfully.", module="TICKET")
        
        ticket = await self.bot.db.tickets.get_ticket(interaction.channel.id)
        if not ticket:
            Console.debug("Cannot fetch ticket from DB.", module="TICKET")
            return await interaction.followup.send("This channel is not a ticket.", ephemeral=True)
            
        Console.debug("Revoking permissions for owner and added_users...", module="TICKET")
        users_to_revoke = [ticket['owner_id']]
        if ticket.get('added_users'):
            added = ticket['added_users']
            if isinstance(added, str):
                users_to_revoke.extend(json.loads(added))
            elif isinstance(added, list):
                users_to_revoke.extend(added)

        for user_id in users_to_revoke:
            member = interaction.guild.get_member(user_id)
            if member:
                await interaction.channel.set_permissions(member, send_messages=False, read_messages=True)

        Console.debug("Updating ticket status to closed...", module="TICKET")
        await self.bot.db.execute("UPDATE tickets SET status = 'closed' WHERE channel_id = $1", interaction.channel.id)
        
        Console.debug("Fetching user trust score...", module="TICKET")
        user_data = await self.bot.db.fetch("SELECT trust_score FROM public.users WHERE user_id = $1", interaction.user.id, fetch_one=True)
        trust_score_val = str(user_data['trust_score']) if user_data else "N/A"
        
        Console.debug("Instantiating CloseTicketView...", module="TICKET")
        view = CloseTicketView(
            data={
                "username": str(interaction.user.display_name),
                "platform_id": str(interaction.user.id),
                "trust_score": trust_score_val,
                "avatar": interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url,
                "category": ticket.get("ticket_type", "N/A"),
                "created_at": ticket.get("created_at", "N/A"),
                "reason": self.reason.value,
                "closed_by": str(interaction.user.display_name),
                "closed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            bot=self.bot
        )
        
        Console.debug("Sending CloseTicketView HTTP request...", module="TICKET")
        try:
            await interaction.followup.send(
                view=view,
                files=[discord.File("images/banners/banner.webp", filename="banner_channel.webp")]
            )
            Console.debug("CloseTicketView sent successfully.", module="TICKET")
        except Exception as e:
            Console.error(f"Failed to send CloseTicketView: {e}")
            import traceback
            traceback.print_exc()
