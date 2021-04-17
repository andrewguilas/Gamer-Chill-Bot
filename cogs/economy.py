MAX_FIELDS_FOR_LEADERBOARD_EMBED = 10

import discord
from discord.ext import commands, tasks
from datetime import datetime
from pymongo import MongoClient
import time
import math

cluster = MongoClient("mongodb+srv://admin:QZnOT86qe3TQ@cluster0.meksl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
economoy_data_store = cluster.discord_revamp.economy
settings_data_store = cluster.discord_revamp.settings

def get_settings(guild_id: int):
    data = settings_data_store.find_one({"guild_id": guild_id}) 
    if not data:
        data = {"guild_id": guild_id}
        settings_data_store.insert_one(data)
    return data

def save_economy_data(data):
    economoy_data_store.update_one({"user_id": data["user_id"]}, {"$set": data})
    
def get_economy_data(user_id: int):
    data = economoy_data_store.find_one({"user_id": user_id}) 
    if not data:
        data = {"user_id": user_id, "money": 0}
        economoy_data_store.insert_one(data)
    return data

def create_embed(info: {} = {}, fields: {} = {}):
    embed = discord.Embed(
        title = info.get("title") or "",
        description = info.get("description") or "",
        colour = info.get("color") or discord.Color.blue(),
        url = info.get("url") or "",
    )

    for name, value in fields.items():
        embed.add_field(name = name, value = value, inline = info.get("inline") or False)

    if info.get("author"):
        embed.set_author(name = info.author.name, url = info.author.mention, icon_url = info.author.avatar_url)
    if info.get("footer"):
        embed.set_footer(text = info.footer)
    if info.get("image"):
        embed.set_image(url = info.url)
    if info.get("thumbnail"):
        embed.set_thumbnail(url = info.thumbnail)
    
    return embed

class subscriptions(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ["bal"], description = "Loads the member's balance.")
    async def balance(self, context, member: discord.Member = None):
        if not member:
            member = context.author

        response = await context.send(embed = create_embed({
            "title": f"Loading {member}'s balance",
            "color": discord.Color.gold()
        }))

        try:
            user_data = get_economy_data(member.id)
            money = user_data["money"]
            await response.edit(embed = create_embed({
                "title": f"{member}'s Balance: ${money}"
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not load {member}'s balance",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command(description = "Retrieves the leaderboard for the richest people in the server.")
    async def forbes(self, context):
        response = await context.send(embed = create_embed({
            "title": f"Loading Forbes...",
            "color": discord.Color.gold()
        }))

        try:
            members_in_server_data = economoy_data_store.find().sort("money", -1)
            fields = {}
            for rank, member_data in enumerate(members_in_server_data):
                member = context.guild.get_member(member_data["user_id"])
                if member:
                    money = member_data["money"]
                    fields[f"{rank + 1}. {member.name}"] = f"${money}"
                
                if rank == MAX_FIELDS_FOR_LEADERBOARD_EMBED - 1:
                    break
        
                await response.edit(embed = create_embed({
                    "title": "Forbes"
                }, fields))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not load Forbes...",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command(description = "Gives a member money.")
    async def give(self, context, member: discord.Member, amount: float):
        response = await context.send(embed = create_embed({
            "title": f"Giving {member} ${amount}",
            "color": discord.Color.gold()
        }))

        try:
            # check if money is greater than $0.00
            if amount <= 0:
                await response.edit(embed = create_embed({
                    "title": f"${amount} is not greater than $0.00",
                    "color": discord.Color.red()
                }))
                return

            # check if sender has enough money
            sender_user_data = get_economy_data(context.author.id)
            sender_money = sender_user_data["money"]
            if sender_money < amount:
                await response.edit(embed = create_embed({
                    "title": f"You do not have ${amount}",
                    "color": discord.Color.red()
                }, {
                    "Balance": f"${sender_money}"
                }))
                return

            # run transaction
            reciever_user_data = get_economy_data(member.id)

            reciever_user_data["money"] += amount
            sender_user_data["money"] -= amount

            save_economy_data(reciever_user_data)
            save_economy_data(sender_user_data)

            # response
            await response.edit(embed = create_embed({
                "title": f"Gave {member} ${amount}"
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not give {member} ${amount}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

def setup(client):
    client.add_cog(subscriptions(client))