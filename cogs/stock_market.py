PERIOD = "2h"
INTERVAL = "1m"
DEFAULT_STOCK_DATA = {
    "id": None,
    "shares": {}
}

# discord
import discord
from discord import Color as discord_color
from discord.ext import commands, tasks

# embed
import pytz
from datetime import datetime

# other
import asyncio
import yfinance as yf
from pymongo import MongoClient

import cogs.economy_system as economy_system

cluster = MongoClient("mongodb+srv://admin:QZnOT86qe3TQ@cluster0.meksl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
stocks_data_store = cluster.discord.stocks

def create_embed(title, fields: {} = {}, info: {} = {}):
    embed = discord.Embed(
        title = title,
        colour = info.get("color") or discord_color.blue(),
        timestamp = datetime.now(tz = pytz.timezone("US/Eastern"))
    )

    for name, value in fields.items():
        embed.add_field(
            name = name,
            value = value,
            inline = True
        )

    if info.get("user"):
        embed.set_author(name = info.user, icon_url = info.user.avatar_url)

    return embed

def get_price(ticker: str):
    ticker = ticker.upper()
    try:
        data = yf.download(tickers = ticker, period = PERIOD, interval = INTERVAL)
        price = dict(data)["Close"][0]
        return round(price, 2)
    except:
        pass

def save_stock_data(user_id, data):
    stocks_data_store.update_one({"id": user_id}, {"$set": data})

def insert_stock_data(data):
    stocks_data_store.insert_one(data)

def get_stock_data(user_id):
    data = stocks_data_store.find_one({"id": user_id})
    if not data:
        data = DEFAULT_STOCK_DATA
        insert_stock_data(data)
    return data 

def get_investing_amount(user_id):
    stocks = get_stock_data(user_id)["shares"]
    investing_amount = 0
    for ticker, shares in stocks.items():
        average_price = get_price(ticker)
        investing_amount += round(shares * average_price, 2)
    return investing_amount

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
            await context.send(embed = create_embed(f"ERROR: Something went wrong when obtaining the price of `{ticker}`", {}, {
                "color": discord_color.red(),
            }))

    @commands.command()
    async def buyshares(self, context, ticker: str, shares: int):
        user_id = context.author.id
        ticker = ticker.upper()
        shares = round(shares, 2)
        current_price = get_price(ticker)
        market_value = round(current_price * shares, 2)

        # transaction
        economy_data = economy_system.get_economy_data(user_id)
        if economy_data["bank"] < market_value:
            await context.send(embed = create_embed(f"ERROR: You do not have enough money in the bank to purchase {shares} shares of {ticker}", {
                "Market Value": "$" + str(market_value),
                "Buying Power": "$" + str(round(economy_data["bank"], 2))
            }, {
                "color": discord_color.red(),
                "member": context.author,
            }))
            return
        economy_data["bank"] -= round(market_value, 2)
        economy_system.save_economy_data(user_id, economy_data)

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
        await context.send(embed = create_embed(f"SUCCESS: {shares} shares of {ticker} were bought at ${current_price}", {
            "Average Price": f"${current_price}",
            "Total Price": f"${market_value}",
            "Total Shares": total_shares,
            "Equity": f"${round(total_shares * current_price, 2)}"
        }, {
            "color": discord_color.green(),
            "member": context.author,
        }))

    @commands.command()
    async def sellshares(self, context, ticker: str, shares: int):
        user_id = context.author.id
        ticker = ticker.upper()
        shares = round(shares, 2)
        current_price = get_price(ticker)
        market_value = round(current_price * shares, 2)

        # take shares
        stock_data = get_stock_data(user_id)
        ticker_data = stock_data["shares"].get(ticker)
        if not ticker_data:
            await context.send(embed = create_embed(f"ERROR: You do not have any shares in {ticker}", {
                "Shares to Sell": shares,
                "Shares Holding": 0
            }, {
                "color": discord_color.red(),
                "member": context.author,
            }))
            return
        elif ticker_data < shares:
            await context.send(embed = create_embed(f"ERROR: You only have {ticker_data} shares", {
                "Shares to Sell": shares,
                "Shares Holding": ticker_data
            }, {
                "color": discord_color.red(),
                "member": context.author,
            }))
            return
        
        stock_data["shares"][ticker] -= shares
        if stock_data["shares"][ticker] == 0:
            stock_data["shares"].pop(ticker)
        save_stock_data(user_id, stock_data)

        # give money        
        economy_data = economy_system.get_economy_data(user_id)
        economy_data["bank"] += market_value
        economy_system.save_economy_data(user_id, economy_data)

        await context.send(embed = create_embed(f"SUCCESS: {shares} shares of {ticker} were sold", {
            "Equity Earned": f"${market_value}",
            "Average Price": current_price,
            "Shares Sold": shares,
            "Shares Remaining": stock_data["shares"].get(ticker) and round(stock_data["shares"].get(ticker), 2) or "0"
        }, {
            "color": discord_color.green(),
            "member": context.author,
        }))

    @commands.command()
    async def portfolio(self, context):
        embed = await context.send(embed = create_embed(f"{context.author.name}'s Portfolio", {
            "Status": "Loading...",
        }, {
            "color": discord_color.gold(),
        }))

        user_id = context.author.id
        stock_data = get_stock_data(user_id)

        if not stock_data.get("shares"):
            await embed.edit(embed = create_embed(f"{context.author.name}'s Portfolio", {}, {
                "member": context.author,
            }))
            return

        fields = {}
        investing_amount = 0
        for ticker, shares in stock_data["shares"].items():
            current_price = get_price(ticker)
            title = f"{ticker}: {round(shares, 2)} Shares"
            equity = round(shares * current_price, 2)
            fields[title] = f"Equity: ${equity}"
            investing_amount += equity
        fields["Investing Amount"] = "${}".format(round(investing_amount, 2))

        await embed.edit(embed = create_embed(f"{context.author.name}'s portfolio", fields, {
            "member": context.author,
        }))

def setup(client):
    client.add_cog(stock_market(client))