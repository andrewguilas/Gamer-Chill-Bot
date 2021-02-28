JOIN_EMOJI = "🟩"
MIN_PLAYERS = 2
LOBBY_TIME = 30
UPDATE_DELAY = 1

import discord
from discord.ext import commands
from discord import Color as discord_color

import asyncio
import pytz
from datetime import datetime

def create_embed(title, color = discord_color.blue(), fields = {}):
    embed = discord.Embed(
        title = title,
        colour = color or discord_color.blue()
    )

    for name, value in fields.items():
        embed.add_field(
            name = name,
            value = value,
            inline = False
        )

    embed.timestamp = datetime.now(tz = pytz.timezone("US/Eastern"))

    return embed

def get_time():
    return datetime.now().timestamp()

class uno(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def uno(self, context):
        # get players

        players = []
        time_started = get_time()

        embed = await context.send(embed = create_embed("Uno", None, {
            "Status": f"Awaiting players. React to join. Starting in {30 - round(get_time() - time_started)} seconds.",
            "Players": players
        }))
        await embed.add_reaction(JOIN_EMOJI)

        while True:
            await asyncio.sleep(UPDATE_DELAY)

            if round(get_time() - time_started) >= 30:
                break
                
            players = await embed.reactions[0].users().flatten()

            await embed.edit(embed = create_embed("Uno", None, {
                "Status": f"Awaiting players. React to join. Starting in {round(get_time() - time_started)} seconds.",
                 "Players": players
            }))

        # Setup game

        if len(players) < MIN_PLAYERS:
            await embed.edit(embed = create_embed("Uno", discord_color.gold(), {
                "Status": f"There are not enough players to start the game.",
                "Players": players
            }))
            return

        await embed.edit(embed = create_embed("Uno", None, {
            "Status": f"Setting up game",
            "Players": players
        }))

def setup(client):
    client.add_cog(uno(client))