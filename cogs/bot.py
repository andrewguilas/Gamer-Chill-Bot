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
            inline = False
        )

    embed.timestamp = datetime.now(tz = pytz.timezone("US/Eastern"))

    return embed

class bot(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.check_any(commands.is_owner())
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

def setup(client):
    client.add_cog(bot(client))