import discord
from discord.ext import commands
from helper import get_guild_data, save_guild_data, create_embed, get_user_data, attach_prefix_to_number, save_user_data
import pdb

def is_bank_manager():
    def predicate(context):
        if context.guild:
            guild_data = get_guild_data(context.guild.id)
            bank_manager = context.guild.get_member(guild_data["bank_manager"])
            return bank_manager and bank_manager.id == context.author.id
    return commands.check(predicate)

class bank(commands.Cog, description = "Default bank management commands."):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.check_any(is_bank_manager())
    async def bank(self, context):
        response = await context.send(embed=create_embed({
            "title": "Loading bank balance...",
            "color": discord.Color.gold()
        }))

        try:
            guild_data = get_guild_data(context.guild.id)
            await response.edit(embed=create_embed({
                "title": "Bank Balance: ${}".format(guild_data["bank_balance"]),
            }))
        except Exception as error_message:
            await response.edit(embed=create_embed({
                "title": "Could not load bank balance",
                "color": discord.Color.red(),
            }, {
                "Error Message": error_message
            }))

    @commands.command()
    @commands.check_any(is_bank_manager())
    @commands.guild_only()
    async def print(self, context, amount: float):
        response = await context.send(embed=create_embed({
            "title": f"Printing ${amount}",
            "color": discord.Color.gold()
        }))

        try:
            amount = round(amount, 2)
            if amount <= 0:
                await response.edit(embed=create_embed({
                    "title": "Amount must be greater than 0",
                    "color": discord.Color.red(),
                }))
                return

            guild_data = get_guild_data(context.guild.id)
            guild_data["bank_balance"] += amount
            save_guild_data(guild_data)

            await response.edit(embed=create_embed({
                "title": "Bank Balance: ${} (+${})".format(guild_data["bank_balance"], amount),
            }))
        except Exception as error_message:
            await response.edit(embed=create_embed({
                "title": "Could not load bank balance",
                "color": discord.Color.red(),
            }, {
                "Error Message": error_message
            }))

    @commands.command()
    @commands.check_any(is_bank_manager())
    @commands.guild_only()
    async def loan(self, context, member: discord.Member, amount: float):
        response = await context.send(embed=create_embed({
            "title": f"Loading {member} ${amount}",
            "color": discord.Color.gold()
        }))

        try:
            amount = round(amount, 2)
            if amount <= 0:
                await response.edit(embed=create_embed({
                    "title": "Amount must be greater than 0",
                    "color": discord.Color.red(),
                }))
                return

            guild_data = get_guild_data(context.guild.id)
            if guild_data["bank_balance"] < amount:
                await response.edit(embed=create_embed({
                    "title": "The bank does not have enough money to loan",
                    "color": discord.Color.red(),
                }))
                return

            user_data = get_user_data(member.id)
            user_data["money"] += amount
            save_user_data(user_data)

            guild_data["bank_balance"] -= amount
            save_guild_data(guild_data)

            await response.edit(embed=create_embed({
                "title": f"Loaned {member} ${amount}",
            }, {
                f"{member}'s Balance": "${}".format(round(user_data["money"], 2)),
                "Bank Balance": "${}".format(round(guild_data["bank_balance"], 2))
            }))
        except Exception as error_message:
            await response.edit(embed=create_embed({
                "title": "Could not loan {member} ${amount}",
                "color": discord.Color.red(),
            }, {
                "Error Message": error_message
            }))

    @commands.command()
    @commands.check_any(is_bank_manager())
    @commands.guild_only()
    async def fine(self, context, member: discord.Member, amount: float):
        response = await context.send(embed=create_embed({
            "title": f"Fining {member} ${amount}",
            "color": discord.Color.gold()
        }))

        try:
            amount = round(amount, 2)
            if amount <= 0:
                await response.edit(embed=create_embed({
                    "title": "Amount must be greater than 0",
                    "color": discord.Color.red(),
                }))
                return

            user_data = get_user_data(member.id)
            user_data["money"] -= amount
            save_user_data(user_data)

            guild_data = get_guild_data(context.guild.id)
            guild_data["bank_balance"] += amount
            save_guild_data(guild_data)

            await response.edit(embed=create_embed({
                "title": f"Fined {member} ${amount}",
            }, {
                f"{member}'s Balance": "${}".format(round(user_data["money"], 2)),
                "Bank Balance": "${}".format(guild_data["bank_balance"])
            }))
        except Exception as error_message:
            await response.edit(embed=create_embed({
                "title": "Could not fine {member} ${amount}",
                "color": discord.Color.red(),
            }, {
                "Error Message": error_message
            }))

def setup(client):
    client.add_cog(bank(client))
