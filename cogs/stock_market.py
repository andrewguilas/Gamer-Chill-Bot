PERIOD = "2h"
INTERVAL = "1m"
DEFAULT_ECONOMY_DATA = {
    "id": None,
    "pocket": 20,
    "bank": 500,
}
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
from pymongo import MongoClient
import yfinance as yf

cluster = MongoClient("mongodb+srv://admin:QZnOT86qe3TQ@cluster0.meksl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
economy_data_store = cluster.discord_2.economy
stock_data_store = cluster.discord_2.stocks

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

    if info.get("member"):
        embed.set_author(name = info["member"], icon_url = info["member"].avatar_url)

    return embed

def get_stock_price(ticker: str):
    ticker = ticker.upper()
    try:
        data = yf.download(tickers = ticker, period = PERIOD, interval = INTERVAL)
        price = dict(data)["Close"][0]
        return round(price, 2)
    except:
        pass

# data (stocks)

def save_stock_data(user_id, data):
    stock_data_store.update_one({"id": user_id}, {"$set": data})

def insert_stock_data(data):
    stock_data_store.insert_one(data)

def get_stock_data(user_id):
    data = stock_data_store.find_one({"id": user_id})
    if not data:
        data = DEFAULT_STOCK_DATA
        data["id"] = user_id,
        insert_stock_data(data)
    return data 

# data (economy)

def save_economy_data(user_id, data):
    economy_data_store.update_one({"id": user_id}, {"$set": data})

def insert_economy_data(data):
    economy_data_store.insert_one(data)

def get_economy_data(user_id):
    data = economy_data_store.find_one({"id": user_id})
    if not data:
        data = DEFAULT_ECONOMY_DATA
        data["id"] = user_id
        insert_economy_data(data)
    return data 

class stock_market(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def getprice(self, context, ticker):
        embed = await context.send(embed = create_embed(f"Getting price of {ticker}...", {}, {
            "color": discord_color.gold(),
            "member": context.author,
        }))

        ticker = ticker.upper()
        current_price = get_stock_price(ticker)
        if current_price:
            await embed.edit(embed = create_embed(f"{ticker}: ${current_price}", {}, {
                "member": context.author,
            }))
        else:
            await embed.edit(embed = create_embed(f"ERROR: Something went wrong when obtaining the price of `{ticker}`", {}, {
                "color": discord_color.red(),
                "member": context.author,
            }))

    @commands.command()
    async def buyshares(self, context, ticker: str, shares: int):
        ticker = ticker.upper()
        embed = await context.send(embed = create_embed(f"Buying {shares} shares of {ticker}...", {}, {
            "color": discord_color.gold(),
            "member": context.author,
        }))

        user_id = context.author.id
        current_price = get_stock_price(ticker)
        market_value = current_price * shares

        # transaction
        economy_data = get_economy_data(user_id)
        if economy_data["bank"] < market_value:
            await embed.edit(embed = create_embed(f"ERROR: You do not have enough money to purchase {shares} shares of {ticker}", {
                "Market Value": "$" + str(market_value),
                "Buying Power": "$" + str(round(economy_data["bank"], 2))
            }, {
                "color": discord_color.red(),
                "member": context.author,
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
        
        total_shares = stock_data["shares"][ticker]

        # send status
        await embed.edit(embed = create_embed(f"SUCCESS: {shares} shares of {ticker} were bought at ${current_price}", {
            "Average Price": f"${current_price}",
            "Total Shares": total_shares,
            "Equity": f"${round(total_shares * current_price, 2)}"
        }, {
            "color": discord_color.green(),
            "member": context.author,
        }))

    @commands.command()
    async def sellshares(self, context, ticker: str, shares: int):
        ticker = ticker.upper()
        embed = await context.send(embed = create_embed(f"Selling {shares} shares of {ticker}...", {}, {
            "color": discord_color.gold(),
            "member": context.author,
        }))

        user_id = context.author.id
        current_price = get_stock_price(ticker)

        # take shares
        stock_data = get_stock_data(user_id)
        ticker_data = stock_data["shares"].get(ticker)
        market_value = round(current_price * shares, 2)
        if not ticker_data:
            await embed.edit(embed = create_embed(f"ERROR: You do not have any shares in {ticker}", {
                "Shares to Sell": shares,
                "Shares Holding": round(ticker_data, 2)
            }, {
                "color": discord_color.red(),
                "member": context.author,
            }))
            return
        elif ticker_data < shares:
            await embed.edit(embed = create_embed(f"ERROR: You only have {ticker_data} shares", {
                "Shares to Sell": shares
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
        economy_data = get_economy_data(user_id)
        economy_data["bank"] += market_value
        save_economy_data(user_id, economy_data)

        await embed.edit(embed = create_embed(f"SUCCESS: {shares} shares of {ticker} were sold", {
            "Equity Earned": f"${market_value}",
            "Shares Remaining": stock_data["shares"].get(ticker) and round(stock_data["shares"].get(ticker), 2) or "0"
        }, {
            "color": discord_color.green(),
        }))

    @commands.command()
    async def portfolio(self, context, member: discord.Member = None):
        if not member:
            member = context.author

        embed = await context.send(embed = create_embed(f"Loading {member}'s portfolio...", {}, {
            "color": discord_color.gold(),
            "member": context.author,
        }))

        user_id = member.id
        stock_data = get_stock_data(user_id)

        if not stock_data.get("shares"):
            await embed.send(edit = create_embed(f"{member.name}'s Portfolio", {
                "Equity": "$0.00"
            }, {
                "member": context.author,
            }))
            return

        fields = {}
        investing_amount = 0
        for ticker, shares in stock_data["shares"].items():
            current_price = get_stock_price(ticker)
            equity = round(shares * current_price, 2)
            investing_amount += equity
            fields["{}: {} shares".format(ticker, shares)] = "Equity: ${}".format(equity)
        fields["Investing Amount"] = "${}".format(round(investing_amount, 2))

        await embed.edit(embed = create_embed(f"{member.name}'s portfolio", fields, {
            "member": context.author,
        }))

def setup(client):
    client.add_cog(stock_market(client))