import discord
from discord.ext import commands
from discord import Color as discord_color

import random
import pytz
import random
import asyncio
from translate import Translator
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
            inline = True
        )

    embed.timestamp = datetime.now(tz = pytz.timezone("US/Eastern"))

    return embed

class fun_commands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ["8ball"])
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

        await context.send(embed = discord.Embed(
            title = random.choice(RESPONSES)
        ))

    @commands.command()
    async def roll(self, context, max_number: int = 6):
        await context.send(embed = create_embed(random.randint(1, max_number)))

    @commands.command()
    async def choose(self, context, *choices: str):
        await context.send(embed = create_embed(random.choice(choices)))

    @commands.command()
    async def impersonate(self, context, member: discord.Member, channel: discord.TextChannel, *, message: str):
        if not channel.permissions_for(context.author).send_messages:
            await context.send(embed = create_embed("You cannot talk in here", discord_color.red()))
            return

        webhook = await channel.create_webhook(name = member.name)
        await webhook.send(message, username = member.name, avatar_url = member.avatar_url)
        await webhook.delete()
        await context.send(embed = create_embed("Success: Embed created. This message will automatically delete in 3 seconds.", discord_color.green(), {
            "Message": message,
            "User to Impersonate": member,
            "Channel": channel
        }), delete_after = 3)

        webhooks = await context.channel.webhooks()
        for webhook in webhooks:
            await webhook.delete()

    @commands.command()
    async def whohasbigpp(self, context):
        member = random.choice(context.guild.members)
        await context.send(embed = create_embed(f"Legends say, {member.name} has the biggest pp"))

    @commands.command()
    async def whohassmallpp(self, context):
        member = random.choice(context.guild.members)
        await context.send(embed = create_embed(f"{member.name} flashed the smallest pp I've ever seen"))

    @commands.command()
    async def randomperson(self, context):
        member = random.choice(context.guild.members)
        await context.send(embed = create_embed(member.name))

    @commands.command()
    async def languages(self, context):
        embed = create_embed("ISO 639-1 Codes")
        embed.url = "https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes"
        await context.send(embed = embed)

    @commands.command()
    async def translate(self, context, language: str, *, text: str):
        embed = await context.send(embed = create_embed("Translating...", discord_color.gold(), {
            "Original Text": text,
            "Language": language,
        }))

        try:
            translator = Translator(to_lang=language)
            translation = translator.translate(text)
            await embed.edit(embed = create_embed(translation, discord_color.blue(), {
                "Original Text": text,
                "Language": language,
            }))
        except Exception as error_message:
            await embed.edit(embed = create_embed("ERROR: Something went wrong when translating", discord_color.red(), {
                "Error Message": error_message,
                "Original Text": text,
                "Language": language,
            }))

def setup(client):
    client.add_cog(fun_commands(client))