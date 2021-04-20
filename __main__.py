import discord
from discord.ext import commands
from pymongo import MongoClient
import logging

from secrets import TOKEN, TEST_TOKEN
from constants import PREFIX, EXTENSIONS, DEFAULT_GUILD_SETTINGS
from helper import create_embed, get_settings

async def get_prefix(client, context):
    guild_data = get_settings(context.guild.id)
    return guild_data.get("prefix") or PREFIX

client = commands.Bot(command_prefix = get_prefix, intents = discord.Intents.all())

@client.command(description = "Enables a cog.", brief = "bot creator or administrator")
@commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
async def load(context, extension: str):
    response = await context.send(embed = create_embed({
        "title": f"Loading {extension}...",
        "color": discord.Color.gold(),
    }))

    try:
        client.load_extension(f"cogs.{extension}")
    except Exception as error_message:
        await response.edit(embed = create_embed({
            "title": f"Could not load {extension}",
            "color": discord.Color.red(),
        }, {
            "Error Message": error_message,
        }))
    else:
        await response.edit(embed = create_embed({
            "title": f"{extension} was loaded",
            "color": discord.Color.green(),
        }))

@client.command(description = "Disables a cog.", brief = "bot creator or administrator")
@commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
async def unload(context , extension):
    response = await context.send(embed = create_embed({
        "title": f"Unloading {extension}...",
        "color": discord.Color.gold(),
    }))

    try:
        client.unload_extension(f"cogs.{extension}")
    except Exception as error_message:
        await response.edit(embed = create_embed({
            "title": f"Could not unload {extension}",
            "color": discord.Color.red(),
        }, {
            "Error Message": error_message,
        }))
    else:
        await response.edit(embed = create_embed({
            "title": f"{extension} was unloaded",
            "color": discord.Color.green(),
        }))

@client.command(description = "Reloads a cog.")
async def reload(context, extension):
    response = await context.send(embed = create_embed({
        "title": f"Reloading {extension}...",
        "color": discord.Color.gold(),
    }))

    try:
        client.reload_extension(f"cogs.{extension}")
    except Exception as error_message:
        await response.edit(embed = create_embed({
            "title": f"Could not reload {extension}",
            "color": discord.Color.red(),
        }, {
            "Error Message": error_message,
        }))
    else:
        await response.edit(embed = create_embed({
            "title": f"{extension} was reloaded",
            "color": discord.Color.green(),
        }))

@client.command(description = "Reloads all cogs.")
async def update(context):
    response = await context.send(embed = create_embed({
        "title": "Updating bot...",
        "color": discord.Color.gold(),
    }))

    try:
        for extension in EXTENSIONS:
            client.reload_extension(f"cogs.{extension}")
    except Exception as error_message:
        await response.edit(embed = create_embed({
            "title": "Could not update bot",
            "color": discord.Color.red(),
        }, {
            "Error Message": error_message,
        }))
    else:
        await response.edit(embed = create_embed({
            "title": "Updated bot",
            "color": discord.Color.green(),
        }))

client.remove_command("help")

for extension in EXTENSIONS:
    client.load_extension(f"cogs.{extension}")

client.run(TOKEN)
