import discord
from discord.ext import commands

import os
import sys
from datetime import datetime

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

def is_guild_owner():
    def predicate(context):
        return context.guild and context.guild.owner_id == context.author.id
    return commands.check(predicate)

class bot(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.check_any(commands.is_owner(), is_guild_owner())
    async def execute(self, context, *, code):
        response = await context.send(embed = create_embed({
            "title": "Executing code...",
            "color": discord.Color.gold(),
        }, {
            "Code": code,
        }))

        try:
            exec(code)
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not execute code",
                "color": discord.Color.red(),
            }, {
                "Error Message": error_message,
                "Code": code,
            }))
        else:
            await response.edit(embed = create_embed({
                "title": "Code executed",
                "color": discord.Color.green(),
            }, {
                "Code": code,
            }))

    @commands.command(aliases = ["clearterminal", "clearscreen"])
    @commands.check_any(commands.is_owner())
    async def cls(self, context):
        response = await context.send(embed = create_embed({
            "title": "Clearing terminal",
            "color": discord.Color.gold(),
        }))

        try:
            os.system("cls" if os.name == "nt" else "clear")
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not clear terminal",
                "color": discord.Color.red(),
            }, {
                "Error Message": error_message,
            }))
        else:
            await response.edit(embed = create_embed({
                "title": "Terminal cleared",
                "color": discord.Color.green(),
            }))

    @commands.command()
    @commands.check_any(commands.is_owner(), is_guild_owner())
    async def changeactivity(self, context, *, activity: str = ""):
        activity = activity.lower()

        response = await context.send(embed = create_embed({
            "title": "Changing the bot's activity",
            "color": discord.Color.gold(),
        }, {
            "Activity": activity or "None",
        }))

        try:
            await self.client.change_presence(activity = discord.Game(name = activity))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not change the bot's activity",
                "color": discord.Color.red(),
            }, {
                "Error Message": error_message,
                "Activity": activity or "None",
            }))
        else:
            await response.edit(embed = create_embed({
                "title": "Changed bot's activity",
                "color": discord.Color.green(),
            }, {
                "Activity": activity or "None",
            }))

    @commands.command()
    @commands.check_any(commands.is_owner(), is_guild_owner())
    async def changestatus(self, context, *, status: str = "online"):
        status = status.lower()

        response = await context.send(embed = create_embed({
            "title": f"Changing the bot's status to {status}",
            "color": discord.Color.gold(),
        }))

        try:
            await self.client.change_presence(status = discord.Status[status])
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not change the bot's status to {status}",
                "color": discord.Color.red(),
            }, {
                "Error Message": error_message,
            }))
        else:
            await response.edit(embed = create_embed({
                "title": f"Changed bot's status to {status}",
                "color": discord.Color.green(),
            }))

    @commands.command()
    @commands.check_any(commands.is_owner(), is_guild_owner())
    async def restart(self, context):
        await context.send(embed = create_embed({
            "title": "Restarting bot, no confirmation message after completion...",
            "color": discord.Color.gold(),
        }))
        sys.exit()

def setup(client):
    client.add_cog(bot(client))