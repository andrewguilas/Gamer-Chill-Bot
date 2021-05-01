import discord
from discord.ext import commands

from helper import create_embed, check_if_authorized
from constants import DELETE_RESPONSE_DELAY

class moderation(commands.Cog, description = "Server and member management commands for moderation."):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ["delete"], description = "Clears a set amount of text messages.", brief = "manage messages")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_messages = True))
    async def clear(self, context, amount: int = 1):
        response = await context.send(embed = create_embed({
            "title": f"Clearing {amount} messages...",
            "color": discord.Color.gold()
        }))

        try:
            deleted_messages_count = 0

            def check(context2):
                return context2.id != response.id

            deleted_messages = await context.channel.purge(limit = amount + 2, check = check)
            deleted_messages_count = len(deleted_messages) - 1

            await response.edit(embed = create_embed({
                "title": f"Deleted {deleted_messages_count} messages",
                "color": discord.Color.green()
            }), delete_after = DELETE_RESPONSE_DELAY)
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not delete {amount} messages",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

def setup(client):
    client.add_cog(moderation(client))