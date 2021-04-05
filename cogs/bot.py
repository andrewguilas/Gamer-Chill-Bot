import discord
from discord.ext import commands

import os
import sys
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://admin:QZnOT86qe3TQ@cluster0.meksl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
settings_data_store = cluster.discord_2.settings

def save_settings(data):
    settings_data_store.update_one({"guild_id": data["guild_id"]}, {"$set": data})
    
def get_settings(guild_id: int):
    data = settings_data_store.find_one({"guild_id": guild_id}) 
    if not data:
        data = {"guild_id": guild_id}
        settings_data_store.insert_one(data)
    return data

def get_channel(text_channels: [], value):
    channel = None

    try:
        channel = discord.utils.find(lambda channel: channel.name == value, text_channels) or discord.utils.find(lambda channel: channel.mention == value, text_channels) or discord.utils.find(lambda channel: channel.id == int(value), text_channels)
    except Exception as error_message:
        pass

    return channel

def get_role(roles: [], value):
    role = None

    try:
        role = discord.utils.find(lambda role: role.name == value, roles) or discord.utils.find(lambda role: role.mention == value, roles) or discord.utils.find(lambda role: role.id == int(value), roles)
    except Exception as error_message:
        pass

    return role

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

def is_guild_owner():
    def predicate(context):
        return context.guild and context.guild.owner_id == context.author.id
    return commands.check(predicate)

