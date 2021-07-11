import discord
from discord.ext import commands
import os
import dotenv
from helper import create_embed
from constants import EXTENSIONS, IS_TESTING, PREFIX

dotenv.load_dotenv('.env')
TEST_TOKEN = os.getenv('TEST_TOKEN')
PRODUCTION_TOKEN = os.getenv('PRODUCTION_TOKEN')

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=PREFIX, intents=intents)

@client.command()
@commands.check_any(commands.is_owner(), commands.has_permissions(administrator=True))
async def load(context, extension):
    response = await context.send(embed=create_embed({
        'title': f'Loading {extension}...',
        'color': discord.Color.gold(),
    }))

    try:
        client.load_extension(f'cogs.{extension}')
        await response.edit(embed=create_embed({
            'title': f'Loaded {extension}',
            'color': discord.Color.green(),
        }))
    except Exception as error_message:
        await response.edit(embed=create_embed({
            'title': f'Could not load {extension}',
            'color': discord.Color.red(),
        }, {
            'Error Message': error_message,
        }))

        print(f'ERROR: Could not load extension {extension}')
        print(error_message)

@client.command()
@commands.check_any(commands.is_owner(), commands.has_permissions(administrator=True))
async def unload(context, extension):
    response = await context.send(embed=create_embed({
        'title': f'Unloading {extension}...',
        'color': discord.Color.gold(),
    }))

    try:
        client.unload_extension(f'cogs.{extension}')
        await response.edit(embed=create_embed({
            'title': f'Unloaded {extension}',
            'color': discord.Color.green(),
        }))
    except Exception as error_message:
        await response.edit(embed=create_embed({
            'title': f'Could not unload {extension}',
            'color': discord.Color.red(),
        }, {
            'Error Message': error_message,
        }))

        print(f'ERROR: Could not unload extension {extension}')
        print(error_message)

@client.command()
async def reload(context, extension):
    response = await context.send(embed=create_embed({
        'title': f'Reloading {extension}...',
        'color': discord.Color.gold(),
    }))

    try:
        client.reload_extension(f'cogs.{extension}')
        await response.edit(embed=create_embed({
            'title': f'Reloaded {extension}',
            'color': discord.Color.green(),
        }))
    except Exception as error_message:
        await response.edit(embed=create_embed({
            'title': f'Could not reload {extension}',
            'color': discord.Color.red(),
        }, {
            'Error Message': error_message,
        }))

        print(f'ERROR: Could not reload extension {extension}')
        print(error_message)

@client.command()
async def update(context):
    response = await context.send(embed=create_embed({
        'title': 'Updating bot...',
        'color': discord.Color.gold(),
    }))

    try:
        for extension in EXTENSIONS:
            client.reload_extension(f'cogs.{extension}')
        await response.edit(embed=create_embed({
            'title': 'Updated bot',
            'color': discord.Color.green(),
        }))
    except Exception as error_message:
        await response.edit(embed=create_embed({
            'title': 'Could not update bot',
            'color': discord.Color.red(),
        }, {
            'Error Message': error_message,
        }))        

        print('ERROR: Could not update bot')
        print(error_message)

client.remove_command('help')
for extension in EXTENSIONS:
    client.load_extension(f'cogs.{extension}')

client.run(IS_TESTING and TEST_TOKEN or PRODUCTION_TOKEN)
