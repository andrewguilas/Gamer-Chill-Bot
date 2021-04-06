TOKEN = "ODEzMjU4Njg3MjI5NDYwNDkw.YDMsLA.Tc2QvlTr_-SBZnoJ88W8SLSZUUE"
TEST_TOKEN = "ODI3MjIzMDExNzM5ODI4MjM0.YGX5dw.x0ZjP8RgiV1JujgmAdlIkimsGKQ"
PREFIX = "?"
EXTENSIONS = [
    "events",
    "bot",
    "acas",
    "default_commands",
    # "economy_system",
    "fun",
    # "leveling_system",
    # "lottery",
    # "meme",
    # "moderation",
    # "personal",
    # "server",
    # "stock_market",
    # "vc",
]

import discord
from discord.ext import commands
from datetime import datetime
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://admin:QZnOT86qe3TQ@cluster0.meksl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
settings_data_store = cluster.discord_2.settings

def get_settings(guild_id: int):
    data = settings_data_store.find_one({"guild_id": guild_id}) 
    if not data:
        data = {"guild_id": guild_id}
        settings_data_store.insert_one(data)
    return data

async def get_prefix(client, context):
    guild_data = get_settings(context.guild.id)
    return guild_data.get("prefix") or PREFIX

client = commands.Bot(command_prefix = get_prefix, intents = discord.Intents.all())

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

@client.command(aliases = ["loadextension", "loadcog", "loadfile"], description = "Enables a cog.", brief = "bot creator or administrator")
@commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
async def load(context, extension: str):
    response = await context.send(embed = create_embed({
        "title": f"Loading {extension}...",
        "color": discord.Color.gold(),
    }))

    try:
        client.load_extension(f"cogs.{extension}")
    except commands.ExtensionNotFound:
        await response.edit(embed = create_embed({
            "title": f"{extension} not found",
            "color": discord.Color.red(),
        }))
    except commands.ExtensionAlreadyLoaded:
        await response.edit(embed = create_embed({
            "title": f"{extension} already loaded",
            "color": discord.Color.red(),
        }))
    except Exception as error_message:
        await response.edit(embed = create_embed({
            "title": f"Unable to load {extension}",
            "color": discord.Color.red(),
        }, {
            "Error Message": error_message,
        }))
    else:
        await response.edit(embed = create_embed({
            "title": f"{extension} was loaded",
            "color": discord.Color.green(),
        }))

@client.command(aliases = ["unloadextension", "unloadcog", "unloadfile"], description = "Disables a cog.", brief = "bot creator or administrator")
@commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
async def unload(context, extension):
    response = await context.send(embed = create_embed({
        "title": f"Unloading {extension}...",
        "color": discord.Color.gold(),
    }))

    try:
        client.unload_extension(f"cogs.{extension}")
    except commands.ExtensionNotFound:
        await response.edit(embed = create_embed({
            "title": f"{extension} not found",
            "color": discord.Color.red(),
        }))
    except commands.ExtensionNotLoaded:
        await response.edit(embed = create_embed({
            "title": f"{extension} already unloaded",
            "color": discord.Color.red(),
        }))
    except Exception as error_message:
        await response.edit(embed = create_embed({
            "title": f"Unable to unload {extension}",
            "color": discord.Color.red(),
        }, {
            "Error Message": error_message,
        }))
    else:
        await response.edit(embed = create_embed({
            "title": f"{extension} was unloaded",
            "color": discord.Color.green(),
        }))

@client.command(aliases = ["reloadextension", "reloadcog", "reloadfile"], description = "Reloads a cog.")
async def reload(context, extension):
    response = await context.send(embed = create_embed({
        "title": f"Reloading {extension}...",
        "color": discord.Color.gold(),
    }))

    try:
        client.reload_extension(f"cogs.{extension}")
    except commands.ExtensionNotLoaded:
        await response.edit(embed = create_embed({
            "title": f"{extension} not loaded",
            "color": discord.Color.red(),
        }))
    except commands.ExtensionNotFound:
        await response.edit(embed = create_embed({
            "title": f"{extension} not found",
            "color": discord.Color.red(),
        }))
    except Exception as error_message:
        await response.edit(embed = create_embed({
            "title": f"Unable to reload {extension}",
            "color": discord.Color.red(),
        }, {
            "Error Message": error_message,
        }))
    else:
        await response.edit(embed = create_embed({
            "title": f"{extension} was reloaded",
            "color": discord.Color.green(),
        }))

@client.command(aliases = ["reloadallextensions", "reloadallcogs", "reloadallfiles"], description = "Reloads all cogs.")
async def update(context):
    response = await context.send(embed = create_embed({
        "title": "Updating bot...",
        "color": discord.Color.gold(),
    }))

    try:
        for extension in EXTENSIONS:
            try:
                client.reload_extension(f"cogs.{extension}")
            except commands.ExtensionNotLoaded:
                await response.edit(embed = create_embed({
                    "title": f"{extension} not loaded",
                    "color": discord.Color.red(),
                }))
                return
            except Exception as error_message:
                await response.edit(embed = create_embed({
                    "title": f"Unable to reload {extension}",
                    "color": discord.Color.red(),
                }, {
                    "Error Message": error_message,
                }))
                return
    except Exception as error_message:
        await response.edit(embed = create_embed({
            "title": "Unable to update bot",
            "color": discord.Color.red(),
        }, {
            "Error Message": error_message,
        }))
    else:
        await response.edit(embed = create_embed({
            "title": "Bot updated",
            "color": discord.Color.green(),
        }))

client.remove_command("help")

for extension in EXTENSIONS:
    client.load_extension(f"cogs.{extension}")

client.run(TEST_TOKEN)