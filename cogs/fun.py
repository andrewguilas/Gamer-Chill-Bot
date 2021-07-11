import discord
from discord.ext import commands
import random
import asyncpraw
import os
import dotenv
from helper import create_embed
from constants import EIGHTBALL_RESPONSES, MAX_MEMES, MEME_SUBREDDIT

dotenv.load_dotenv('.env')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_PASSWORD = os.getenv('REDDIT_PASSWORD')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')
REDDIT_USERNAME = os.getenv('REDDIT_USERNAME')

reddit = asyncpraw.Reddit(
    client_id = os.getenv('REDDIT_CLIENT_ID'),
    client_secret = os.getenv('REDDIT_CLIENT_SECRET'),
    password = os.getenv('REDDIT_PASSWORD'),
    user_agent = os.getenv('REDDIT_USER_AGENT'),
    username = os.getenv('REDDIT_USERNAME'),
)

async def get_meme():
    subreddit = await reddit.subreddit(MEME_SUBREDDIT)
    meme = await subreddit.random()
    return meme.url

class fun(commands.Cog, description = 'Fun commands.'):
    def __init__(self, client):
        self.client = client
        self.recent_memes = []

    @commands.command(aliases = ['8ball'])
    async def eightball(self, context, *, question: str):
        response = await context.send(embed=create_embed({
            'title': 'Loading response...',
            'color': discord.Color.gold()   
        }))

        try:
            answer = random.choice(EIGHTBALL_RESPONSES)
            await response.edit(embed=create_embed({
                'title': answer
            }))
        except Exception as error_message:
            await response.edit(embed=create_embed({
                'title': 'Could not load response',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message,
                'Question': question,
            }))

            print('ERROR: Could not roll 8ball')
            print(error_message)

    @commands.command()
    async def roll(self, context, max_number: int = 6):
        response = await context.send(embed=create_embed({
            'title': f'Rolling a die of {max_number}',
            'color': discord.Color.gold()
        }))

        try:
            random_number = random.randint(1, max_number)
            await response.edit(embed=create_embed({
                'title': random_number,
            }))
        except Exception as error_message:
            await response.edit(embed=create_embed({
                'title': f'Could not roll a die of {max_number}',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))

            print('ERROR: Could not roll a dice')
            print(error_message)

    @commands.command()
    @commands.guild_only()
    async def impersonate(self, context, member: discord.Member, channel: discord.TextChannel, *, message: str):
        response = await context.send(embed=create_embed({
            'title': 'Impersonaitng user...',
            'color': discord.Color.gold()
        }))
        
        try:
            if not channel.permissions_for(context.author).send_messages:
                await response.edit(embed=create_embed({
                    'title': f'You cannot talk in {channel}',
                    'color': discord.Color.red()
                }))
                return

            webhook = await channel.create_webhook(name = member.name)
            await webhook.send(message, username=member.name, avatar_url=member.avatar_url)
            await webhook.delete()

            await response.edit(embed=create_embed({
                'title': f'Impersonated {member} in {channel}',
                'color': discord.Color.green()
            }, {
                'Message': message
            }))
        except Exception as error_message:
            await response.edit(embed=create_embed({
                'title': f'Could not impersonate {member.name}',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))

            print(f'ERROR: Could not impersonate {member.name}')
            print(error_message)

    @commands.command()
    @commands.guild_only()
    async def randomperson(self, context):
        response = await context.send(embed=create_embed({
            'title': f'Choosing random person...',
            'color': discord.Color.gold()
        }))

        try:
            random_member = random.choice(context.guild.members)
            await response.edit(embed=create_embed({
                'title': random_member
            }))
        except Exception as error_message:
            await response.edit(embed=create_embed({
                'title': f'Could not choose a random person',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))

            print('ERROR: Could not choose random person')
            print(error_message)

    @commands.command(aliases = ['m', 'meme'])
    async def getmeme(self, context, amount: int = 1):
        try:
            if amount > MAX_MEMES:
                amount = MAX_MEMES

            for _ in range(amount):
                while True:
                    meme = await get_meme()
                    if meme in self.recent_memes:
                        continue

                    self.recent_memes.append(meme)
                    if len(self.recent_memes) > 10:
                        self.recent_memes.pop(0)

                    await context.send(meme)
                    break
        except Exception as error_message:
            await context.send(embed=create_embed({
                'title': f'Could not retrieve meme',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))

            print('Could not retrieve meme')
            print(error_message)

def setup(client):
    client.add_cog(fun(client))
