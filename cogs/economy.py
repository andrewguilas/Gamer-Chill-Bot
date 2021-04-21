import discord
from discord.ext import commands

from constants import ECONOMY_MAX_FIELDS_FOR_LEADERBOARD_EMBED
from helper import create_embed, get_settings, get_user_data, save_user_data, get_all_user_data, sort_dictionary
from cogs.stocks import get_price

class economy(commands.Cog, description = "Economy system commands."):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ["bal"], description = "Loads the member's balance.")
    async def balance(self, context, member: discord.Member = None):
        if not member:
            member = context.author

        if member.bot:
            await context.send(embed = create_embed({
                "title": f"{member} is a bot",
                "color": discord.Color.red()
            }))
            return

        response = await context.send(embed = create_embed({
            "title": f"Loading {member}'s balance",
            "color": discord.Color.gold()
        }))

        try:
            user_data = get_user_data(member.id)
            net_worth = 0
            money = round(user_data["money"], 2)
            portfolio = 0

            for order in user_data["stock_orders"]:
                ticker_price = get_price(order["ticker"])
                if ticker_price:
                    portfolio += ticker_price * order["shares"]

            portfolio = round(portfolio, 2)
            net_worth = round(money + portfolio, 2)

            await response.edit(embed = create_embed({
                "title": f"{member}'s Balance: ${net_worth}"
            }, {
                "Bank": f"${money}",
                "Stocks": f"${portfolio}"
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

        all_user_data = get_all_user_data("money")
        richest_list = {}
        for data in all_user_data:
            user = context.guild.get_member(data["user_id"])
            if user:
                net_worth = 0
                money = round(data["money"], 2)
                portfolio = 0

                for order in data["stock_orders"]:
                    ticker_price = get_price(order["ticker"])
                    if ticker_price:
                        portfolio += ticker_price * order["shares"]

                net_worth = round(money + portfolio, 2)
                richest_list[user.name] = net_worth

        richest_list = sort_dictionary(richest_list, True)

        fields = {}
        for rank, member_name in enumerate(richest_list):
            net_worth = richest_list.get(member_name)
            fields[f"{rank + 1}. {member_name}"] = f"${net_worth}"
            if rank == ECONOMY_MAX_FIELDS_FOR_LEADERBOARD_EMBED - 1:
                break

        await response.edit(embed = create_embed({
            "title": "Forbes"
        }, fields))

    @commands.command(description = "Gives a member money.")
    async def give(self, context, member: discord.Member, amount: float):
        if member.bot:
            await context.send(embed = create_embed({
                "title": f"{member} is a bot",
                "color": discord.Color.red()
            }))
            return

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