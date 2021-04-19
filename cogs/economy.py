import discord
from discord.ext import commands

from constants import ECONOMY_MAX_FIELDS_FOR_LEADERBOARD_EMBED
from helper import create_embed, get_settings, get_user_data, save_user_data, get_all_user_data

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
            user_data = get_user_data(member.id)
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
            all_user_data = get_all_user_data("money")
            guild_user_data = []
            for data in all_user_data:
                if context.guild.get_member(data["user_id"]):
                    guild_user_data.append(data)

            fields = {}
            for rank, member_data in enumerate(guild_user_data):
                member = context.guild.get_member(member_data["user_id"])
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
            sender_user_data = get_user_data(context.author.id)
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
            reciever_user_data = get_user_data(member.id)
            reciever_user_data["money"] += amount
            sender_user_data["money"] -= amount

            save_user_data(reciever_user_data)
            save_user_data(sender_user_data)

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