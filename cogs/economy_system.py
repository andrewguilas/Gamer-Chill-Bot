PERIOD = "2h"
INTERVAL = "1m"
MAX_FIELDS_FOR_LEADERBOARD_EMBED = 10
MAX_FIELDS = 5
DEFAULT_ECONOMY_DATA = {
    "id": None,
    "pocket": 20,
    "bank": 500,
}

DEFAULT_STOCK_DATA = {
    "id": None,
    "shares": {}
}

import discord
from discord import Color as discord_color
from discord.ext import commands, tasks

import pytz
import yfinance as yf
from datetime import datetime
from pymongo import MongoClient

import os
from PIL import Image
from finvizfinance.quote import finvizfinance
from finvizfinance.screener.overview import Overview

cluster = MongoClient("mongodb+srv://admin:QZnOT86qe3TQ@cluster0.meksl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
economy_data_store = cluster.discord_2.economy
stocks_data_store = cluster.discord_2.stocks

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
    if info.get("author_name"):
        embed.set_author(name = info["author_name"], icon_url = info.get("author_icon"))
    if info.get("thumbnail"):
        embed.set_thumbnail(url = info["thumbnail"])
    if info.get("image"):
        embed.set_image(url = info["image"])
    if info.get("url"):
        embed.url = info["url"]
    if info.get("footer"):
        embed.set_footer(text = info["footer"], icon_url = "")

    return embed

# economy data

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

# stock data

def insert_stock_data(data):
    stocks_data_store.insert_one(data)

def get_stock_data(user_id):
    data = stocks_data_store.find_one({"id": user_id})
    if not data:
        data = DEFAULT_STOCK_DATA
        data["id"] = user_id
        insert_stock_data(data)
    return data 

def get_stock_price(ticker: str):
    ticker = ticker.upper()
    try:
        data = yf.download(tickers = ticker, period = PERIOD, interval = INTERVAL)
        price = dict(data)["Close"][0]
        return round(price, 2)
    except:
        pass

class economy_system(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ["bal", "balance"])
    async def wealth(self, context, member: discord.Member = None):
        if context.author.bot:
            return
        elif not member:
            member = context.author

        # create loading embed
        embed = await context.send(embed = create_embed(f"{member}'s Wealth", {
            "Status": "Loading...",
            "Name": member.mention,
        }, {
            "color": discord_color.gold(),
            "member": member,
        }))

        # get bank & pocket money
        money_data = get_economy_data(member.id)
        if not money_data:
            money_data = DEFAULT_ECONOMY_DATA
            insert_economy_data(money_data)

        bank_money = money_data["bank"]
        pocket_money = money_data["pocket"]

        # get stock money
        stock_data = get_stock_data(member.id)

        stock_money = 0
        for ticker, share_count in stock_data["shares"].items():
            average_price = get_stock_price(ticker)
            if not average_price:
                continue

            stock_money += average_price * share_count

        # update embed
        await embed.edit(embed = create_embed(f"{member}'s Wealth", {
            "Net Worth": "${}".format(round(bank_money + pocket_money + stock_money, 2)),
            "Bank": "${}".format(round(bank_money, 2)),
            "Pocket": "${}".format(round(pocket_money, 2)),
            "Stocks": "${}".format(round(stock_money, 2)),
            "Name": member.mention,
        }, {
            "member": member,
        }))

    @commands.command()
    async def forbes(self, context):
        if context.author.bot:
            return

        # create loading embed
        embed = await context.send(embed = create_embed("Forbes Richest Members", {
            "Status": "Loading list..."
        }, {
            "color": discord_color.gold(),
            "member": context.author,
        }))

        # create richest list
        members_money_data = list(economy_data_store.find({}))
        richest_list = {}
        for member_money_data in members_money_data:   
            user = context.guild.get_member(member_money_data["id"])   
            if not user:
                continue 
                
            pocket_money = member_money_data["pocket"]
            bank_money = member_money_data["bank"]

            # get stock money
            stock_data = get_stock_data(member_money_data["id"])
            stock_money = 0
            for ticker, share_count in stock_data["shares"].items():
                average_price = get_stock_price(ticker)
                stock_money += average_price * share_count
            richest_list[user.name] = round(pocket_money + bank_money + stock_money, 2)
        richest_list = sorted(richest_list.items(), key = lambda x: x[1], reverse = True)

        # create fields
        fields = {}
        for place, data in enumerate(richest_list):
            fields[f"{place + 1}. {data[0]}"] = "${}".format(data[1])
            if place == MAX_FIELDS_FOR_LEADERBOARD_EMBED - 1:
                break

        # update embed
        await embed.edit(embed = create_embed("Forbes Richest Members", fields, {
            "member": context.author,
        }))
    
    @commands.command()
    async def withdraw(self, context, amount: int):
        if context.author.bot:
            return

        amount = round(amount, 2)
        user = context.author

        # create loading embed
        embed = await context.send(embed = create_embed("Withdrawing Money", {
            "Status": "Processing..."
        }, {
            "color": discord_color.gold(),
            "member": user,
        }))

        # handle money
        money_data = get_economy_data(user.id)
        if not money_data:
            money_data = DEFAULT_ECONOMY_DATA
            insert_economy_data(money_data)

        if amount > money_data["bank"]:
            await embed.edit(embed = create_embed(f"ERROR: You do not have enough money in the bank to withdraw ${amount}", {
                "Pocket": "${}".format(round(money_data["pocket"], 2)),
                "Amount to Withdraw": "${}".format(round(amount, 2))
            }, {
                "color": discord_color.red(),
                "member": user,
            }))
            return
        
        money_data["bank"] -= amount
        money_data["pocket"] += amount
        save_economy_data(user.id, money_data)

        # update embed
        await embed.edit(embed = create_embed(f"Withdrew ${amount} from the bank", {
            "Bank": "${}".format(round(money_data["bank"], 2)),
            "Pocket": "${}".format(round(money_data["pocket"], 2)),
            "Amount Withdraw": "${}".format(round(amount, 2)),
        }, {
            "color": discord_color.green(),
            "member": user,
        }))

    @commands.command()
    async def deposit(self, context, amount: int):
        if context.author.bot:
            return

        amount = round(amount, 2)
        user = context.author

        # create loading embed
        embed = await context.send(embed = create_embed("Depositing Money", {
            "Status": "Processing..."
        }, {
            "color": discord_color.gold(),
            "member": user,
        }))

        # handle money
        money_data = get_economy_data(user.id)
        if not money_data:
            money_data = DEFAULT_ECONOMY_DATA
            insert_economy_data(money_data)

        if amount > money_data["pocket"]:
            await embed.edit(embed = create_embed(f"ERROR: You do not have enough money in your pocket to deposit ${amount}", {
                "Bank": "${}".format(round(money_data["bank"], 2)),
                "Pocket": "${}".format(round(money_data["pocket"], 2)),
                "Amount to Withdraw": "${}".format(round(amount, 2))
            }, {
                "color": discord_color.red(),
                "member": user,
            }))
            return
        
        money_data["pocket"] -= amount
        money_data["bank"] += amount
        save_economy_data(user.id, money_data)

        # update embed
        await embed.edit(embed = create_embed(f"Depositing ${amount} into bank", {
            "Bank": "${}".format(round(money_data["bank"], 2)),
            "Pocket": "${}".format(round(money_data["pocket"], 2)),
            "Amount Deposited": "${}".format(round(amount, 2)),
        }, {
            "color": discord_color.green(),
            "member": user,
        }))

    @commands.command()
    async def give(self, context, receiver: discord.Member, amount: int):
        if context.author.bot:
            return

        # create loading embed
        embed = await context.send(embed = create_embed("Giving Money", {
            "Status": "Handing..."
        }, {
            "color": discord_color.gold(),
            "member": context.author,
        }))

        # handle money

        amount = round(amount, 2)
        sender = context.author
        sender_data = get_economy_data(sender.id)
        receiver_data = get_economy_data(receiver.id)

        if sender_data["pocket"] < amount:
            await embed.edit(embed = create_embed(f"ERROR: {sender}, you do not have enough money in your pocket to give to {receiver}", {
                f"{sender.name}'s Pocket": "${}".format(sender_data["pocket"]),
                f"Amount to Give to {receiver}": "${}".format(amount),
            }, {
                "color": discord_color.red(),
                "member": sender,
            }))
            return

        sender_data["pocket"] -= amount
        receiver_data["pocket"] += amount
        save_economy_data(sender.id, sender_data)
        save_economy_data(receiver.id, receiver_data)

        # update embed
        await embed.edit(embed = create_embed(f"{sender} gave ${amount} to {receiver}", {
            f"{sender.name}'s Pocket": "${}".format(sender_data["pocket"]),
            f"{receiver.name}'s Pocket": "${}".format(receiver_data["pocket"]),
            f"Amount Given to {receiver}": "${}".format(amount)
        }, {
            "color": discord_color.green(),
            "member": sender,
        }))

    @commands.command()
    async def wire(self, context, receiver: discord.Member, amount: int):
        if context.author.bot:
            return

        # create loading embed
        embed = await context.send(embed = create_embed("Wiring Money", {
            "Status": "Processing..."
        }, {
            "color": discord_color.gold(),
            "member": context.author,
        }))

        # handle money

        amount = round(amount, 2)
        sender = context.author
        sender_data = get_economy_data(sender.id)
        receiver_data = get_economy_data(receiver.id)

        if sender_data["bank"] < amount:
            await embed.edit(embed = create_embed(f"ERROR: {sender}, you do not have enough money in the bank to give to {receiver}", {
                f"{sender.name}'s Account Balance": "${}".format(round(sender_data["bank"], 2)),
                f"Amount to Wire to {receiver}": "${}".format(round(amount, 2)),
            }, {
                "color": discord_color.red(),
                "member": sender,
            }))
            return

        sender_data["bank"] -= amount
        receiver_data["bank"] += amount
        save_economy_data(sender.id, sender_data)
        save_economy_data(receiver.id, receiver_data)

        # update embed
        await embed.edit(embed = create_embed(f"{sender} wired ${amount} to {receiver}", {
            f"{sender.name}'s Bank Account": "${}".format(round(sender_data["bank"], 2)),
            f"{receiver.name}'s Bank Account": "${}".format(round(receiver_data["bank"], 2)),
            f"Amount Wired to {receiver}": "${}".format(round(amount, 2))
        }, {
            "color": discord_color.green(),
            "member": sender,
        }))

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    async def addmoney(self, context, member: discord.Member, location: str, amount: int = None):
        embed = await context.send(embed = create_embed("Adding Money", {
            "Status": "Printing Money...",
        }, {
            "color": discord_color.gold(),
            "member": context.author,
        }))

        amount = round(amount, 2)
        if location == "pocket" or location == "bank":
            money_data = get_economy_data(member.id)
            money_data[location] += amount
            save_economy_data(member.id, money_data)

            await embed.edit(embed = create_embed(f"Added ${amount} to {member}'s {location}", {
                "Ran By": context.author,
            }, {
                "color": discord_color.green(),
                "member": context.author,
            }))
        else:
            await embed.edit(embed = create_embed(f"ERROR: `{location}` is not a valid location. Choose `pocket` or `bank`", {
                "Ran By": context.author,
            }, {
                "color": discord_color.red(),
                "member": context.author,
            }))

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    async def setmoney(self, context, member: discord.Member, location: str, amount: int = None):
        embed = await context.send(embed = create_embed(f"Changing {member}'s Money", {
            "Status": "Printing Money...",
        }, {
            "color": discord_color.gold(),
            "member": context.author,
        }))

        amount = round(amount, 2)
        if location == "pocket" or location == "bank":
            money_data = get_economy_data(member.id)
            money_data[location] = amount
            save_economy_data(member.id, money_data)

            await embed.edit(embed = create_embed(f"Changed {member}'s {location} to ${amount}", {
                "Ran By": context.author,
            }, {
                "color": discord_color.green(),
                "member": context.author,
            }))
        else:
            await embed.edit(embed = create_embed(f"ERROR: `{location}` is not a valid location. Choose `pocket` or `bank`", {
                "Ran By": context.author,
            }, {
                "color": discord_color.red(),
                "member": context.author,
            }))

    @commands.command(aliases = ["stock", "dd"])
    async def stockinfo(self, context, ticker: str):
        ticker = ticker.upper()
        loading_embed = await context.send(embed = create_embed(f"Loading data for {ticker}...", {}, {
            "color": discord_color.gold(),
            "member": context.author,
        }))

        try:
            chart = None
            ordered_pages = []
            pages = {
                "Table of Contents": {
                    "1 - Table of Contents": f"Sections of accessible data",
                    "2 - Description": "Description of the stock",
                    "3 - Info": "Stock info including but not limited to industry, index, market cap, short float, and sales",
                    "4 - Ratings": "Ratings of the stock by various sources",
                    "5 - News": "The latest news regarding the stock",
                    "6 - Share Holders": "Individual stock owners and companies",
                },
                "Description": {}, 
                "Info": {},
                "Ratings": {},
                "News": {},
                "Share Holders": {},
            }

            stock = finvizfinance(ticker)

            stock.TickerCharts()
            for file_name in os.listdir():
                if file_name == ticker + ".jpg":
                    chart = file_name

            # convert jpg to png
            jpg_image = Image.open(chart)
            jpg_image.save(f"{ticker}.png")
            chart = ticker + ".png"

            pages["Description"]["Description"] = stock.TickerDescription()[0:1021] + "..."
            pages["Info"] = stock.TickerFundament()

            ratings_data = stock.TickerOuterRatings()
            for index, ratings_creator in ratings_data["Outer"].items():
                pages["Ratings"][ratings_creator] = "Rating: {rating} | Price: {price} | Status: {status}".format(
                    rating = ratings_data["Rating"][index],
                    price = ratings_data["Price"][index],
                    status = ratings_data["Status"][index],
                )
                if index == MAX_FIELDS - 1:
                    break

            news_data = stock.TickerNews()
            for index, title in news_data["Title"].items():
                pages["News"][title] = "Date: {date} | Link: {link}".format(
                    date = news_data["Date"][index],
                    link = news_data["Link"][index],
                )

                if index == MAX_FIELDS - 1:
                    break

            owners_data = stock.TickerInsideTrader()
            for index, owner in owners_data["Insider Trading"].items():
                pages["Share Holders"][owner] = "Transaction: {transaction} | Cost: {cost} | Shares: {shares} | Value: {value} | Shares Total: {shares_total} | Date: {date}".format(
                    transaction = owners_data["Transaction"][index],
                    cost = owners_data["Cost"][index],
                    shares = owners_data["#Shares"][index],
                    value = owners_data["Value ($)"][index],
                    shares_total = owners_data["#Shares Total"][index],
                    date = owners_data["Date"][index],
                )
                if index == MAX_FIELDS - 1:
                    break

            # create embeds

            for title, fields in pages.items():
                pages[title] = create_embed(title, fields, {
                    "member": context.author,
                })

            # create ordered pages

            for title, embed in pages.items():
                ordered_pages.append(pages[title])
        except Exception as error_message:
            await loading_embed.edit(embed = create_embed(f"ERROR: Something went wrong when loading data for {ticker}", {
                "Error Message": error_message,
            }, {
                "color": discord_color.red(),
                "member": context.author,
            }))
            return
        else:
            await loading_embed.delete()
            await context.send(file = discord.File(chart, filename = "image.png"), embed = create_embed(f"{ticker} Info", {}, {
                "member": context.author,
                "thumbnail": "attachment://image.png"
            }))

            for file_name in os.listdir():
                if file_name == ticker + ".jpg" or file_name == ticker + ".png":
                    os.remove(file_name)

        # create interactive embed

        EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]
        
        current_page = 0
        new_embed = ordered_pages[current_page]
        new_embed.set_footer(text = f"Page {current_page + 1}/{len(ordered_pages)}", icon_url = "")
        message = await context.send(embed = new_embed)

        for emoji in EMOJIS:
            await message.add_reaction(emoji)

        while True:
            def check_reaction(reaction, user):
                if user == context.author and reaction.message.channel == context.channel and reaction.message.id == message.id:
                    if str(reaction.emoji) in EMOJIS:
                        return True

            chosen_reaction, user = await self.client.wait_for("reaction_add", check = check_reaction)

            for index, emoji in enumerate(EMOJIS):
                if emoji == chosen_reaction.emoji:
                    current_page = index
                    break

            new_embed = ordered_pages[current_page]
            new_embed.set_footer(text = f"Page {current_page + 1}/{len(ordered_pages)}", icon_url = "")
            await message.edit(embed = new_embed)
            await chosen_reaction.remove(user)

def setup(client):
    client.add_cog(economy_system(client))