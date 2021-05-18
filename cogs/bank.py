import discord
from discord.ext import commands
from helper import get_guild_data, create_embed, get_user_data, attach_prefix_to_number, save_user_data
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
    @commands.guild_only()
    async def bank(self, context):
        response = await context.send(embed=create_embed({
            "title": "Loading bank balance...",
            "color": discord.Color.gold()
        }))

        try:
            guild_data = get_guild_data(context.guild.id)
            balance = guild_data["bank_balance"]
            balance = attach_prefix_to_number(balance, "$")

            await response.edit(embed=create_embed({
                "title": f"Bank Balance: {balance}",
            }))
        except Exception as error_message:
            await response.edit(embed=create_embed({
                "title": "Could not load bank balance",
                "color": discord.Color.red(),
            }, {
                "Error Message": error_message
            }))

def setup(client):
    client.add_cog(bank(client))
