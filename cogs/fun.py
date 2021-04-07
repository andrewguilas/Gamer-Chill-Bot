import discord
from discord.ext import commands

import random
import pytz
import random
import asyncio
import asyncpraw
from translate import Translator
from datetime import datetime

reddit = asyncpraw.Reddit(
    client_id = "cTdcYAFeJKqwKg",
    client_secret = "QO0zyzU_pB8voB0nQUvfXIRgqmL02g", 
    password = "6&OB7s4PcCKz&08o",
    user_agent = "gamer-chill-bot",
    username = "Hast1e"
)

async def get_meme():
    subreddit = await reddit.subreddit("memes")
    meme = await subreddit.random()
    return meme.url

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

class fun_commands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ["8ball"], description = "Retrieves a random response to a yes/no question.")
    async def _8ball(self, context, *, question):
        RESPONSES = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes - definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
            "No"
        ]

        await context.send(embed = create_embed({
            "title": random.choice(RESPONSES),
        }))

    @commands.command(aliases = ["dice"], description = "Chooses a random number between 1 and 6 or 1 and the specific number.")
    async def roll(self, context, max_number: int = 6):
        await context.send(embed = create_embed({
            "title": random.randint(1, max_number),
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
                    "title": "You cannot talk in this channel",
                    "color": discord.Color.red()
                }))
                return

            webhook = await channel.create_webhook(name = member.name)
            await webhook.send(message, username = member.name, avatar_url = member.avatar_url)
            await webhook.delete()

            await response.edit(embed = create_embed({
                "title": "User impersonated",
                "color": discord.Color.green()
            }, {
                "Message": message,
                "User": member,
                "Channel": channel
            }))
        except Exception as error_message:
            await context.send(embed = create_embed({
                "title": "Could not impersonate user",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command(description = "Retrieves a random person from the server.")
    async def randomperson(self, context):
        member = random.choice(context.guild.members)
        await context.send(embed = create_embed({
            "title": member.name
        }))

    @commands.command(description = "Retrieves a list of supported languages for the ?translate command.")
    async def languages(self, context):
        await context.send(embed = create_embed({
            "title": "ISO 639-1 Codes",
            "url": "https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes"
        }))

    @commands.command(description = "Translates a different languages to english.")
    async def translate(self, context, language: str, *, text: str):
        response = await context.send(embed = create_embed({
            "title": "Translating...",
            "color": discord.Color.gold()
        }, {
            "Original Text": text,
            "Language": language,
        }))

        try:
            translator = Translator(to_lang = language)
            translation = translator.translate(text)
            await response.edit(embed = create_embed({
                "title": translation,
            }, {
                "Original Text": text,
                "Language": language,
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not translate",
            }, {
                "Error Message": error_message,
                "Original Text": text,
                "Language": language,
            }))

    @commands.command(aliases = ["m", "meme"], description = "Retrieves a random meme from r/memes.")
    async def getmeme(self, context, amount: int = 1):
        MAX_MEMES = 5
        if amount > MAX_MEMES:
            amount = MAX_MEMES

        for _ in range(amount):
            meme = await get_meme()
            await context.send(meme)

def setup(client):
    client.add_cog(fun_commands(client))