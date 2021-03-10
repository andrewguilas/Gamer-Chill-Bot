STARTING_POCKET_MONEY = 20
STARTING_BANK_MONEY = 500
ANNOUNCEMENT_CHANNEL = 813757261045563432

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
economy_data_base = cluster.discord.economy
misc_data_base = cluster.discord.misc

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

class lottery(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def lotteryinfo(self, context):
        current_lottery_data = misc_data_base.find_one({"key": "current_lottery"})
        if current_lottery_data:
            lottery_creator = context.guild.get_member(current_lottery_data["creator"])
            ticket_price = current_lottery_data["ticket_price"]
            tickets_circulating = len(current_lottery_data["tickets"])
            await context.send(embed = create_embed("Current Lottery", {
                "Ending": datetime.fromtimestamp(current_lottery_data["timestamp_ending"]),
                "Ticket Price": f"${ticket_price}",
                "Money Pool": "${}".format(tickets_circulating * ticket_price),
                "Creator": lottery_creator and lottery_creator.mention or "Could Not Find",
                "Tickets Circulating": tickets_circulating,
            }))
        else:
            await context.send(embed = create_embed("No Existing Lottery"))

    @commands.command()
    async def buytickets(self, context, tickets: int = 1):
        tickets = round(tickets)
        user_id = context.author.id

        current_lottery_data = misc_data_base.find_one({"key": "current_lottery"})
        ticket_price = current_lottery_data["ticket_price"]
        total_price = round(ticket_price * tickets, 2)

        member_money_data = economy_data_base.find_one({"id": user_id})
        if not member_money_data:
            member_money_data =  {
                "id": user_id,
                "pocket": STARTING_POCKET_MONEY,
                "bank": STARTING_BANK_MONEY
            }
            economy_data_base.insert_one(member_money_data)

        if member_money_data["pocket"] < total_price:
            await context.send(embed = create_embed(f"You do not have enough money to purchase {tickets} ticket(s)", {
                "Pocket Money": "${}".format(member_money_data["pocket"]),
                "Ticket Count": tickets,
                "Ticket Price": f"${ticket_price}",
                "Total Price": f"${total_price}",
            }, {
                "member": context.author,
            }))
            return
        member_money_data["pocket"] -= total_price
        economy_data_base.update_one({"id": user_id}, {"$set": member_money_data})

        tickets_to_add = [user_id] * tickets
        current_lottery_data["tickets"] += tickets_to_add
        tickets_circulating = len(current_lottery_data["tickets"])
        misc_data_base.update_one({"key": "current_lottery"}, {"$set": current_lottery_data})

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

        current_lottery_data = misc_data_base.find_one({"key": "current_lottery"})
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
        
        misc_data_base.insert_one(new_lottery_data)
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
        current_lottery_data = misc_data_base.find_one({"key": "current_lottery"})
        if not current_lottery_data:
            await context.send(embed = create_embed("No Existing Lottery", {}, {
                "color": discord_color.red()
            }))
            return

        winner = None
        winner_id = None
        tickets = current_lottery_data["tickets"]
        while True:
            winner_id = random.choice(tickets)
            winner = context.guild.get_member(winner_id)
            if winner:
                break
        
        announcement_channel = self.client.get_channel(ANNOUNCEMENT_CHANNEL)
        tickets_circulating = len(tickets)
        ticket_price = current_lottery_data["ticket_price"]
        lottery_creator = context.guild.get_member(current_lottery_data["creator"])
        money_pool = tickets_circulating * ticket_price

        member_money_data = economy_data_base.find_one({"id": winner_id})
        member_money_data["bank"] += money_pool
        economy_data_base.update_one({"id": winner_id}, {"$set": member_money_data})

        await announcement_channel.send(embed = create_embed("Lottery Ended", {
            "Winner": f"||{winner.mention}||",
            "Grand Prize": "${}".format(money_pool),
            "Ticket Price": f"${ticket_price}",
            "Creator": lottery_creator and lottery_creator.mention or "Could Not Find",
            "Tickets Circulating": tickets_circulating,
        }))

        misc_data_base.delete_many({"key": "current_lottery"})

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    async def cancellottery(self, context):
        current_lottery_data = misc_data_base.find_one({"key": "current_lottery"})
        if not current_lottery_data:
            await context.send(embed = create_embed("No Existing Lottery", {}, {
                "color": discord_color.red()
            }))
            return

        tickets_to_return = {}
        for ticket_owner_id in current_lottery_data["tickets"]:
            if not tickets_to_return.get(ticket_owner_id):
                tickets_to_return[ticket_owner_id] = 1
            else:
                tickets_to_return[ticket_owner_id] += 1

        for member_id, ticket_count in tickets_to_return.items():
            member_money_data = economy_data_base.find_one({"id": member_id})
            member_money_data["bank"] += ticket_count * current_lottery_data["ticket_price"]
            economy_data_base.update_one({"id": member_id}, {"$set": member_money_data})

        misc_data_base.delete_many({"key": "current_lottery"})

        await context.send(embed = create_embed("Lottery cancelled. All tickets were refunded.", {
            "Ran By": context.author.mention
        }))

def setup(client):
    client.add_cog(lottery(client))