import discord
from discord.ext import commands

import random
import asyncpraw
from datetime import datetime
import os

from helper import create_embed
from constants import EIGHTBALL_RESPONSES, MAX_MEMES, MEME_SUBREDDIT

reddit = asyncpraw.Reddit(
    client_id = os.getenv("GCB_REDDIT_CLIENT_ID"),
    client_secret = os.getenv("GCB_REDDIT_CLIENT_SECRET"),
    password = os.getenv("GCB_REDDIT_PASSWORD"),
    user_agent = os.getenv("GCB_REDDIT_USER_AGENT"),
    username = os.getenv("GCB_REDDIT_USERNAME"),
)

async def get_meme():
    subreddit = await reddit.subreddit(MEME_SUBREDDIT)
    meme = await subreddit.random()
    return meme.url

class fun(commands.Cog, description = "Fun commands."):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ["8ball"], description = "Retrieves a random response to a yes/no question.")
    async def eightball(self, context, *, question: str):
        response = await context.send(embed = create_embed({
            "title": "Loading response...",
            "color": discord.Color.gold()   
        }))

        try:
            answer = random.choice(EIGHTBALL_RESPONSES)
            await response.edit(embed = create_embed({
                "title": answer
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not load response",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message,
                "Question": question,
            }))

    @commands.command(aliases = ["dice"], description = "Chooses a random number between 1 and 6 or 1 and the specific number.")
    async def roll(self, context, max_number: int = 6):
        response = await context.send(embed = create_embed({
            "title": f"Rolling a die of {max_number}",
            "color": discord.Color.gold()
        }))

        try:
            random_number = random.randint(1, max_number)
            await response.edit(embed = create_embed({
                "title": random_number,
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not roll a die of {max_number}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command(aliases = ["become"], description = "Sends a message disguised as the member.")
    async def impersonate(self, context, member: discord.Member, channel: discord.TextChannel, *, message: str):
        response = await context.send(embed = create_embed({
            "title": "Impersonaitng user...",
            "color": discord.Color.gold()
        }))
        
        try:
            if not channel.permissions_for(context.author).send_messages:
                await response.edit(embed = create_embed({
                    "title": f"You cannot talk in {channel}",
                    "color": discord.Color.red()
                }))
                return

            webhook = await channel.create_webhook(name = member.name)
            await webhook.send(message, username = member.name, avatar_url = member.avatar_url)
            await webhook.delete()

            await response.edit(embed = create_embed({
                "title": f"Impersonated {member} in {channel}",
                "color": discord.Color.green()
            }, {
                "Message": message
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not impersonate user",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command(description = "Retrieves a random person from the server.")
    async def randomperson(self, context):
        response = await context.send(embed = create_embed({
            "title": f"Choosing random person...",
            "color": discord.Color.gold()
        }))

        try:
            random_member = random.choice(context.guild.members)
            await response.edit(embed = create_embed({
                "title": random_member
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not choose a random person",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command(aliases = ["m", "meme"], description = "Retrieves a random meme from r/memes.")
    async def getmeme(self, context, amount: int = 1):
        try:
            if amount > MAX_MEMES:
                amount = MAX_MEMES

            for _ in range(amount):
                meme = await get_meme()
                await context.send(meme)
        except Exception as error_message:
            await context.send(embed = create_embed({
                "title": f"Could not retrieve meme",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

def setup(client):
    client.add_cog(fun(client))
