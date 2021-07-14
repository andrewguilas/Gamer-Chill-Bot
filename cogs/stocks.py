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
    async def getprice(self, context, ticker: str):
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

def setup(client):
    client.add_cog(stocks(client))