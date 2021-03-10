"""
MAX_FIELDS_FOR_LEADERBOARD_EMBED = 10
DEFAULT_DATA = {
    "id": None,
    "pocket": 20,
    "bank": 500,
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
import cogs.stock_market as stock_market_module

cluster = MongoClient("mongodb+srv://admin:QZnOT86qe3TQ@cluster0.meksl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
economy_data_store = cluster.discord.economy

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

def save_economy_data(user_id, data):
    economy_data_store.update_one({"id": user_id}, {"$set": data})

def insert_economy_data(data):
    economy_data_store.insert_one(data)

def get_economy_data(user_id):
    data = economy_data_store.find_one({"id": user_id})
    if not data:
        data = DEFAULT_DATA
        insert_economy_data(data)
    return data 

def give_money(user_id, location, amount):
    amount = round(amount, 2)
    economy_data = get_economy_data(user_id)
    economy_data[location] += amount
    save_economy_data(user_id, economy_data)

class economy_system(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ["bal", "balance"])
    async def wealth(self, context, member: discord.Member = None):
        if not member:
            member = context.author

        embed = await context.send(embed = create_embed(f"{member}'s Wealth", {
            "Status": "Loading...",
        }, {
            "color": discord_color.gold(),
            "member": member,
        }))

        # get data
        stats = get_economy_data(member.id)
        bank = round(stats["bank"], 2)
        pocket = round(stats["pocket"], 2)

        # get stock data
        stock_data = stock_market_module.get_stock_data(member.id)
        investing_money = 0
        for ticker, shares in stock_data["shares"].items():
            current_price = stock_market_module.get_price(ticker)
            investing_money += round(shares * current_price, 2)

        # create embed
        await embed.edit(embed = create_embed(f"{member}'s Wealth", {
            "Name": member.mention,
            "Bank": f"${bank}",
            "Pocket": f"${pocket}",
            "Net Worth": f"{round(bank + pocket + investing_money, 2)}"
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
        }))

        # create richest list
        documents = list(economy_data_store.find({}))
        richest_list = {}
        for data in documents:   
            user = context.guild.get_member(data["id"])    
            pocket = data["pocket"]
            bank = data["bank"]
            investing = stock_market_module.get_investing_amount(data["id"])
            richest_list[user.name] = round(pocket + bank + investing, 2)
        richest_list = sorted(richest_list.items(), key = lambda x: x[1], reverse = True)

        # create fields
        fields = {}
        for place, data in enumerate(richest_list):
            fields[f"{place + 1}. {data[0]}"] = f"${round(data[1])}"
            if place == MAX_FIELDS_FOR_LEADERBOARD_EMBED :
                break
            place += 1

        # update embed
        await embed.edit(embed = create_embed("Forbes Richest Members", fields))

    @commands.command()
    async def withdraw(self, context, amount: int):
        amount = round(amount, 2)
        user = context.author
        economy_data = get_economy_data(user.id)
        if amount > round(economy_data["bank"], 2):
            await context.send(embed = create_embed(f"ERROR: You do not have enough money in your bank to withdraw ${amount}", {
                "Bank": "${}".format(round(economy_data["bank"], 2)),
                "Amount to Withdraw": "${}".format(amount)
            }, {
                "color": discord_color.red(),
                "member": user,
            }))
            return
        
        economy_data["bank"] -= amount
        economy_data["pocket"] += amount
        save_economy_data(user.id, economy_data)

        await context.send(embed = create_embed(f"Withdrew ${amount} from the bank", {
            "Bank": "${}".format(round(economy_data["bank"], 2)),
            "Pocket": "${}".format(round(economy_data["pocket"], 2)),
            "Amount Withdraw": "${}".format(amount)
        }, {
            "color": discord_color.green(),
            "member": user,
        }))

    @commands.command()
    async def deposit(self, context, amount: int):
        amount = round(amount, 2)
        user = context.author
        economy_data = get_economy_data(user.id)
        if amount > round(economy_data["pocket"], 2):
            await context.send(embed = create_embed(f"ERROR: You do not have enough money in your pocket to deposit ${amount} into the bank", {
                "Pocket": "${}".format(round(economy_data["pocket"], 2)),
                "Amount to Deposit": "${}".format(amount)
            }, {
                "color": discord_color.red(),
                "member": user,
            }))
            return
        
        economy_data["pocket"] -= amount
        economy_data["bank"] += amount

        save_economy_data(user.id, economy_data)
        await context.send(embed = create_embed(f"Deposited ${amount} from into the bank", {
            "Bank": "${}".format(round(economy_data["bank"], 2)),
            "Pocket": "${}".format(round(economy_data["pocket"], 2)),
            "Amount Deposited": "${}".format(amount)
        }, {
            "color": discord_color.green(),
            "member": user,
        }))

    @commands.command()
    async def give(self, context, receiver: discord.Member, amount: int):
        amount = round(amount, 2)
        sender = context.author
        sender_economy_data = get_economy_data(sender.id)
        receiver_economy_data = get_economy_data(receiver.id)

        if round(sender_economy_data["pocket"], 2) < amount:
            await context.send(embed = create_embed(f"ERROR: {sender}, you do not have enough money to give to {receiver}", {
                f"{sender.name}'s Pocket": "${}".format(round(sender_economy_data["pocket"], 2)),
                f"{receiver.name}'s Pocket": "${}".format(round(receiver_economy_data["pocket"], 2)),
                f"Amount to Give from {sender}'s Pocket to {receiver}'s Pocket": "${}".format(amount)
            }, {
                "color": discord_color.red(),
            }))
            return

        sender_economy_data["pocket"] -= amount
        receiver_economy_data["pocket"] += amount
        save_economy_data(sender.id, sender_economy_data)
        save_economy_data(receiver.id, receiver_economy_data)

        await context.send(embed = create_embed(f"{sender} gave ${amount} to {receiver}", {
            f"{sender.name}'s Pocket": "${}".format(round(sender_economy_data["pocket"], 2)),
            f"{receiver.name}'s Pocket": "${}".format(round(receiver_economy_data["pocket"], 2)),
            f"Amount Given from {sender}'s Pocket to {receiver}'s Pocket": "${}".format(amount)
        }, {
            "color": discord_color.green()
        }))

    @commands.command()
    async def wire(self, context, receiver: discord.Member, amount: int):
        amount = round(amount, 2)
        sender = context.author
        sender_economy_data = get_economy_data(sender.id)
        receiver_economy_data = get_economy_data(receiver.id)

        if round(sender_economy_data["bank"], 2) < amount:
            await context.send(embed = create_embed(f"ERROR: {sender}, you do not have enough money to wire money to {receiver}", {
                f"{sender.name}'s Bank Account": "${}".format(round(sender_economy_data["bank"], 2)),
                f"{receiver.name}'s Bank Account": "${}".format(round(receiver_economy_data["bank"], 2)),
                f"Amount to Give from {sender}'s Bank Account to {receiver}'s Bank Account": "${}".format(amount)
            }, {
                "color": discord_color.red(),
            }))
            return

        sender_economy_data["bank"] -= amount
        receiver_economy_data["bank"] += amount
        save_economy_data(sender.id, sender_economy_data)
        save_economy_data(receiver.id, receiver_economy_data)

        await context.send(embed = create_embed(f"{sender} wired ${amount} to {receiver}", {
            f"{sender.name}'s Bank Account": "${}".format(round(sender_economy_data["bank"], 2)),
            f"{receiver.name}'s Bank Account": "${}".format(round(receiver_economy_data["bank"], 2)),
            f"Amount Given from {sender}'s Bank Account to {receiver}'s Bank Account": "${}".format(amount)
        }, {
            "color": discord_color.green(),
        }))

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    async def addmoney(self, context, member: discord.Member, location: str, amount: int = None):
        amount = round(amount, 2)
        if location == "pocket" or location == "bank":
            give_money(member.id, location, amount)
            await context.send(embed = create_embed(f"SUCCESS: Added ${amount} to {member}'s {location}", {
                "Ran By": context.author.mention,
            }, {
                "color": discord_color.green(),
            }))
        else:
            await context.send(embed = create_embed(f"ERROR: `{location}` is not a valid location. Choose `pocket` or `bank`", {}, {
                "color": discord_color.red()
            }))

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    async def setmoney(self, context, member: discord.Member, location: str, amount: int = None):
        amount = round(amount, 2)
        if location == "pocket" or location == "bank":
            money_data = get_economy_data(member.id)
            money_data[location] = amount
            save_economy_data(member.id, money_data)
            await context.send(embed = create_embed(f"SUCCESS: Set {member}'s {location} to ${amount}", {
                "Ran By": context.author.mention,
            }, {
                "color": discord_color.green(),
            }))
        else:
            await context.send(embed = create_embed(f"ERROR: `{location}` is not a valid location. Choose `pocket` or `bank`", {}, {
                "color": discord_color.red()
            }))

def setup(client):
    client.add_cog(economy_system(client))
"""