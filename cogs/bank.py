import discord
from discord.ext import commands

class bank(commands.Cog, description = "Default bank management commands."):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.guild_only()
    async def test(self, context):
        await context.send("hey")

def setup(client):
    client.add_cog(bank(client))