class bot(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.check_any(commands.is_owner(), is_guild_owner())
    async def execute(self, context, *, code):
        response = await context.send(embed = create_embed({
            "title": "Executing code...",
            "color": discord.Color.gold(),
        }, {
            "Code": code,
        }))

        try:
            exec(code)
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not execute code",
                "color": discord.Color.red(),
            }, {
                "Error Message": error_message,
                "Code": code,
            }))
        else:
            await response.edit(embed = create_embed({
                "title": "Code executed",
                "color": discord.Color.green(),
            }, {
                "Code": code,
            }))

    @commands.command(aliases = ["clearterminal", "clearscreen"])
    @commands.check_any(commands.is_owner())
    async def cls(self, context):
        response = await context.send(embed = create_embed({
            "title": "Clearing terminal",
            "color": discord.Color.gold(),
        }))

        try:
            os.system("cls" if os.name == "nt" else "clear")
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not clear terminal",
                "color": discord.Color.red(),
            }, {
                "Error Message": error_message,
            }))
        else:
            await response.edit(embed = create_embed({
                "title": "Terminal cleared",
                "color": discord.Color.green(),
            }))

    @commands.command()
    @commands.check_any(commands.is_owner(), is_guild_owner())
    async def changeactivity(self, context, *, activity: str = ""):
        activity = activity.lower()

        response = await context.send(embed = create_embed({
            "title": "Changing the bot's activity",
            "color": discord.Color.gold(),
        }, {
            "Activity": activity or "None",
        }))

        try:
            await self.client.change_presence(activity = discord.Game(name = activity))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not change the bot's activity",
                "color": discord.Color.red(),
            }, {
                "Error Message": error_message,
                "Activity": activity or "None",
            }))
        else:
            await response.edit(embed = create_embed({
                "title": "Changed bot's activity",
                "color": discord.Color.green(),
            }, {
                "Activity": activity or "None",
            }))

    @commands.command()
    @commands.check_any(commands.is_owner(), is_guild_owner())
    async def changestatus(self, context, *, status: str = "online"):
        status = status.lower()

        response = await context.send(embed = create_embed({
            "title": f"Changing the bot's status to {status}",
            "color": discord.Color.gold(),
        }))

        try:
            await self.client.change_presence(status = discord.Status[status])
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not change the bot's status to {status}",
                "color": discord.Color.red(),
            }, {
                "Error Message": error_message,
            }))
        else:
            await response.edit(embed = create_embed({
                "title": f"Changed bot's status to {status}",
                "color": discord.Color.green(),
            }))

    @commands.command()
    @commands.check_any(commands.is_owner(), is_guild_owner())
    async def restart(self, context):
        await context.send(embed = create_embed({
            "title": "Restarting bot, no confirmation message after completion...",
            "color": discord.Color.gold(),
        }))
        sys.exit()

    @commands.command(aliases = ["set"])
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    async def setsettings(self, context, name: str, *, value = None):
        response = await context.send(embed = create_embed({
            "title": "Changing settings...",
            "color": discord.Color.gold(),
        }, {
            "Name": name,
            "Value": value,
        }))

        try:
            settings = get_settings(context.guild.id)
            name = name.lower()
            if name == "join_channel":
                if not value or value.lower() == "none":
                    settings["join_channel"] = None
                    save_settings(settings)

                    await response.edit(embed = create_embed({
                        "title": "Removed join channel",
                        "color": discord.Color.green(),
                    }))
                else:
                    channel = get_channel(context.guild.text_channels, value)
                    if channel:
                        settings["join_channel"] = channel.id
                        save_settings(settings)

                        await response.edit(embed = create_embed({
                            "title": f"Set join channel to {channel}",
                            "color": discord.Color.green(),
                        }))
                    else:
                        await response.edit(embed = create_embed({
                            "title": f"{value} is not a valid channel",
                            "color": discord.Color.red(),
                        }))
            elif name == "default_role":
                if not value or value.lower() == "none":
                    settings["default_role"] = None
                    save_settings(settings)

                    await response.edit(embed = create_embed({
                        "title": "Removed default role",
                        "color": discord.Color.green(),
                    }))
                else:
                    role = get_role(context.guild.roles, value)
                    if role:
                        settings["default_role"] = role.id
                        save_settings(settings)

                        await response.edit(embed = create_embed({
                            "title": f"Set default role to {role}",
                            "color": discord.Color.green(),
                        }))
                    else:
                        await response.edit(embed = create_embed({
                            "title": f"{value} is not a valid role",
                            "color": discord.Color.red(),
                        }))
            elif name == "acas_channel":
                if not value or value.lower() == "none":
                    settings["acas_channel"] = None
                    save_settings(settings)

                    await response.edit(embed = create_embed({
                        "title": "Removed ACAS channel",
                        "color": discord.Color.green(),
                    }))
                else:
                    channel = get_channel(context.guild.text_channels, value)
                    if channel:
                        settings["acas_channel"] = channel.id
                        save_settings(settings)

                        await response.edit(embed = create_embed({
                            "title": f"Set ACAS channel to {channel}",
                            "color": discord.Color.green(),
                        }))
                    else:
                        await response.edit(embed = create_embed({
                            "title": f"{value} is not a valid channel",
                            "color": discord.Color.red(),
                        }))
            elif name == "acas_role":
                if not value or value.lower() == "none":
                    settings["acas_role"] = None
                    save_settings(settings)

                    await response.edit(embed = create_embed({
                        "title": "Removed ACAS role",
                        "color": discord.Color.green(),
                    }))
                else:
                    role = get_role(context.guild.roles, value)
                    if role:
                        settings["acas_role"] = role.id
                        save_settings(settings)

                        await response.edit(embed = create_embed({
                            "title": f"Set ACAS role to {role}",
                            "color": discord.Color.green(),
                        }))
                    else:
                        await response.edit(embed = create_embed({
                            "title": f"{value} is not a valid role",
                            "color": discord.Color.red(),
                        })) 
            elif name == "acas_enabled":
                if not value or value.lower() == "false":
                    settings["acas_enabled"] = False
                    save_settings(settings)

                    await response.edit(embed = create_embed({
                        "title": "Disabled ACAS",
                        "color": discord.Color.green(),
                    }))
                elif value.lower() == "true":
                    settings["acas_enabled"] = True
                    save_settings(settings)

                    await response.edit(embed = create_embed({
                        "title": "Enabled ACAS",
                        "color": discord.Color.green(),
                    }))
                else:
                    await response.edit(embed = create_embed({
                        "title": f"{value} is not a valid boolean (true/false)",
                        "color": discord.Color.red()
                    }))
                    return
            elif name == "prefix":
                value = str(value)
                if value:
                    settings["prefix"] = value
                    save_settings(settings)

                    await response.edit(embed = create_embed({
                        "title": f"Changed prefix to {value}",
                        "color": discord.Color.green(),
                    }))
                else:
                    await response.edit(embed = create_embed({
                        "title": f"{value} could not be converted to a string",
                        "color": discord.Color.red()
                    }))
                    return
            else:
                await response.edit(embed = create_embed({
                    "title": f"{name} is not a valid setting",
                    "color": discord.Color.red(),
                }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Unable to change settings",
                "color": discord.Color.red(),
            }, {
                "Error Message": error_message,
                "Name": name,
                "Value": value,
            }))            

    @commands.command(aliases = ["settings"])
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    async def getsettings(self, context):
        response = await context.send(embed = create_embed({
            "title": "Loading settings...",
            "color": discord.Color.gold(),
        }))

        try:
            settings = get_settings(context.guild.id)
            await response.edit(embed = create_embed({
                "title": "Settings",
            }, settings))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Unable to load settings",
                "color": discord.Color.red(),
            }, {
                "Error Message": error_message,
            }))

def setup(client):
    client.add_cog(bot(client))