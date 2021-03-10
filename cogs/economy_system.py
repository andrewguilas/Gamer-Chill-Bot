STARTING_POCKET_MONEY = 20
STARTING_BANK_MONEY = 500
MAX_FIELDS_FOR_LEADERBOARD_EMBED = 10

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

cluster = MongoClient("mongodb+srv://admin:QZnOT86qe3TQ@cluster0.meksl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
economy = cluster.discord.economy

def create_embed(title, color = discord_color.blue(), fields = {}, user = None):
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

def save_data(user_id, data):
    economy.update_one({"id": user_id}, {"$set": data})

def insert_data(data):
    economy.insert_one(data)

def get_data(user_id):
    data = economy.find_one({"id": user_id})
    if not data:
        data =  {
            "id": user_id,
            "pocket": STARTING_POCKET_MONEY,
            "bank": STARTING_BANK_MONEY
        }
        insert_data(data)
    return data 

def give_money(user_id, location, amount):
    # get data / set default data
    amount = round(amount, 2)
    stats = get_data(user_id)

    # add money
    pocket = stats["pocket"]
    bank = stats["bank"]

    if location == "pocket":
        pocket += amount
    else:
        bank += amount

    # save data
    save_data(user_id, {
        "pocket": pocket,
        "bank": bank
    })

class economy_system(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def pocket(self, context, member: discord.Member = None):
        if not member:
            member = context.author

        # get data
        stats = get_data(member.id)
        pocket = round(stats["pocket"], 2)

        # create embed
        await context.send(embed = create_embed(f"{member}'s pocket", None, {
            "Name": member.mention,
            "Amount": f"${pocket}"
        }, member))

    @commands.command()
    async def bank(self, context, member: discord.Member = None):
        if not member:
            member = context.author

        # get data
        stats = get_data(member.id)
        bank = round(stats["bank"], 2)

        # create embed
        await context.send(embed = create_embed(f"{member}'s Bank Account", None, {
            "Name": member.mention,
            "Amount": f"${bank}"
        }, member))

    @commands.command()
    async def wealth(self, context, member: discord.Member = None):
        if not member:
            member = context.author

        # get data
        stats = get_data(member.id)
        bank = round(stats["bank"], 2)
        pocket = round(stats["pocket"], 2)

        # create embed
        await context.send(embed = create_embed(f"{member}'s Wealth", None, {
            "Name": member.mention,
            "Bank": f"${bank}",
            "Pocket": f"${pocket}",
            "Net Worth": f"{round(bank + pocket, 2)}"
        }, member))

    @commands.command()
    async def forbes(self, context):
        if context.author.bot:
            return

        # create loading embed
        embed = await context.send(embed = create_embed("Forbes Richest Members", discord_color.gold(), {
            "Status": "Loading list..."
        }))

        # create richest list
        documents = list(economy.find({}))
        richest_list = {}
        for data in documents:   
            user = context.guild.get_member(data["id"])    
            richest_list[user.name] = round(data["pocket"] + data["bank"], 2)
        richest_list = sorted(richest_list.items(), key = lambda x: x[1], reverse = True)

        # create fields
        fields = {}
        for place, data in enumerate(richest_list):
            fields[f"{place + 1}. {data[0]}"] = f"${round(data[1])}"
            if place == MAX_FIELDS_FOR_LEADERBOARD_EMBED :
                break
            place += 1

        # update embed
        await embed.edit(embed = create_embed("Forbes Richest Members", None, fields))

    @commands.command()
    async def withdraw(self, context, amount: int):
        amount = round(amount, 2)
        user = context.author
        data = get_data(user.id)
        if amount > round(data["bank"], 2):
            await context.send(embed = create_embed(f"ERROR: You do not have enough money in your bank to withdraw ${amount}", discord_color.red(), {
                "Bank": round(data["bank"], 2),
                "Pocket": round(data["pocket"], 2),
                "Amount to Withdraw": amount
            }))
            return
        
        data["bank"] -= amount
        data["pocket"] += amount

        save_data(user.id, data)
        await context.send(embed = create_embed(f"Withdrew ${amount} from the bank", discord_color.green(), {
            "Bank": round(data["bank"], 2),
            "Pocket": round(data["pocket"], 2),
            "Amount Withdraw": amount
        }, user))

    @commands.command()
    async def deposit(self, context, amount: int):
        amount = round(amount, 2)
        user = context.author
        data = get_data(user.id)
        if amount > round(data["pocket"], 2):
            await context.send(embed = create_embed(f"ERROR: You do not have enough money in your pocket to deposit ${amount} into the bank", discord_color.red(), {
                "Bank": round(data["bank"], 2),
                "Pocket": round(data["pocket"], 2),
                "Amount to Deposit": amount
            }))
            return
        
        data["pocket"] -= amount
        data["bank"] += amount

        save_data(user.id, data)
        await context.send(embed = create_embed(f"Deposited ${amount} from into the bank", discord_color.green(), {
            "Bank": round(data["bank"], 2),
            "Pocket": round(data["pocket"], 2),
            "Amount Deposited": amount
        }, user))

    @commands.command()
    async def give(self, context, receiver: discord.Member, amount: int):
        amount = round(amount, 2)
        sender = context.author
        sender_data = get_data(sender.id)
        receiver_data = get_data(receiver.id)

        if round(sender_data["pocket"], 2) < amount:
            await context.send(embed = create_embed(f"ERROR: {sender}, you do not have enough money to give to {receiver}", discord_color.red(), {
                f"{sender.name}'s Pocket": round(sender_data["pocket"], 2),
                f"{receiver.name}'s Pocket": round(receiver_data["pocket"], 2),
                f"Amount to Give from {sender}'s Pocket to {receiver}'s Pocket": amount
            }))
            return

        sender_data["pocket"] -= amount
        receiver_data["pocket"] += amount
        save_data(sender.id, sender_data)
        save_data(receiver.id, receiver_data)

        await context.send(embed = create_embed(f"{sender} gave ${amount} to {receiver}", discord_color.green(), {
            f"{sender.name}'s Pocket": "${}".format(round(sender_data["pocket"], 2)),
            f"{receiver.name}'s Pocket": "${}".format(round(receiver_data["pocket"], 2)),
            f"Amount Given from {sender}'s Pocket to {receiver}'s Pocket": "${}".format(amount)
        }))

    @commands.command()
    async def wire(self, context, receiver: discord.Member, amount: int):
        amount = round(amount, 2)
        sender = context.author
        sender_data = get_data(sender.id)
        receiver_data = get_data(receiver.id)

        if round(sender_data["bank"], 2) < amount:
            await context.send(embed = create_embed(f"ERROR: {sender}, you do not have enough money to wire money to {receiver}", discord_color.red(), {
                f"{sender.name}'s Bank Account": round(sender_data["bank"], 2),
                f"{receiver.name}'s Bank Account": round(receiver_data["bank"], 2),
                f"Amount to Give from {sender}'s Bank Account to {receiver}'s Bank Account": amount
            }))
            return

        sender_data["bank"] -= amount
        receiver_data["bank"] += amount
        save_data(sender.id, sender_data)
        save_data(receiver.id, receiver_data)

        await context.send(embed = create_embed(f"{sender} wired ${amount} to {receiver}", discord_color.green(), {
            f"{sender.name}'s Bank Account": "${}".format(round(sender_data["bank"], 2)),
            f"{receiver.name}'s Bank Account": "${}".format(round(receiver_data["bank"], 2)),
            f"Amount Given from {sender}'s Bank Account to {receiver}'s Bank Account": "${}".format(amount)
        }))

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    async def addmoney(self, context, member: discord.Member, location: str, amount: int = None):
        amount = round(amount, 2)
        if location == "pocket" or location == "bank":
            give_money(member.id, location, amount)
            await context.send(embed = create_embed(f"Added ${amount} to {member}'s {location}"))
        else:
            await context.send(embed = create_embed(f"ERROR: `{location}` is not a valid location. Choose `pocket` or `bank`"))

def setup(client):
    client.add_cog(economy_system(client))