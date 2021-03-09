ANNOUNCEMENT_CHANNEL = 813757261045563432
UPDATE_TIME = 60

# discord
import discord
from discord import Color as discord_color
from discord.ext import commands, tasks

# embed
import pytz
from datetime import datetime

# other
import random
import time
from collections import Counter
from pymongo import MongoClient
import cogs.economy_system as economy_system

cluster = MongoClient("mongodb+srv://admin:QZnOT86qe3TQ@cluster0.meksl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
misc_data_store = cluster.discord.misc

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

def delete_lottery_data():
    misc_data_store.delete_many({"key": "current_lottery"})

def save_lottery_data(data):
    misc_data_store.update_one({"key": "current_lottery"}, {"$set": data})
    
def insert_lottery_data(data):
    misc_data_store.insert_one(data)

def get_lottery_data():
    return misc_data_store.find_one({"key": "current_lottery"}) 

class lottery(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.check_lottery_duration.start()

    def cog_unload(self):
        self.check_lottery_duration.cancel()


    def cog_load(self):
        self.check_lottery_duration.start()

    @tasks.loop(seconds = UPDATE_TIME)
    async def check_lottery_duration(self):
        await self.client.wait_until_ready()

        guild = self.client.guilds[0]
        current_lottery_data = get_lottery_data()

        if not current_lottery_data or time.time() < current_lottery_data["timestamp_ending"]:
            return

        announcement_channel = self.client.get_channel(ANNOUNCEMENT_CHANNEL)
        tickets = current_lottery_data["tickets"]
        tickets_circulating = len(tickets)
        ticket_price = current_lottery_data["ticket_price"]
        lottery_creator = guild.get_member(current_lottery_data["creator"])
        money_pool = tickets_circulating * ticket_price

        if tickets_circulating == 0:
            await announcement_channel.send(embed = create_embed("Lottery Ended", {
                "Winner": "None",
                "Grand Prize": "${}".format(money_pool),
                "Ticket Price": f"${ticket_price}",
                "Creator": lottery_creator and lottery_creator.mention or "Could Not Find",
                "Tickets Circulating": tickets_circulating,
            }))
            delete_lottery_data()
            return

        winner = None
        winner_id = None
        while True:
            winner_id = random.choice(tickets)
            winner = guild.get_member(winner_id)
            if winner:
                break

        member_money_data = economy_system.get_economy_data(winner_id)
        member_money_data["bank"] += money_pool
        economy_system.save_economy_data(winner_id, member_money_data)

        await announcement_channel.send(embed = create_embed("Lottery Ended", {
            "Winner": f"||{winner.mention}||",
            "Grand Prize": "${}".format(money_pool),
            "Ticket Price": f"${ticket_price}",
            "Creator": lottery_creator and lottery_creator.mention or "Could Not Find",
            "Tickets Circulating": tickets_circulating,
        }))

        delete_lottery_data()

    @commands.command()
    async def lotteryinfo(self, context):
        current_lottery_data = get_lottery_data()
        if current_lottery_data:
            lottery_creator = context.guild.get_member(current_lottery_data["creator"])
            ticket_price = current_lottery_data["ticket_price"]
            tickets_circulating = len(current_lottery_data["tickets"])
            tickets_bought = Counter(current_lottery_data["tickets"])[context.author.id]
            await context.send(embed = create_embed("Current Lottery", {
                "Ending": datetime.fromtimestamp(current_lottery_data["timestamp_ending"]),
                "Ticket Price": f"${ticket_price}",
                "Money Pool": "${}".format(tickets_circulating * ticket_price),
                "Creator": lottery_creator and lottery_creator.mention or "Could Not Find",
                "Tickets Circulating": tickets_circulating,
                "Tickets Bought": tickets_bought,
            }))
        else:
            await context.send(embed = create_embed("No Existing Lottery"))

    @commands.command()
    async def buytickets(self, context, tickets: int = 1):
        tickets = round(tickets)
        user_id = context.author.id

        current_lottery_data = get_lottery_data()
        ticket_price = current_lottery_data["ticket_price"]
        total_price = round(ticket_price * tickets, 2)

        member_money_data = economy_system.get_economy_data(user_id)
        if member_money_data["pocket"] < total_price:
            await context.send(embed = create_embed(f"ERROR: You do not have enough money to purchase {tickets} ticket(s)", {
                "Pocket Money": "${}".format(member_money_data["pocket"]),
                "Ticket Count": tickets,
                "Ticket Price": f"${ticket_price}",
                "Total Price": f"${total_price}",
            }, {
                "color": discord_color.red(),
                "member": context.author,
            }))
            return
        member_money_data["pocket"] -= total_price
        economy_system.save_economy_data(user_id, member_money_data)

        tickets_to_add = [user_id] * tickets
        current_lottery_data["tickets"] += tickets_to_add
        tickets_circulating = len(current_lottery_data["tickets"])
        save_lottery_data(current_lottery_data)

        await context.send(embed = create_embed(f"SUCCESS: Bought {tickets} tickets", {
            "Tickets Bought": tickets,
            "Ticket Price": f"${ticket_price}",
            "Total Cost": f"${total_price}",
            "Money Pool": "${}".format(tickets_circulating * ticket_price),
            "Tickets Circulating": tickets_circulating,
        }, {
            "color": discord_color.green(),
            "member": context.author,
        }))

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    async def createlottery(self, context, timestamp_ending: int, ticket_price: int):
        lottery_creator = context.author
        ticket_price = round(ticket_price, 2)
        date_ending = datetime.fromtimestamp(timestamp_ending)
        if not date_ending:
            await context.send(embed = create_embed("ERROR: Could not create lottery", {
                "Error Message": f"{timestamp_ending} is not a valid epoch time stamp"
            }, {
                "color": discord_color.red()
            }))
            return

        current_lottery_data = get_lottery_data()
        if current_lottery_data:
            await context.send(embed = create_embed("ERROR: Could not create lottery", {
                "Error Message": "There is an existing lottery. Type `?endlottery` or `cancellottery` to resolve.",
            }, {
                "color": discord_color.red()
            }))
            return

        new_lottery_data =  {
            "key": "current_lottery",
            "timestamp_ending": timestamp_ending,
            "ticket_price": ticket_price,
            "creator": lottery_creator.id,
            "tickets": [],
        }

        insert_lottery_data(new_lottery_data)

        await context.send(embed = create_embed("Lottery Created", {
            "Creator": lottery_creator.mention,
            "Ending": date_ending,
            "Ticket Price": f"${ticket_price}"
        }, {
            "color": discord_color.green(),
        }))

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    async def endlottery(self, context):
        announcement_channel = self.client.get_channel(ANNOUNCEMENT_CHANNEL)
        current_lottery_data = get_lottery_data()
        if not current_lottery_data:
            await context.send(embed = create_embed("No Existing Lottery", {}, {
                "color": discord_color.red()
            }))
            return

        winner = None
        winner_id = None
        tickets = current_lottery_data["tickets"]
        tickets_circulating = len(tickets)
        ticket_price = current_lottery_data["ticket_price"]
        lottery_creator = context.guild.get_member(current_lottery_data["creator"])
        money_pool = tickets_circulating * ticket_price

        if tickets_circulating == 0:
            await announcement_channel.send(embed = create_embed("Lottery Ended", {
                "Winner": "None",
                "Grand Prize": "${}".format(money_pool),
                "Ticket Price": f"${ticket_price}",
                "Creator": lottery_creator and lottery_creator.mention or "Could Not Find",
                "Tickets Circulating": tickets_circulating,
            }))
            delete_lottery_data()
            return

        while True:
            winner_id = random.choice(tickets)
            winner = context.guild.get_member(winner_id)
            if winner:
                break

        member_money_data = economy_system.get_economy_data(winner_id)
        member_money_data["bank"] += money_pool
        economy_system.save_economy_data(winner_id, member_money_data)

        await announcement_channel.send(embed = create_embed("Lottery Ended", {
            "Winner": f"||{winner.mention}||",
            "Grand Prize": "${}".format(money_pool),
            "Ticket Price": f"${ticket_price}",
            "Creator": lottery_creator and lottery_creator.mention or "Could Not Find",
            "Tickets Circulating": tickets_circulating,
        }))

        delete_lottery_data()

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    async def cancellottery(self, context):
        current_lottery_data = misc_data_store.find_one({"key": "current_lottery"})
        if not current_lottery_data:
            await context.send(embed = create_embed("No Existing Lottery", {}, {
                "color": discord_color.red()
            }))
            return

        ticket_counts = Counter(current_lottery_data["tickets"])
        for member_id, ticket_count in ticket_counts.items():
            member_money_data = economy_system.get_economy_data(member_id)
            member_money_data["bank"] += ticket_count * current_lottery_data["ticket_price"]
            economy_system.save_economy_data(member_id, member_money_data)

        delete_lottery_data()

        await context.send(embed = create_embed("Lottery cancelled. All tickets were refunded.", {
            "Ran By": context.author.mention
        }))

def setup(client):
    client.add_cog(lottery(client))