import discord
from discord.ext import commands
from pymongo import MongoClient
import yfinance as yf

from secrets import MONGO_TOKEN
from helper import create_embed, get_settings
from constants import STOCKS_PERIOD, STOCKS_INTERVAL

cluster = MongoClient(MONGO_TOKEN)
stocks_data_store = cluster.discord_revamp.stocks
economoy_data_store = cluster.discord_revamp.economy

def save_economy_data(data):
    economoy_data_store.update_one({"user_id": data["user_id"]}, {"$set": data})
    
def get_economy_data(user_id: int):
    data = economoy_data_store.find_one({"user_id": user_id}) 
    if not data:
        data = {"user_id": user_id, "money": 0}
        economoy_data_store.insert_one(data)
    return data

def save_stocks_data(data):
    stocks_data_store.update_one({"user_id": data["user_id"]}, {"$set": data})
    
def get_stocks_data(user_id: int):
    data = stocks_data_store.find_one({"user_id": user_id}) 
    if not data:
        data = {"user_id": user_id, "orders": []}
        stocks_data_store.insert_one(data)
    return data

def get_price(ticker: str):
    ticker = ticker.upper()
    data = yf.download(tickers = ticker, period = STOCKS_PERIOD, interval = STOCKS_INTERVAL)
    price = dict(data)["Close"][0]
    return round(price, 2)

