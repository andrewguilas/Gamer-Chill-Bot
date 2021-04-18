import discord
from discord.ext import commands
from pymongo import MongoClient

from constants import ECONOMY_MAX_FIELDS_FOR_LEADERBOARD_EMBED
from secrets import MONGO_TOKEN
from helper import create_embed, get_settings

cluster = MongoClient(MONGO_TOKEN)
economoy_data_store = cluster.discord_revamp.economy

def save_economy_data(data):
    economoy_data_store.update_one({"user_id": data["user_id"]}, {"$set": data})
    
def get_economy_data(user_id: int):
    data = economoy_data_store.find_one({"user_id": user_id}) 
    if not data:
        data = {"user_id": user_id, "money": 0}
        economoy_data_store.insert_one(data)
    return data

class economy(commands.Cog, description = "Economy system commands."):
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
            money = round(user_data["money"], 2)
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
                    money = round(member_data["money"], 2)
                    fields[f"{rank + 1}. {member.name}"] = f"${money}"
                
                if rank == ECONOMY_MAX_FIELDS_FOR_LEADERBOARD_EMBED - 1:
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
    client.add_cog(economy(client))