import discord
from discord.ext import commands, tasks
from yahoo_fin import stock_info as si
import yfinance as yf
import asyncio
import requests

from helper import create_embed, get_user_data, save_user_data
from constants import UPDATE_TICKERS, TICKER_PERIOD, TICKER_INTERVAL

def get_price(ticker: str, round_to: int = 2):
    try:
        price = round(si.get_live_price(ticker.lower()), round_to)
        return price
    except:
        return None

def get_open(ticker: str, round_to: int = 2):
    try:
        ticker = ticker.upper()
        data = yf.download(tickers = ticker, period = TICKER_PERIOD, interval = TICKER_INTERVAL)
        price = round(dict(data)["Open"][0], round_to)
        return price 
    except:
        return None

class stocks(commands.Cog, description = "Stock market commands."):
    def __init__(self, client):
        self.client = client
        self.tickers = {
            "BTC": {
                "ticker": "BTC-USD",
                "round_to": 0,
            },
            "ETH": {
                "ticker": "ETH-USD",
                "round_to": 0,
            },
            "ADA": {
                "ticker": "ADA-USD",
                "round_to": 2,
            },
            "SPY": {
                "ticker": "SPY",
                "round_to": 2,
            },
        }
        self.update_tickers.start()

    def cog_unload(self):
        self.update_tickers.cancel()

    def cog_load(self):
        self.update_tickers.start()

    @tasks.loop()
    async def update_tickers(self):
        await self.client.wait_until_ready()
        while True:
            for nickname, info in self.tickers.items():
                try:
                    ticker = info["ticker"]
                    open_price = get_open(ticker, info["round_to"])
                    current_price = get_price(ticker, info["round_to"])

                    change = round(current_price - open_price, info["round_to"])
                    change_text = change < 0 and f"-${abs(change)}" or f"+${change}"
                    change_percent = round(change / open_price * 100, 2)
                    change_percent_text = change_percent < 0 and f"-{abs(change_percent)}" or f"+{change_percent}"

                    status = open_price and current_price < open_price and discord.Status.dnd or discord.Status.online
                    await self.client.change_presence(activity = discord.Game(name = f"{nickname}: ${current_price} | {change_percent_text}% | {change_text}"), status = status)
                except requests.exceptions.ConnectionError:
                    print("ERROR: Max retrieves with live tickers")
                except Exception as error_message:
                    print(error_message)
                await asyncio.sleep(UPDATE_TICKERS)

    @commands.command()
    @commands.guild_only()
    async def getprice(self, context, ticker: str):
        ticker = ticker.upper()
        response = await context.send(embed = create_embed({
            "title": f"Loading share price of {ticker}...",
            "color": discord.Color.gold()
        }))

        try:
            share_price = get_price(ticker)
            if not share_price:
                await response.edit(embed=create_embed({
                    "title": f"Could not get share price of {ticker}",
                    "color": discord.Color.red()
                }))
                return

            await response.edit(embed = create_embed({
                "title": f"{ticker}: ${share_price}"
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not get share price of {ticker}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command()
    @commands.guild_only()
    async def buyshares(self, context, ticker: str, shares_to_purchase: float):
        ticker = ticker.upper()
        shares_to_purchase = round(shares_to_purchase, 4)

        response = await context.send(embed = create_embed({
            "title": f"Buying {shares_to_purchase} shares of {ticker}...",
            "color": discord.Color.gold()
        }))

        try:
            # checks
            if shares_to_purchase <= 0:
                await response.edit(embed = create_embed({
                    "title": f"You must buy more than 0 shares",
                    "color": discord.Color.red()
                }))
                return

            share_price = get_price(ticker)
            if not share_price:
                await response.edit(embed = create_embed({
                    "title": f"Could not get share price of {ticker}",
                    "color": discord.Color.red()
                }))
                return

            # handle money transaction
            total_price = round(share_price * shares_to_purchase, 2)
            user_data = get_user_data(context.author.id)
            user_balance = round(user_data["money"], 2)
            if user_balance < total_price:
                await response.edit(embed = create_embed({
                    "title": f"You do not have enough money to purchase {shares_to_purchase} of {ticker}",
                    "color": discord.Color.red()
                }, {
                    "Total Price": f"${total_price}",
                    "Balance": "${}".format(user_balance)
                }))
                return
                
            user_data["money"] -= total_price                

            # handle share transaction
            if not user_data["stocks"].get(ticker):
                user_data["stocks"][ticker] = {
                    "shares": shares_to_purchase,
                    "average_price": share_price
                }
            else:
                average_price = user_data["stocks"][ticker]["average_price"]
                shares_owned = user_data["stocks"][ticker]["shares"]
                total_shares = user_data["stocks"][ticker]["shares"] + shares_to_purchase
                average_price = round(((average_price * shares_owned) + (share_price * shares_to_purchase)) / total_shares, 2)
                user_data["stocks"][ticker] = {
                    "average_price": average_price,
                    "shares": user_data["stocks"][ticker]["shares"] + shares_to_purchase
                }

            # response
            save_user_data(user_data)
            shares_owned = round(user_data["stocks"][ticker]["shares"], 4)
            average_price = round(user_data["stocks"][ticker]["average_price"], 2)
            await response.edit(embed = create_embed({
                "title": f"Bought {shares_to_purchase} shares of {ticker} at ${share_price} (-${total_price})",
                "color": discord.Color.green()
            }, {
                "Shares Owned": f"{shares_owned} Shares",
                "Average Price": f"${average_price}"
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not buy {shares_to_purchase} shares of {ticker}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command()
    @commands.guild_only()
    async def sellshares(self, context, ticker: str, shares_to_sell: float):
        ticker = ticker.upper()
        shares_to_sell = round(shares_to_sell, 4)

        response = await context.send(embed = create_embed({
            "title": f"Selling {shares_to_sell} shares of {ticker}...",
            "color": discord.Color.gold()
        }))
        
        try:
            # checks
            if shares_to_sell <= 0:
                await response.edit(embed = create_embed({
                    "title": f"You must sell more than 0 shares",
                    "color": discord.Color.red()
                }))
                return

            share_price = get_price(ticker)
            if not share_price:
                await response.edit(embed = create_embed({
                    "title": f"Could not get share price of {ticker}",
                    "color": discord.Color.red()
                }))
                return

            # handle money transaction
            total_price = round(share_price * shares_to_sell, 2)

            user_data = get_user_data(context.author.id)
            if not user_data["stocks"].get(ticker) or user_data["stocks"][ticker]["shares"] < shares_to_sell:
                await response.edit(embed = create_embed({
                    "title": f"You don't have enough shares of {ticker} to sell",
                    "color": discord.Color.red()
                }))
                return
            else:
                user_data["money"] += total_price
                user_data["stocks"][ticker]["shares"] -= shares_to_sell
                if user_data["stocks"][ticker]["shares"] == 0:
                    user_data["stocks"].pop(ticker)

            # response
            save_user_data(user_data)

            shares_remaining = 0
            if user_data["stocks"].get(ticker):
                shares_remaining = round(user_data["stocks"][ticker]["shares"], 4)

            await response.edit(embed = create_embed({
                "title": f"Sold {shares_to_sell} shares of {ticker} at ${share_price} (+${total_price})",
                "color": discord.Color.green()
            }, {
                "Shares Remaining": f"{shares_remaining} Shares",
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not sell {shares_to_sell} shares of {ticker}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command()
    @commands.guild_only()
    async def portfolio(self, context, member: discord.Member = None):
        if not member:
            member = context.author

        response = await context.send(embed = create_embed({
            "title": f"Loading {member}'s portfolio...",
            "color": discord.Color.gold()
        }))

        try:
            user_data = get_user_data(member.id)
            total_equity = 0
            total_profit = 0
            fields = {}
            for ticker, stock_data in user_data["stocks"].items():
                share_price = get_price(ticker)
                if not share_price:
                    continue

                total_shares = round(stock_data["shares"], 4)
                average_price = round(stock_data["average_price"], 2)
                equity = round(total_shares * average_price, 2)
                profit = round((share_price - average_price) * total_shares, 2)

                total_equity += equity
                total_profit += profit
                fields[ticker.upper()] = f"{total_shares} Shares @ ${average_price} | Equity: ${equity} | Profit: ${profit}"

            total_equity = round(total_equity, 2)
            total_profit = round(total_profit, 2)
            fields["SUMMARY"] = f"Equity: ${total_equity} | Profit: ${total_profit}"
            await response.edit(embed = create_embed({
                "title": f"{member}'s Portfolio"
            }, fields))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not load {member}'s portfolio",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

def setup(client):
    client.add_cog(stocks(client))
