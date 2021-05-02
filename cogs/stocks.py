import discord
from discord.ext import commands
from yahoo_fin import stock_info as si

from helper import create_embed, get_user_data, save_user_data

def get_price(ticker: str):
    price = si.get_live_price(ticker.lower())
    return price and round(price, 2)

class stocks(commands.Cog, description = "Stock market commands."):
    def __init__(self, client):
        self.client = client

    @commands.command(description = "Gets the most recent price of the stock.")
    async def getprice(self, context, ticker: str):
        ticker = ticker.upper()
        response = await context.send(embed = create_embed({
            "title": f"Loading share price of {ticker}...",
            "color": discord.Color.gold()
        }))

        try:
            share_price = get_price(ticker)
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

    @commands.command(description = "Buys shares of a stock.")
    async def buyshares(self, context, ticker: str, shares_to_purchase: float):
        ticker = ticker.upper()
        shares_to_purchase = round(shares_to_purchase, 2)

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
            if user_data["money"] < total_price:
                await response.edit(embed = create_embed({
                    "title": f"You do not have enough money to purchase {shares_to_purchase} of {ticker} (-${total_price})",
                    "color": discord.Color.red()
                }, {
                    "Total Price": f"${total_price}",
                    "Balance": "${}".format(user_data["money"])
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
            await response.edit(embed = create_embed({
                "title": f"Bought {shares_to_purchase} shares of {ticker} at ${share_price}",
                "color": discord.Color.green()
            }, {
                "Shares Owned": "{} Shares".format(user_data["stocks"][ticker]["shares"]),
                "Average Price": "${}".format(user_data["stocks"][ticker]["average_price"])
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not buy {shares_to_purchase} shares of {ticker}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command(description = "Sells shares of a stock.")
    async def sellshares(self, context, ticker: str, shares_to_sell: float):
        ticker = ticker.upper()
        shares_to_sell = round(shares_to_sell, 2)

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
                shares_remaining = user_data["stocks"][ticker]["shares"]

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

    @commands.command(description = "Gets owned stocks of the user.")
    async def portfolio(self, context, member: discord.Member = None):
        if not member:
            member = context.author

        response = await context.send(embed = create_embed({
            "title": f"Loading {member}'s portfolio...",
            "color": discord.Color.gold()
        }))

        try:
            user_data = get_user_data(member.id)
            fields = {}
            for ticker, stock_data in user_data["stocks"].items():
                share_price = get_price(ticker)
                if not share_price:
                    continue

                total_shares = round(stock_data["shares"], 2)
                average_price = round(stock_data["average_price"], 2)
                equity = round(total_shares * average_price, 2)
                profit = round((share_price - average_price) * total_shares, 2)

                fields[ticker.upper()] = f"{total_shares} Shares @ ${average_price} | Equity: ${equity} | Profit: ${profit}"

            await response.edit(embed = create_embed({
                "title": f"{member}'s Portfolio"
            }, fields))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not load {member}'s portfolio",
                "color": discord.Color.red()
            }))

def setup(client):
    client.add_cog(stocks(client))