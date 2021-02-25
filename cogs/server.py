import discord
from discord.ext import commands
from discord import Color as discord_color

import pytz
from datetime import datetime

def create_embed(title, color = discord_color.blue(), fields = {}):
    embed = discord.Embed(
        title = title,
        colour = color or discord_color.blue()
    )

    for name, value in fields.items():
        embed.add_field(
            name = name,
            value = value,
            inline = False
        )

    embed.timestamp = datetime.now(tz = pytz.timezone("US/Eastern"))

    return embed

class server(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_webhooks = True))
    async def clearwebhooks(self, context, channel: discord.TextChannel = None):
        webhooks = await context.channel.webhooks()
        count = len(webhooks)
        
        if not channel:
            channel = context.channel

        if count == 0:
            await context.send(embed = create_embed(f"Success: There are no webhooks to delete in #{channel}", discord_color.green(), {
                "Webhooks": str(webhooks),
                "Channel": channel.mention,
            }))
            return

        embed = create_embed(f"Success: {count} webhooks were deleted in #{channel}", discord_color.green(), {
            "Webhooks": str(webhooks),
            "Channel": channel.mention,
        })

        try:
            for webhook in webhooks:
                await webhook.delete()
        except Exception as error_message:
            current_webhooks = await channel.webhooks()
            await context.send(embed = create_embed(f"Error: Something went wrong with deleting the webhooks in #{channel}", discord_color.red(), {
                "Webhooks": str(webhooks),
                "Amount Deleted": current_webhooks / count,
                "Channel": channel.mention,
                "Error Message": error_message,
            }))
        else:
            await context.send(embed = embed)

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_webhooks = True))
    async def listwebhooks(self, context, channel: discord.TextChannel = None):
        if (not channel):
            channel = context.channel

        webhooks = await channel.webhooks()
        await context.send(embed = create_embed(f"There are {len(webhooks)} webhooks in #{channel}", None, {
            "Webhooks": str(webhooks),
            "Channel": channel.mention
        }))   

def setup(client):
    client.add_cog(server(client))