class stocks(commands.Cog, description = "Stock market commands."):
    def __init__(self, client):
        self.client = client

    @commands.command(description = "Gets the recent price of the stock.")
    async def getprice(self, context, ticker: str):
        ticker = ticker.upper()

        response = await context.send(embed = create_embed({
            "title": f"Loading share price for {ticker}",
            "color": discord.Color.gold()
        }))

        try:
            price = get_price(ticker)
            await response.edit(embed = create_embed({
                "title": f"{ticker}: ${price}"
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not get share price for {ticker}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command(description = "Buys shares of the stock.")
    async def buyshares(self, context, ticker: str, amount: float):
        ticker = ticker.upper()
        amount = round(amount, 2)

        response = await context.send(embed = create_embed({
            "title": f"Buying {amount} shares of {ticker}",
            "color": discord.Color.gold()
        }))

        try:
            if amount <= 0:
                await response.edit(embed = create_embed({
                    "title": f"{amount} is not greather than 0",
                    "color": discord.Color.red()
                }))
                return

            # get stock price
            share_price = get_price(ticker)
            if not share_price:
                raise Exception("")

            # handle money transaction
            total_price = round(share_price * amount, 2)
            user_money_data = get_economy_data(context.author.id)

            user_money = user_money_data["money"]
            if user_money < total_price:
                await response.edit(embed = create_embed({
                    "title": f"You don't have enough money to buy {amount} shares of {ticker}",
                    "color": discord.Color.red()
                }, {
                    "Share Price": share_price,
                    "Balance": f"${user_money}"
                }))
                return

            user_money_data["money"] -= total_price
            save_economy_data(user_money_data)

            # handle share trade
            user_stocks_data = get_stocks_data(context.author.id)
            user_stocks_data["orders"].append({
                "ticker": ticker,
                "shares": amount,
                "average_price": share_price
            })
            save_stocks_data(user_stocks_data)

            # response
            orders_for_stock = []
            total_shares = 0
            average_price = 0
            for order in user_stocks_data["orders"]:
                if order["ticker"] == ticker:
                    total_shares += order["shares"]
                    orders_for_stock.append(order)
                    average_price += order["shares"] * order["average_price"]
                
            average_price /= total_shares
            average_price = round(average_price, 2)
            equity = round(total_shares * average_price, 2)
            total_shares = round(total_shares, 2)

            await response.edit(embed = create_embed({
                "title": f"Bought {amount} shares of {ticker} at ${share_price} (-${total_price})",
                "color": discord.Color.green()
            }, {
                "Total Shares": f"{total_shares} Shares",
                "Average Price": f"${average_price}",
                "Equity": f"${equity}"
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not buy {amount} shares of {ticker}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command(description = "Retrieves owned shares on the stock market.")
    async def portfolio(self, context, member: discord.Member = None):
        if not member:
            member = context.author

        response = await context.send(embed = create_embed({
            "title": f"Retrieving {member}'s portfolio",
            "color": discord.Color.gold()
        }))

        try:
            orders_by_stock = {}
            user_stock_data = get_stocks_data(member.id)
            for order in user_stock_data["orders"]:
                ticker = order["ticker"]
                if not orders_by_stock.get(ticker):
                    orders_by_stock[ticker] = []
                orders_by_stock[ticker].append(order)

            fields = {}
            for ticker, stock_orders in orders_by_stock.items():
                total_shares = 0
                average_price = 0

                for order in stock_orders:
                    total_shares += order["shares"]
                    average_price += order["shares"] * order["average_price"]
                    
                average_price /= total_shares
                average_price = round(average_price, 2)
                equity = round(total_shares * average_price, 2)

                stock_price = get_price(ticker)
                profit = round(stock_price * total_shares - equity, 2)

                total_shares = round(total_shares, 2)

                fields[ticker] = f"{total_shares} Shares @ ${average_price} | Equity: ${equity} | Profit: ${profit}"

            await response.edit(embed = create_embed({
                "title": f"{member}'s Portfolio",
            }, fields))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not retrieve {member}'s portfolio",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command(description = "Sells shares of the stock.")
    async def sellshares(self, context, ticker: str, amount: float):
        ticker = ticker.upper()
        amount = round(amount, 2)

        response = await context.send(embed = create_embed({
            "title": f"Selling {amount} shares of {ticker}",
            "color": discord.Color.gold()
        }))

        try:
            if amount <= 0:
                await response.edit(embed = create_embed({
                    "title": f"{amount} is not greather than 0",
                    "color": discord.Color.red()
                }))
                return

            # check if member has enough shares
            shares_owned = 0
            user_stock_data = get_stocks_data(context.author.id)
            for order in user_stock_data["orders"]:
                if order["ticker"] == ticker:
                    shares_owned += order["shares"]

            if shares_owned < amount:
                await response.edit(embed = create_embed({
                    "title": f"You don't owned enough shares to sell {amount} shares of {ticker}",
                    "color": discord.Color.red()
                }, {
                    "Shares Owned": f"{shares_owned} Shares"
                }))
                return

            # sell shares
            shares_remaining_to_sell = amount
            user_stock_data = get_stocks_data(context.author.id)

            while shares_remaining_to_sell > 0:
                for index, order in enumerate(user_stock_data["orders"].copy()):
                    if order["ticker"] == ticker:
                        if order["shares"] == shares_remaining_to_sell:
                            shares_remaining_to_sell = 0
                            user_stock_data["orders"].pop(index)
                        elif order["shares"] > shares_remaining_to_sell:
                            user_stock_data["orders"][index]["shares"] -= shares_remaining_to_sell
                            shares_remaining_to_sell = 0
                        elif order["shares"] < shares_remaining_to_sell:
                            shares_remaining_to_sell -= order["shares"]
                            user_stock_data["orders"].pop(index)
                        break
            save_stocks_data(user_stock_data)

            # give money
            share_price = get_price(ticker)
            total_price = round(share_price * amount, 2)
            user_money_data = get_economy_data(context.author.id)
            user_money_data["money"] += total_price
            save_economy_data(user_money_data)

            # resposne

            orders_for_stock = []
            total_shares = 0
            average_price = 0
            for order in user_stock_data["orders"]:
                if order["ticker"] == ticker:
                    total_shares += order["shares"]
                    orders_for_stock.append(order)
                    average_price += order["shares"] * order["average_price"]
                
            average_price /= total_shares
            average_price = round(average_price, 2)
            equity = round(total_shares * average_price, 2)
            total_shares = round(total_shares, 2)
            
            await response.edit(embed = create_embed({
                "title": f"Sold {amount} shares of {ticker} at ${share_price} (+${total_price})",
                "color": discord.Color.green()
            }, {
                "Total Shares": f"{total_shares} Shares",
                "Average Price": f"${average_price}",
                "Equity": f"${equity}"
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not sell {amount} shares of {ticker}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

def setup(client):
    client.add_cog(stocks(client))