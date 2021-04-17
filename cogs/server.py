import discord
from discord.ext import commands
import re

def create_embed(info: {} = {}, fields: {} = {}):
    embed = discord.Embed(
        title = info.get("title") or "",
        description = info.get("description") or "",
        colour = info.get("color") or discord.Color.blue(),
        url = info.get("url") or "",
    )

    for name, value in fields.items():
        embed.add_field(name = name, value = value, inline = info.get("inline") or False)

    if info.get("author"):
        embed.set_author(name = info.author.name, url = info.author.mention, icon_url = info.author.avatar_url)
    if info.get("footer"):
        embed.set_footer(text = info.footer)
    if info.get("image"):
        embed.set_image(url = info.url)
    if info.get("thumbnail"):
        embed.set_thumbnail(url = info.thumbnail)
    
    return embed

def sort_dictionary(dict: {}):
    sorted_dictionary = {}
    sorted_keys = sorted(dict, key = dict.get, reverse = True)

    for key in sorted_keys:
        sorted_dictionary[key] = dict[key]
        
    return sorted_dictionary

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

            members = sort_dictionary(members)

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