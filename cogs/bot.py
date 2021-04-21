import discord
from discord.ext import commands
import os
import sys
import time
import math

from helper import create_embed, get_settings, save_settings, get_channel, get_role, is_guild_owner, format_time
from constants import VERSION_LOGS, VC_LANGUAGES, VC_ACCENTS

def get_first_n_items(dictionary, number):
    new_dictionary = {}
    for index in list(dictionary)[:number]:
        new_dictionary[index] = dictionary.get(index)
    return new_dictionary

class bot(commands.Cog, description = "Bot management and settings."):
    def __init__(self, client):
        self.client = client
        self.uptime = time.time()

    @commands.command(aliases = ["run"], description = "Runs code through the bot.", brief = "bot creator or server owner")
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

    @commands.command(description = "Clears the terminal's logs.", brief = "bot creator")
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

    @commands.command(description = "Changes the bot's activity in its profile.", brief = "bot creator or server owner")
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

    @commands.command(description = "Changes the bot's status in its profile. Possible statuses are online, offline, dnd, and idle.", brief = "bot creator or server owner")
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

    @commands.command(description = "Stops and starts the bot if it is being hosted on a server. Stops the bot if it is being hosted locally.", brief = "bot creator or server owner")
    @commands.check_any(commands.is_owner(), is_guild_owner())
    async def restart(self, context):
        await context.send(embed = create_embed({
            "title": "Restarting bot, no confirmation message after completion...",
            "color": discord.Color.gold(),
        }))
        sys.exit()

    @commands.command(aliases = ["set"], description = "Changes a server specific setting in the data stores.", brief = "specific")
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
                if not context.author.guild_permissions.administrator and not await self.client.is_owner(context.author):
                    await response.edit(embed = create_embed({
                        "title": f"You don't have administrator or bot creator permissions",
                        "color": discord.Color.red(),
                    }))
                    return

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
                if not context.author.guild_permissions.administrator and not await self.client.is_owner(context.author):
                    await response.edit(embed = create_embed({
                        "title": f"You don't have administrator or bot creator permissions",
                        "color": discord.Color.red(),
                    }))
                    return

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
                if not context.author.guild_permissions.administrator and not await self.client.is_owner(context.author):
                    await response.edit(embed = create_embed({
                        "title": f"You don't have administrator or bot creator permissions",
                        "color": discord.Color.red(),
                    }))
                    return

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
                if not context.author.guild_permissions.administrator and not await self.client.is_owner(context.author):
                    await response.edit(embed = create_embed({
                        "title": f"You don't have administrator or bot creator permissions",
                        "color": discord.Color.red(),
                    }))
                    return

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
            
            elif name == "vc_accent":
                value = str(value)
                if value:
                    settings["vc_accent"] = value
                    save_settings(settings)

                    await response.edit(embed = create_embed({
                        "title": f"Changed the bot's accent to {value}",
                        "color": discord.Color.green(),
                    }))
                else:
                    await response.edit(embed = create_embed({
                        "title": f"{value} could not be converted to a string",
                        "color": discord.Color.red()
                    }))
                    return
            elif name == "vc_language":
                value = str(value)
                if value:
                    settings["vc_language"] = value
                    save_settings(settings)

                    await response.edit(embed = create_embed({
                        "title": f"Changed the bot's language to {value}",
                        "color": discord.Color.green(),
                    }))
                else:
                    await response.edit(embed = create_embed({
                        "title": f"{value} could not be converted to a string",
                        "color": discord.Color.red()
                    }))
                    return
            elif name == "vc_slow_mode":
                if not value or value.lower() == "false":
                    settings["vc_slow_mode"] = False
                    save_settings(settings)

                    await response.edit(embed = create_embed({
                        "title": "Disabled bot slow mode",
                        "color": discord.Color.green(),
                    }))
                elif value.lower() == "true":
                    settings["vc_slow_mode"] = True
                    save_settings(settings)

                    await response.edit(embed = create_embed({
                        "title": "Enabled bot slow mode",
                        "color": discord.Color.green(),
                    }))
                else:
                    await response.edit(embed = create_embed({
                        "title": f"{value} is not a valid boolean (true/false)",
                        "color": discord.Color.red()
                    }))
                    return
            
            elif name == "voice_exp":
                if not context.author.guild_permissions.administrator and not await self.client.is_owner(context.author):
                    await response.edit(embed = create_embed({
                        "title": f"You don't have administrator or bot creator permissions",
                        "color": discord.Color.red(),
                    }))
                    return

                value = int(value)
                if value:
                    settings["voice_exp"] = value
                    save_settings(settings)

                    await response.edit(embed = create_embed({
                        "title": f"Set voice EXP to {value}",
                        "color": discord.Color.green(),
                    }))
                else:
                    await response.edit(embed = create_embed({
                        "title": f"{value} is not a valid integer",
                        "color": discord.Color.red()
                    }))
                    return
            elif name == "message_exp":
                if not context.author.guild_permissions.administrator and not await self.client.is_owner(context.author):
                    await response.edit(embed = create_embed({
                        "title": f"You don't have administrator or bot creator permissions",
                        "color": discord.Color.red(),
                    }))
                    return

                value = int(value)
                if value:
                    settings["message_exp"] = value
                    save_settings(settings)

                    await response.edit(embed = create_embed({
                        "title": f"Set message EXP to {value}",
                        "color": discord.Color.green(),
                    }))
                else:
                    await response.edit(embed = create_embed({
                        "title": f"{value} is not a valid integer",
                        "color": discord.Color.red()
                    }))
                    return
            elif name == "level_dificulty":
                if not context.author.guild_permissions.administrator and not await self.client.is_owner(context.author):
                    await response.edit(embed = create_embed({
                        "title": f"You don't have administrator or bot creator permissions",
                        "color": discord.Color.red(),
                    }))
                    return
            
                value = int(value)
                if value:
                    settings["level_dificulty"] = value
                    save_settings(settings)

                    await response.edit(embed = create_embed({
                        "title": f"Set level dificulty to {value}",
                        "color": discord.Color.green(),
                    }))
                else:
                    await response.edit(embed = create_embed({
                        "title": f"{value} is not a valid integer",
                        "color": discord.Color.red()
                    }))
                    return
            elif name == "message_cooldown":
                if not context.author.guild_permissions.administrator and not await self.client.is_owner(context.author):
                    await response.edit(embed = create_embed({
                        "title": f"You don't have administrator or bot creator permissions",
                        "color": discord.Color.red(),
                    }))
                    return

                value = int(value)
                if value:
                    settings["message_cooldown"] = value
                    save_settings(settings)

                    await response.edit(embed = create_embed({
                        "title": f"Set message cooldown to {value}",
                        "color": discord.Color.green(),
                    }))
                else:
                    await response.edit(embed = create_embed({
                        "title": f"{value} is not a valid integer",
                        "color": discord.Color.red()
                    }))
                    return
            elif name == "money_per_level":
                if not context.author.guild_permissions.administrator and not await self.client.is_owner(context.author):
                    await response.edit(embed = create_embed({
                        "title": f"You don't have administrator or bot creator permissions",
                        "color": discord.Color.red(),
                    }))
                    return

                value = int(value)
                if value:
                    settings["money_per_level"] = value
                    save_settings(settings)

                    await response.edit(embed = create_embed({
                        "title": f"Set money per level reward to ${value}",
                        "color": discord.Color.green(),
                    }))
                else:
                    await response.edit(embed = create_embed({
                        "title": f"{value} is not a valid integer",
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

    @commands.command(aliases = ["settings"], description = "Retrieves a list of server specific settings in the data store.")
    async def getsettings(self, context):
        response = await context.send(embed = create_embed({
            "title": "Loading settings...",
            "color": discord.Color.gold(),
        }))

        try:
            settings = get_settings(context.guild.id)
            await response.edit(embed = create_embed({
                "title": "Settings",
                "inline": True,
            }, settings))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Unable to load settings",
                "color": discord.Color.red(),
            }, {
                "Error Message": error_message,
            }))

    @commands.command(description = "Gets specific data.")
    async def get(self, context, name: str, *, value = None):
        response = await context.send(embed = create_embed({
            "title": f"Loading {name}...",
            "color": discord.Color.gold()
        }))

        try:
            if name == "vc_language":
                if value:
                    value = int(value)
                else:
                    value = 1

                first_page = value * 25 - 25
                last_page = value * 25

                fields = {}
                for key, language_name in enumerate(list(VC_LANGUAGES.keys())):
                    if key >= first_page and key < last_page:
                        fields[language_name] = VC_LANGUAGES[language_name]

                await response.edit(embed = create_embed({
                    "title": f"VC Languages (Page {value})",
                    "inline": True,
                }, fields))
            elif name == "vc_accent":
                if value:
                    value = int(value)
                else:
                    value = 1

                first_page = value * 25 - 25
                last_page = value * 25

                fields = {}
                for key, language_name in enumerate(list(VC_ACCENTS.keys())):
                    if key >= first_page and key < last_page:
                        fields[language_name] = VC_ACCENTS[language_name]

                await response.edit(embed = create_embed({
                    "title": f"VC Accents (Page {value})",
                    "inline": True,
                }, fields))
            else:
                await response.edit(embed = create_embed({
                    "title": f"{name} does not have any data",
                    "color": discord.Color.red()
                }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not get {name}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command(description = "Retrieves the Python and discord.py version the bot is running on.")
    async def version(self, context):
        response = await context.send(embed = create_embed({
            "title": "Loading version...",
            "color": discord.Color.gold()
        }))

        try:
            python_version = sys.version_info
            python_version_text = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
            discordpy_version_text = discord.__version__

            await response.edit(embed = create_embed({
                "title": "Bot Version",
            }, {
                "Python": python_version_text,
                "discord.py": discordpy_version_text
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not get version",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command(description = "Retrieves the bot's uptime, connected servers, members watching and users watching.")
    async def info(self, context):
        response = await context.send(embed = create_embed({
            "title": "Loading bot info...",
            "color": discord.Color.gold()
        }))

        try:
            uptime = round(time.time() - self.uptime)
            uptime_text = format_time(uptime)

            connected_servers = 0
            members_watching = 0
            user_ids = []

            for guild in self.client.guilds:
                connected_servers += 1
                for member in guild.members:
                    members_watching += 1
                    if not member.id in user_ids:
                        user_ids.append(member.id)

            users_watching = len(user_ids)

            await response.edit(embed = create_embed({
                "title": "Bot Info",
            }, {
                "Uptime": uptime_text,
                "Connected Servers": connected_servers,
                "Members Watching": members_watching,
                "Users Watching": users_watching
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not load bot info",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command()
    async def updatelog(self, context):
        logs = get_first_n_items(VERSION_LOGS, 10)
        await context.send(embed = create_embed({
            "title": "Update Log",
        }, logs))

def setup(client):
    client.add_cog(bot(client))