import discord
from discord.ext import commands
import re

from helper import create_embed, sort_dictionary

class server(commands.Cog, description = "Server stats."):
    def __init__(self, client):
        self.client = client

    @commands.command(description = "Lists the top messagers in the server.")
    async def messageleaderboard(self, context):
        response = await context.send(embed = create_embed({
            "title": "Loading message leaderboard...",
            "color": discord.Color.gold()
        }))

        try:
            members = {}
            for channel in context.guild.text_channels:
                messages = await channel.history().flatten()
                for message in messages:
                    author_name = message.author.name
                    if not members.get(author_name):
                        members[author_name] = 1
                    else:
                        members[author_name] += 1

            members = sort_dictionary(members, True)

            await response.edit(embed = create_embed({
                "title": "Message Leaderboard"
            }, members))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not load message leaderboard",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

def setup(client):
    client.add_cog(server(client))