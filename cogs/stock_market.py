# discord
import discord
from discord import Color as discord_color
from discord.ext import commands, tasks

# embed
import pytz
from datetime import datetime

# other
import time
import random
import asyncio
from pymongo import MongoClient
from yahoo_fin import stock_info as si

cluster = MongoClient("mongodb+srv://admin:QZnOT86qe3TQ@cluster0.meksl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
economy = cluster.discord.economy

def create_embed(title, color = discord_color.blue(), fields = {}, user = {}):
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
    if user:
        embed.set_author(name = user, icon_url = user.avatar_url)

    return embed

"""

def is_guild_owner():
    def predicate(ctx):
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id
    return commands.check(predicate)

def save_data(user_id, data):
    economy.update_one({"id": user_id}, {"$set": data})

def insert_data(data):
    economy.insert_one(data)

def get_data(user_id):
    data = economy.find_one({"id": user_id})
    if not data:
        data =  {
            "id": user_id,
            "pocket": STARTING_POCKET_MONEY,
            "bank": STARTING_BANK_MONEY
        }
        insert_data(data)
    return data 

"""

class stock_market(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def getprice(self, context, ticker):
        ticker = ticker.upper()
        current_price = None
        try:
            current_price = si.get_live_price(ticker)
        except AssertionError:
            await context.send(embed = create_embed(f"ERROR: `{ticker}` not found", discord_color.red()))
        except Exception as error_message:
            await context.send(embed = create_embed(f"ERROR: Something went wrong when obtaining the price of `{ticker}`", discord_color.red(), {
                "Error Message": error_message
            }))
        else:
            await context.send(embed = create_embed(f"{ticker}: ${round(current_price, 2)}"))

    @commands.command()
    async def buyshares(self, context, ticker, amount_of_shares):
        pass

    @commands.command()
    async def sellshares(self, context, ticker, amount_of_shares):
        pass

def setup(client):
    client.add_cog(stock_market(client))