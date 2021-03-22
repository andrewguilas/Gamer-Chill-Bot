MAX_CACHED_MEMES = 10
MIN_CACHED_MEMES = 5

# discord
import discord
from discord import Color as discord_color
from discord.ext import commands, tasks

# embed
import pytz
from datetime import datetime

import asyncpraw

reddit = asyncpraw.Reddit(
    client_id = "cTdcYAFeJKqwKg",
    client_secret = "QO0zyzU_pB8voB0nQUvfXIRgqmL02g", 
    password = "6&OB7s4PcCKz&08o",
    user_agent = "gamer-chill-bot",
    username = "Hast1e"
)

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

    if info.get("member"):
        embed.set_author(name = info["member"], icon_url = info["member"].avatar_url)

    return embed

async def get_meme():
    subreddit = await reddit.subreddit("memes")
    meme = await subreddit.random()
    return meme.url

class meme(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.cached_memes = []

    @commands.command(aliases = ["meme", "m"])
    @commands.cooldown(1, 1, commands.BucketType.member)
    async def getmeme(self, context, amount: int = 1):
        if amount > 3:
            amount = 3

        for _ in range(amount):
            meme = len(self.cached_memes) > 0 and self.cached_memes[0] or await get_meme()
            await context.send(meme)

            if len(self.cached_memes) > 0:
                self.cached_memes.pop(0)

            if len(self.cached_memes) < MIN_CACHED_MEMES:
                for _ in range(MAX_CACHED_MEMES - len(self.cached_memes)):
                    self.cached_memes.append(await get_meme())

    @commands.command()
    async def getcachedmemes(self, context):
        fields = {}
        for index, meme in enumerate(self.cached_memes):
            fields[f"File {index}"] = meme

        await context.send(embed = create_embed("Cached Memes", fields, {
            "member": context.author
        }))

def setup(client):
    client.add_cog(meme(client))