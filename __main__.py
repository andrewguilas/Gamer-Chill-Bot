TOKEN = "ODEzMjU4Njg3MjI5NDYwNDkw.YDMsLA.Tc2QvlTr_-SBZnoJ88W8SLSZUUE"

import discord
from discord.ext import commands
from discord import Color as discord_color

import os
import pytz
from datetime import datetime

client = commands.Bot(command_prefix = "?", intents = discord.Intents.all())

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

@client.command()
@commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
async def load(context, extention):
    embed = await context.send(embed = create_embed(f"Loading {extention}...", {}, {
        "color": discord_color.gold(),
        "member": context.author,
    }))

    try:
        client.load_extension(f"cogs.{extention}")
    except Exception as error_message:
        await embed.edit(embed = create_embed(f"ERROR: {extention} was unable to load", {
            "Error Message": str(error_message)
        }, {
            "color": discord_color.red(),
            "member":  context.author,
        }))
    else:
        await embed.edit(embed = create_embed(f"SUCCESS: {extention} was loaded", {}, {
            "color": discord_color.green(),
            "member":  context.author,
        }))

@client.command()
@commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
async def unload(context, extention):
    embed = await context.send(embed = create_embed(f"Unloading {extention}...", {}, {
        "color": discord_color.gold(),
        "member": context.author,
    }))

    try:
        client.unload_extension(f"cogs.{extention}")
    except Exception as error_message:
        await embed.edit(embed = create_embed(f"ERROR: {extention} was unable to be unloaded", {
            "Error Message": str(error_message)
        }, {
            "color": discord_color.red(),
            "member":  context.author,
        }))
    else:
        await embed.edit(embed = create_embed(f"SUCCESS: {extention} was unloaded", {}, {
            "color": discord_color.green(),
            "member":  context.author,
        }))

@client.command()
async def reload(context, extention):
    embed = await context.send(embed = create_embed(f"Reloading {extention}...", {}, {
        "color": discord_color.gold(),
        "member": context.author,
    }))

    try:
        client.reload_extension(f"cogs.{extention}")
    except Exception as error_message:
        await embed.edit(embed = create_embed(f"ERROR: {extention} was unable to be reloaded", {
            "Error Message": str(error_message)
        }, {
            "color": discord_color.red(),
            "member":  context.author,
        }))
    else:
        await embed.edit(embed = create_embed(f"SUCCESS: {extention} was reloaded", {}, {
            "color": discord_color.green(),
            "member":  context.author,
        }))

@client.command()
async def update(context):
    embed = await context.send(embed = create_embed(f"Updating bot...", {}, {
        "color": discord_color.gold(),
        "member": context.author,
    }))

    try:
        for file_name in os.listdir("./cogs"):
            if file_name.endswith(".py"):
                client.reload_extension(f"cogs.{file_name[:-3]}")
    except Exception as error_message:
        await embed.edit(embed = create_embed(f"ERROR: Unable to update bot", {
            "Error Message": str(error_message)
        }, {
            "color": discord_color.red(),
            "member":  context.author,
        }))
    else:
        await embed.edit(embed = create_embed(f"Bot as updated", {}, {
            "color": discord_color.green(),
            "member":  context.author,
        }))

client.remove_command("help")

for file_name in os.listdir("./cogs"):
    if file_name.endswith(".py"):
        client.load_extension(f"cogs.{file_name[:-3]}")

client.run(TOKEN)