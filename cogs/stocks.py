import discord
from discord.ext import commands
from helper import create_embed, get_user_data, save_user_data, attach_suffix_to_number
from yahoo_fin import stock_info as si
import yfinance as yf

def get_price(ticker):
    try:
        price = round(si.get_live_price(ticker.lower()), 2)
        return price
    except Exception as error_message:
        print(error_message)
        return None

def get_open(ticker):
    try:
        data = yf.download(tickers=ticker.upper(), period='w', interval='1d', progress=False)
        price = round(dict(data)['Open'][0], 2)
        return price 
    except:
        return None

class stocks(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def getprice(self, context, ticker):
        ticker = ticker.upper()
        response = await context.send(embed = create_embed({
            'title': f'Loading share price of {ticker}...',
            'color': discord.Color.gold()
        }))

        try:
            share_price = get_price(ticker)
            if not share_price:
                await response.edit(embed=create_embed({
                    'title': f'Could not get share price of {ticker}',
                    'color': discord.Color.red()
                }))
                return

            open_price = get_open(ticker)
            open_price_text = ''
            if open_price:
                change_percent = round((share_price - open_price) / open_price * 100, 2)
                open_price_text = attach_suffix_to_number(change_percent, '%')
                open_price_text = f' ({open_price_text})'

            await response.edit(embed = create_embed({
                'title': f'{ticker}: ${share_price}{open_price_text}'
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                'title': f'Could not retrieve share price of {ticker}',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))

    @commands.command()
    async def buyshares(self, context, ticker, shares_to_purchase: int):
        ticker = ticker.upper()
        shares_to_purchase = round(shares_to_purchase, 4)

        response = await context.send(embed = create_embed({
            'title': f'Buying {shares_to_purchase} shares of {ticker}...',
            'color': discord.Color.gold()
        }))

        try:
            if shares_to_purchase <= 0:
                await response.edit(embed = create_embed({
                    'title': f'You must buy more than 0 shares',
                    'color': discord.Color.red()
                }))
                return

            share_price = get_price(ticker)
            if not share_price:
                await response.edit(embed = create_embed({
                    'title': f'Could not retrieve share price of {ticker}',
                    'color': discord.Color.red()
                }))
                return

            user_data = get_user_data(context.author.id)
            user_balance = user_data['balance']
            total_price = share_price * shares_to_purchase
            if user_balance < total_price:
                await response.edit(embed = create_embed({
                    'title': f'You cannot afford to buy {shares_to_purchase} of {ticker}',
                    'color': discord.Color.red()
                }, {
                    'Total Price': f'${total_price}',
                    'Balance': f'${user_balance}'
                }))
                return
                
            user_data['balance'] -= total_price                
            if not user_data['stocks'].get(ticker):
                user_data['stocks'][ticker] = {
                    'shares': shares_to_purchase,
                    'average_price': share_price
                }
            else:
                average_price = user_data['stocks'][ticker]['average_price']
                shares_owned = user_data['stocks'][ticker]['shares']
                total_shares = user_data['stocks'][ticker]['shares'] + shares_to_purchase
                average_price = round(((average_price * shares_owned) + (share_price * shares_to_purchase)) / total_shares, 2)
                user_data['stocks'][ticker] = {
                    'average_price': average_price,
                    'shares': user_data['stocks'][ticker]['shares'] + shares_to_purchase
                }

            save_user_data(user_data)
            shares_owned = user_data['stocks'][ticker]['shares']
            average_price = user_data['stocks'][ticker]['average_price']
            await response.edit(embed = create_embed({
                'title': f'Bought {shares_to_purchase} shares of {ticker} at ${share_price} (-${total_price})',
                'color': discord.Color.green()
            }, {
                'Shares Owned': f'{shares_owned} Shares',
                'Average Price': f'${average_price}'
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                'title': f'Could not buy {shares_to_purchase} shares of {ticker}',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))

            print(f'Could not buy {shares_to_purchase} shares of {ticker}')
            print(error_message)

    @commands.command()
    async def sellshares(self, context, ticker, shares_to_sell: int):
        ticker = ticker.upper()
        shares_to_sell = round(shares_to_sell, 4)

        response = await context.send(embed = create_embed({
            'title': f'Selling {shares_to_sell} shares of {ticker}...',
            'color': discord.Color.gold()
        }))
        
        try:
            if shares_to_sell <= 0:
                await response.edit(embed = create_embed({
                    'title': f'You must sell more than 0 shares',
                    'color': discord.Color.red()
                }))
                return

            share_price = get_price(ticker)
            if not share_price:
                await response.edit(embed = create_embed({
                    'title': f'Could not retrieve share price of {ticker}',
                    'color': discord.Color.red()
                }))
                return

            user_data = get_user_data(context.author.id)
            total_price = share_price * shares_to_sell
            if not user_data['stocks'].get(ticker) or user_data['stocks'][ticker]['shares'] < shares_to_sell:
                await response.edit(embed = create_embed({
                    'title': f'You don\'t have enough shares of {ticker} to sell',
                    'color': discord.Color.red()
                }, {
                    'Shares Owned': not user_data['stocks'].get(ticker) and 'None' or user_data['stocks'][ticker]['shares']
                }))
                return
            else:
                user_data['balance'] += total_price
                user_data['stocks'][ticker]['shares'] -= shares_to_sell
                if user_data['stocks'][ticker]['shares'] == 0:
                    user_data['stocks'].pop(ticker)

            save_user_data(user_data)
            shares_remaining = user_data['stocks'].get(ticker) and user_data['stocks'][ticker]['shares'] or 0
            await response.edit(embed = create_embed({
                'title': f'Sold {shares_to_sell} shares of {ticker} at ${share_price} (+${total_price})',
                'color': discord.Color.green()
            }, {
                'Shares Remaining': f'{shares_remaining} Shares',
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                'title': f'Could not sell {shares_to_sell} shares of {ticker}',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))

            print(f'Could not sell {shares_to_sell} shares of {ticker}')
            print(error_message)

    @commands.command()
    async def portfolio(self, context, *, member: discord.Member = None):
        if not member:
            member = context.author

        if member.bot:
            await context.send(embed = create_embed({
                'title': f'{member} is a bot',
                'color': discord.Color.red()
            }))
            return

        response = await context.send(embed = create_embed({
            'title': f'Loading {member}\'s portfolio...',
            'color': discord.Color.gold()
        }))

        try:
            user_data = get_user_data(member.id)
            total_equity = 0
            total_profit = 0

            fields = {}
            for ticker, stock_data in user_data['stocks'].items():
                share_price = get_price(ticker)
                if not share_price:
                    continue

                total_shares = stock_data['shares']
                average_price = stock_data['average_price']
                equity = total_shares * average_price
                profit = (share_price - average_price) * total_shares

                total_equity += equity
                total_profit += profit
                fields[ticker.upper()] = f'{total_shares} Shares @ ${average_price} | Equity: ${equity} | Profit: ${profit}'

            fields['SUMMARY'] = f'Equity: ${total_equity} | Profit: ${total_profit}'
            await response.edit(embed = create_embed({
                'title': f'{member}\'s Portfolio'
            }, fields))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                'title': f'Could not retrieve {member}\'s portfolio',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))

            print(f'Could not retrieve {member}\'s portfolio')
            print(error_message)

def setup(client):
    client.add_cog(stocks(client))