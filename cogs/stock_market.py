PERIOD = "2h"
INTERVAL = "1m"
STARTING_POCKET_MONEY = 20
STARTING_BANK_MONEY = 500

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
import yfinance as yf

cluster = MongoClient("mongodb+srv://admin:QZnOT86qe3TQ@cluster0.meksl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
economy = cluster.discord.economy
stocks = cluster.discord.stocks

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

def is_guild_owner():
    def predicate(ctx):
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id
    return commands.check(predicate)

def get_price(ticker: str):
    ticker = ticker.upper()
    try:
        data = yf.download(tickers = ticker, period = PERIOD, interval = INTERVAL)
        price = dict(data)["Close"][0]
        return round(price, 2)
    except:
        pass

# data (stocks)

def save_stock_data(user_id, data):
    stocks.update_one({"id": user_id}, {"$set": data})

def insert_stock_data(data):
    stocks.insert_one(data)

def get_stock_data(user_id):
    data = stocks.find_one({"id": user_id})
    if not data:
        data =  {
            "id": user_id,
            "shares": {}
        }
        insert_stock_data(data)
    return data 

# data (economy)

def save_economy_data(user_id, data):
    economy.update_one({"id": user_id}, {"$set": data})

def insert_economy_data(data):
    economy.insert_one(data)

def get_economy_data(user_id):
    data = economy.find_one({"id": user_id})
    if not data:
        data =  {
            "id": user_id,
            "pocket": STARTING_POCKET_MONEY,
            "bank": STARTING_BANK_MONEY
        }
        insert_economy_data(data)
    return data 

class stock_market(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def getprice(self, context, ticker):
        ticker = ticker.upper()
        current_price = get_price(ticker)
        if current_price:
            await context.send(embed = create_embed(f"{ticker}: ${current_price}"))
        else:
            await context.send(embed = create_embed(f"ERROR: Something went wrong when obtaining the price of `{ticker}`", discord_color.red()))

    @commands.command()
    async def buyshares(self, context, ticker: str, shares: int):
        ticker = ticker.upper()
        shares = round(shares, 2)
        user_id = context.author.id
        current_price = get_price(ticker)
        market_value = round(current_price * shares, 2)

        # transaction
        economy_data = get_economy_data(user_id)
        if economy_data["bank"] < market_value:
            await context.send(embed = create_embed(f"ERROR: You do not have enough money to purchase {shares} shares of {ticker}", discord_color.red(), {
                "Market Value": "$" + str(market_value),
                "Buying Power": "$" + str(round(economy_data["bank"], 2))
            }))
            return

        economy_data["bank"] -= round(market_value, 2)
        save_economy_data(user_id, economy_data)

        # give shares
        stock_data = get_stock_data(user_id)
        ticker_data = stock_data["shares"].get(ticker)
        if ticker_data:
            stock_data["shares"][ticker] += shares
        else:
            stock_data["shares"][ticker] = shares
        save_stock_data(user_id, stock_data)
        
        total_shares = round(stock_data["shares"][ticker], 2)

        # send status
        await context.send(embed = create_embed(f"SUCCESS: {shares} shares of {ticker} were bought at ${current_price}", discord_color.green(), {
            "Average Price": f"${current_price}",
            "Total Shares": total_shares,
            "Equity": f"${round(total_shares * current_price, 2)}"
        }))

    @commands.command()
    async def sellshares(self, context, ticker: str, shares: int):
        ticker = ticker.upper()
        user_id = context.author.id
        current_price = get_price(ticker)
        market_value = round(current_price * shares, 2)

        # take shares
        stock_data = get_stock_data(user_id)
        ticker_data = stock_data["shares"].get(ticker)
        if not ticker_data:
            await context.send(embed = create_embed(f"ERROR: You do not have any shares in {ticker}", discord_color.red(), {
                "Shares to Sell": shares,
                "Shares Holding": 0
            }))
            return
        elif ticker_data < shares:
            await context.send(embed = create_embed(f"ERROR: You only have {ticker_data} shares", discord_color.red(), {
                "Shares to Sell": shares,
                "Shares Holding": ticker_data
            }))
            return
        
        stock_data["shares"][ticker] -= shares
        if stock_data["shares"][ticker] == 0:
            stock_data["shares"].pop(ticker)
        save_stock_data(user_id, stock_data)

        # give money        
        economy_data = get_economy_data(user_id)
        economy_data["bank"] += market_value
        save_economy_data(user_id, economy_data)

        await context.send(embed = create_embed(f"SUCCESS: {shares} shares of {ticker} were sold", discord_color.green(), {
            "Equity Earned": f"${market_value}",
            "Shares Remaining": stock_data["shares"].get(ticker) and round(stock_data["shares"].get(ticker), 2) or "0"
        }))

    @commands.command()
    async def portfolio(self, context):
        user_id = context.author.id
        stock_data = get_stock_data(user_id)

        if not stock_data.get("shares"):
            await context.send(embed = create_embed(f"{context.author.name}'s Portfolio"))
            return

        fields = {}
        for ticker, shares in stock_data["shares"].items():
            current_price = get_price(ticker)
            title = f"{ticker}: {round(shares, 2)} Shares"
            print(shares, current_price)
            fields[title] = f"Equity: ${round(shares * current_price, 2)}"

        await context.send(embed = create_embed(f"{context.author.name}'s portfolio", None, fields))

def setup(client):
    client.add_cog(stock_market(client))