TOKEN = "ODEzMjU4Njg3MjI5NDYwNDkw.YDMsLA.Tc2QvlTr_-SBZnoJ88W8SLSZUUE"

import discord
from discord.ext import commands
from discord import Color as discord_color

import os
import pytz
import threading
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

intents = discord.Intents.all()
client = commands.Bot(command_prefix = "?", intents = intents)

@client.command()
@commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
async def load(context, extention):
    try:
        client.load_extension(f"cogs.{extention}")
    except Exception as error_message:
        await context.send(embed = create_embed(f"Error: {extention} was unable to load", discord_color.red(), {
            "Error Message": str(error_message)
        }))
    else:
        await context.send(embed = create_embed(f"Success: {extention} was loaded", discord_color.green()))

@client.command()
@commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
async def unload(context, extention):
    try:
        client.unload_extension(f"cogs.{extention}")
    except Exception as error_message:
        await context.send(embed = create_embed(f"Error: {extention} was unable to unload", discord_color.red(), {
            "Error Message": str(error_message)
        }))
    else:
        await context.send(embed = create_embed(f"Success: {extention} was unloaded", discord_color.green()))

@client.command()
@commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
async def reload(context, extention):
    try:
        client.reload_extension(f"cogs.{extention}")
    except Exception as error_message:
        await context.send(embed = create_embed(f"Error: {extention} was unable to reload", discord_color.red(), {
            "Error Message": str(error_message)
        }))
    else:
        await context.send(embed = create_embed(f"Success: {extention} was reloaded", discord_color.green()))

@client.command()
@commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
async def update(context):
    try:
        for file_name in os.listdir("./cogs"):
            if file_name.endswith(".py"):
                client.reload_extension(f"cogs.{file_name[:-3]}")
    except Exception as error_message:
        await context.send(embed = create_embed(f"Error: Unable to update bot", discord_color.red(), {
            "Error Message": str(error_message)
        }))
    else:
        await context.send(embed = create_embed(f"Success: Bot was updated", discord_color.green()))

def main():
    client.remove_command("help")

    for file_name in os.listdir("./cogs"):
            if file_name.endswith(".py"):
                client.load_extension(f"cogs.{file_name[:-3]}")

    client.run(TOKEN)

if __name__ == "__main__":
    main()