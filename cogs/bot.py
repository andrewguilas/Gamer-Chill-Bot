import discord
from discord import Color as discord_color
from discord.ext import commands

import math
import pytz
import os
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
            inline = True
        )

    embed.timestamp = datetime.now(tz = pytz.timezone("US/Eastern"))

    return embed

def is_guild_owner():
    def predicate(ctx):
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id
    return commands.check(predicate)

class bot(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.check_any(commands.is_owner(), is_guild_owner())
    async def execute(self, context, *, code):
        embed = create_embed("Executing Code", discord_color.gold(), {
            "Code": code,
        })
        embed.set_footer(text = f"#{context.channel}")
        embed.set_author(name = context.author, icon_url = context.author.avatar_url)
        await context.send(embed = embed)

        try:
            exec(code)
        except Exception as error_message:
            embed = create_embed(f"Error: Something went wrong when executing code", discord_color.red(), {
                "Error Message": str(error_message),
                "Code": code
            })
            embed.set_footer(text = f"#{context.channel}")
            embed.set_author(name = context.author, icon_url = context.author.avatar_url)
            await context.send(embed = embed)
        else:
            embed = create_embed(f"Success: Code was executed", discord_color.green(), {
                "Code": code
            })
            embed.set_footer(text = f"#{context.channel}")
            embed.set_author(name = context.author, icon_url = context.author.avatar_url)
            await context.send(embed = embed)

    @commands.command()
    @commands.check_any(commands.is_owner())
    async def cls(self, context):
        try:
            os.system('cls' if os.name == 'nt' else 'clear')
        except Exception as error_message:
            embed = create_embed(f"Error: Something went wrong clearing terminal", discord_color.red(), {
                "Error Message": str(error_message),
            })
            embed.set_footer(text = f"#{context.channel}")
            embed.set_author(name = context.author, icon_url = context.author.avatar_url)
            await context.send(embed = embed)
        else:
            embed = create_embed(f"Success: Terminal was cleared", discord_color.green())
            embed.set_footer(text = f"#{context.channel}")
            embed.set_author(name = context.author, icon_url = context.author.avatar_url)
            await context.send(embed = embed)

    @commands.command()
    @commands.check_any(commands.is_owner(), is_guild_owner())
    async def changeactivity(self, context, *, activity = ""):
        try:
            await self.client.change_presence(activity = discord.Game(name = activity))
        except Exception as error_message:
            embed = create_embed(f"Error: Something went when changing the bot's activity to `{activity}`", discord_color.red(), {
                "Error Message": str(error_message),
            })
            embed.set_footer(text = f"#{context.channel}")
            embed.set_author(name = context.author, icon_url = context.author.avatar_url)
            await context.send(embed = embed)
        else:
            embed = create_embed(f"Success: Bot's activity changed to `{activity}`", discord_color.green())
            embed.set_footer(text = f"#{context.channel}")
            embed.set_author(name = context.author, icon_url = context.author.avatar_url)
            await context.send(embed = embed)

    @commands.command()
    @commands.check_any(commands.is_owner(), is_guild_owner())
    async def changestatus(self, context, *, status = "online"):
        try:
            await self.client.change_presence(status = discord.Status[status])
        except Exception as error_message:
            embed = create_embed(f"Error: Something went when changing the bot's status to `{status}`", discord_color.red(), {
                "Error Message": str(error_message),
            })
            embed.set_footer(text = f"#{context.channel}")
            embed.set_author(name = context.author, icon_url = context.author.avatar_url)
            await context.send(embed = embed)
        else:
            embed = create_embed(f"Success: Bot's status changed to `{status}`", discord_color.green())
            embed.set_footer(text = f"#{context.channel}")
            embed.set_author(name = context.author, icon_url = context.author.avatar_url)
            await context.send(embed = embed)

def setup(client):
    client.add_cog(bot(client))