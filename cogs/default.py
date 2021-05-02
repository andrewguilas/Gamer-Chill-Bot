import discord
from discord.ext import commands
import os

from helper import create_embed, get_guild_data, save_guild_data, get_object, sort_dictionary
from constants import SETTINGS, GET_FLAGS, VC_ACCENTS, VC_LANGUAGES, DELETE_RESPONSE_DELAY

CLIENT_ID = os.getenv("GCB_CLIENT_ID")

class default(commands.Cog, description = "Default bot commands."):
    def __init__(self, client):
        self.client = client

    @commands.command(description = "Retrieves the client to bot latency.")
    async def ping(self, context):
        response = await context.send(embed = create_embed({
            "title": "Loading ping...",
            "color": discord.Color.gold()
        }))

        try:
            ping = round(self.client.latency * 1000)
            await response.edit(embed = create_embed({
                "title": f"{ping} ms",
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not load ping",
            }, {
                "Error Message": error_message
            }))

    @commands.command(description = "Retrieves an invite link for the bot.")
    async def invite(self, context):
        response = await context.send(embed = create_embed({
            "title": "Loading bot invite...",
            "color": discord.Color.gold()
        }))

        try:
            invite_url = discord.utils.oauth_url(client_id = CLIENT_ID, permissions = discord.Permissions(8))
            await response.edit(embed = create_embed({
                "title": f"Bot Invite",
                "url": invite_url
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not load bot invite",
            }, {
                "Error Message": error_message
            }))

    @commands.command(aliases = ["cmds"], description = "Retrieves a list of all the bot commands.")
    async def help(self, context, flag: str = None, value: str = None):
        response = await context.send(embed = create_embed({
            "title": "Loading commands...",
            "color": discord.Color.gold()
        }))

        try:
            if not flag:
                await response.edit(embed = create_embed({
                    "title": "Help Command Usage",
                }, {
                    "Commands": "help command <command_name>",
                    "Cogs": "help cog <cog_name>",
                    "Settings": "help settings",
                    "Get Flags": "help get_flag"
                }))
            elif flag == "command":
                for command in self.client.commands:
                    command_name = command.name
                    if command_name == value:
                        cog_name = command.cog_name
                        if not cog_name:
                            cog_name = "cog"

                        aliases = ", ".join(command.aliases)
                        if len(aliases) > 0:
                            aliases = " (" + aliases + ")"

                        description = command.description
                        if description:
                            description = description
                        else:
                            description = ""

                        parameters = ", ".join(command.clean_params)
                        if parameters:
                            parameters = " <" + parameters + ">"

                        brief = command.brief
                        if brief:
                            brief = " Requires " + brief + " permissions."
                        else:
                            brief = " Requires no permissions."

                        await response.edit(embed = create_embed({
                            "title": f"{command_name}{aliases}{parameters}",
                            "description": f"{description}{brief}" or "\u200b"
                        }))
                        return
                await response.edit(embed = create_embed({
                    "title": f"Could not find command {value}",
                    "color": discord.Color.red()
                }))       
            elif flag == "cog":
                command_info = {}
                for command in self.client.commands:
                    cog_name = command.cog_name
                    if not cog_name:
                        cog_name = "cog"

                    command_name = command.name

                    aliases = ", ".join(command.aliases)
                    if len(aliases) > 0:
                        aliases = " (" + aliases + ")"

                    description = command.description
                    if description:
                        description = description
                    else:
                        description = ""

                    parameters = ", ".join(command.clean_params)
                    if parameters:
                        parameters = " <" + parameters + ">"

                    brief = command.brief
                    if brief:
                        brief = " Requires " + brief + " permissions."
                    else:
                        brief = " Requires no permissions."

                    if not command_info.get(cog_name):
                        command_info[cog_name] = {}
                    command_info[cog_name][f"{command_name}{aliases}{parameters}"] = f"{description}{brief}" or "\u200b"

                if not value:
                    cogs = {"cog": "Cog management."}
                    for cog_name, cog_info in self.client.cogs.items():
                        cogs[cog_name] = cog_info.description or "\u200b"

                    await response.edit(embed = create_embed({
                        "title": f"Cogs",
                    }, cogs))
                else:
                    commands = command_info.get(value)
                    if not commands:
                        await response.edit(embed = create_embed({
                            "title": f"Could not find cog {value}",
                            "color": discord.Color.red()
                        }))
                    else: 
                        await response.edit(embed = create_embed({
                            "title": f"{value} Commands",
                        }, commands))
            elif flag == "settings":
                await response.edit(embed = create_embed({
                    "title": "Settings"
                }, SETTINGS))
            elif flag == "get_flag":
                await response.edit(embed = create_embed({
                    "title": "?get Flags"
                }, GET_FLAGS))
            else:
                await response.edit(embed = create_embed({
                    "title": f"Invalid flag {flag}",
                    "color": discord.Color.red()
                }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not load commands",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command(aliases = ["whois"], description = "Retrieves info of the user.")
    async def userinfo(self, context, user: discord.Member = None):
        if not user:
            user = context.author

        response = await context.send(embed = create_embed({
            "title": f"Loading user info for {user}...",
            "color": discord.Color.gold()
        }))

        try:
            roles = ""
            for index, role in enumerate(user.roles):
                if index > 0:
                    roles = roles + ", "
                roles = roles + role.name

            await response.edit(embed = create_embed({
                "title": f"{user}'s User Info",
                "thumbnail": user.avatar_url,
                "inline": True,
            }, {
                "Name": user,
                "User ID": user.id,
                "Nickname": user.nick,
                "Account Creation Date": user.created_at,
                "Server Join Date": user.joined_at,
                "Premium Join Date": user.premium_since,
                "Is Bot": user.bot,
                "Is Pending": user.pending,
                "Roles": roles,
                "Top Role": user.top_role,
                "Activity": user.activity and user.activity.name or "None",
                "Device": user.desktop_status and "Desktop" or user.mobile_status and "Mobile" or user.web_status and "Web" or "Unknown",
                "Status": user.status,
                "Is In Voice Channel": user.voice and user.voice.channel or "False",
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Something went wrong when retrieving user info for {user}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message,
            }))

    @commands.command(aliases = ["whereami"], description = "Retrieves info of the server.")
    async def serverinfo(self, context):
        guild = context.guild

        response = await context.send(embed = create_embed({
            "title": f"Loading server info for {guild.name}",
            "color": discord.Color.gold()
        }))

        humans = 0
        bots = 0

        online = 0
        idle = 0
        dnd = 0
        offline = 0

        try:
            for member in guild.members:
                if member.bot:
                    bots += 1
                else:
                    humans += 1

                if str(member.status) == "online":
                    online += 1
                elif str(member.status) == "idle":
                    idle += 1
                elif str(member.status) == "dnd":
                    dnd += 1
                elif str(member.status) == "offline":
                    offline += 1

            await response.edit(embed = create_embed({
                "title": f"{guild.name} server info",
                "thumbnail": guild.icon_url,
                "inline": True,
            }, {
                "Name": guild.name,
                "ID": guild.id,
                "Creation Date": guild.created_at,
                "Owner": guild.owner.mention,
                "Region": guild.region,
                "Invites": len(await guild.invites()),
                "Member Count": guild.member_count,
                "Members": f"😀 {humans} 🤖 {bots}",
                "Ban Count": len(await guild.bans()),
                "Member Statuses": f"🟩 {online} 🟨 {idle} 🟥 {dnd} ⬜ {offline}",
                "Category Count": len(guild.categories),
                "Channel Count": len(guild.channels),
                "Text Channel Count": len(guild.text_channels),
                "Voice Channel Count": len(guild.voice_channels),
                "Emoji Count": len(guild.emojis),
                "Role Count": len(guild.roles)
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not load server info for {guild.name}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command(aliases = ["set"], description = "Changes a server specific setting in the data stores.", brief = "specific")
    async def setsettings(self, context, name: str, *, value = None):
        response = await context.send(embed = create_embed({
            "title": f"Changing {name} to {value}...",
            "color": discord.Color.gold(),
        }))

        try:
            settings = get_guild_data(context.guild.id)
            name = name.lower()
            if name == "prefix":
                if not value:
                    await response.edit(embed = create_embed({
                        "title": "No prefix entered",
                        "color": discord.Color.red()
                    }))
                    return

                value = str(value)
                settings["prefix"] = value
                save_guild_data(settings)

                await response.edit(embed = create_embed({
                    "title": f"Changed prefix to {value}",
                    "color": discord.Color.green(),
                }))
            elif name == "vc_language":
                if not value:
                    await response.edit(embed = create_embed({
                        "title": "No language entered",
                        "color": discord.Color.red()
                    }))
                    return

                value = str(value)
                if not VC_LANGUAGES.get(value):
                    await response.edit(embed = create_embed({
                        "title": f"{value} is not a valid language",
                        "color": discord.Color.red()
                    }))
                    return

                settings["vc_language"] = value
                save_guild_data(settings)

                await response.edit(embed = create_embed({
                    "title": f"Changed the bot's language to {value}",
                    "color": discord.Color.green(),
                }))
            elif name == "vc_accent":
                if not value:
                    await response.edit(embed = create_embed({
                        "title": "No accent entered",
                        "color": discord.Color.red()
                    }))
                    return

                value = str(value)
                if not VC_ACCENTS.get(value):
                    await response.edit(embed = create_embed({
                        "title": f"{value} is not a valid accent",
                        "color": discord.Color.red()
                    }))
                    return

                settings["vc_accent"] = value
                save_guild_data(settings)

                await response.edit(embed = create_embed({
                    "title": f"Changed the bot's accent to {value}",
                    "color": discord.Color.green(),
                }))
            elif name == "vc_slow_mode":
                if not value or value.lower() == "false":
                    settings["vc_slow_mode"] = False
                    save_guild_data(settings)

                    await response.edit(embed = create_embed({
                        "title": "Disabled bot slow mode",
                        "color": discord.Color.green(),
                    }))
                elif value.lower() == "true":
                    settings["vc_slow_mode"] = True
                    save_guild_data(settings)

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
            elif name == "message_cooldown":
                if not context.author.guild_permissions.administrator and not await self.client.is_owner(context.author):
                    await response.edit(embed = create_embed({
                        "title": f"You don't have administrator or bot creator permissions",
                        "color": discord.Color.red(),
                    }))
                    return

                if not value:
                    await response.edit(embed = create_embed({
                        "title": "No prefix entered",
                        "color": discord.Color.red()
                    }))
                    return

                value = int(value)
                settings["message_cooldown"] = value
                save_guild_data(settings)

                await response.edit(embed = create_embed({
                    "title": f"Set message cooldown to {value} seconds",
                    "color": discord.Color.green(),
                }))
            elif name == "exp_per_message":
                if not context.author.guild_permissions.administrator and not await self.client.is_owner(context.author):
                    await response.edit(embed = create_embed({
                        "title": f"You don't have administrator or bot creator permissions",
                        "color": discord.Color.red(),
                    }))
                    return

                if not value:
                    await response.edit(embed = create_embed({
                        "title": "No prefix entered",
                        "color": discord.Color.red()
                    }))
                    return

                value = int(value)
                settings["exp_per_message"] = value
                save_guild_data(settings)

                await response.edit(embed = create_embed({
                    "title": f"Set message EXP to {value}",
                    "color": discord.Color.green(),
                }))
            elif name == "exp_channels":
                channel = get_object(context.guild.text_channels, value)
                if not channel:
                    await response.edit(embed = create_embed({
                        "title": f"Could not get channel {value}",
                        "color": discord.Color.red()
                    }))
                    return

                if channel.id in settings["exp_channels"]:
                    settings["exp_channels"].pop(channel.id)
                    save_guild_data(settings)
                    await response.edit(embed = create_embed({
                        "title": f"Removed {channel} from EXP channels",
                        "color": discord.Color.green()
                    }))
                else:
                    settings["exp_channels"].append(channel.id)
                    save_guild_data(settings)
                    await response.edit(embed = create_embed({
                        "title": f"Added {channel} from EXP channels",
                        "color": discord.Color.green()
                    }))
            elif name == "join_channel":
                if not context.author.guild_permissions.administrator and not await self.client.is_owner(context.author):
                    await response.edit(embed = create_embed({
                        "title": f"You don't have administrator or bot creator permissions",
                        "color": discord.Color.red(),
                    }))
                    return

                if not value or value.lower() == "none":
                    settings["join_channel"] = None
                    save_guild_data(settings)

                    await response.edit(embed = create_embed({
                        "title": "Removed join channel",
                        "color": discord.Color.green(),
                    }))
                else:
                    channel = get_object(context.guild.text_channels, value)
                    if channel:
                        settings["join_channel"] = channel.id
                        save_guild_data(settings)

                        await response.edit(embed = create_embed({
                            "title": f"Set join channel to {channel}",
                            "color": discord.Color.green(),
                        }))
                    else:
                        await response.edit(embed = create_embed({
                            "title": f"Could not find channel {value}",
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
                    save_guild_data(settings)

                    await response.edit(embed = create_embed({
                        "title": "Removed default role",
                        "color": discord.Color.green(),
                    }))
                else:
                    role = get_object(context.guild.roles, value)
                    if role:
                        settings["default_role"] = role.id
                        save_guild_data(settings)

                        await response.edit(embed = create_embed({
                            "title": f"Set default role to {role}",
                            "color": discord.Color.green(),
                        }))
                    else:
                        await response.edit(embed = create_embed({
                            "title": f"Could not get role {value}",
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
                    save_guild_data(settings)

                    await response.edit(embed = create_embed({
                        "title": "Removed ACAS channel",
                        "color": discord.Color.green(),
                    }))
                else:
                    channel = get_object(context.guild.text_channels, value)
                    if channel:
                        settings["acas_channel"] = channel.id
                        save_guild_data(settings)

                        await response.edit(embed = create_embed({
                            "title": f"Set ACAS channel to {channel}",
                            "color": discord.Color.green(),
                        }))
                    else:
                        await response.edit(embed = create_embed({
                            "title": f"Could not get channel {value}",
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
                    save_guild_data(settings)

                    await response.edit(embed = create_embed({
                        "title": "Removed ACAS role",
                        "color": discord.Color.green(),
                    }))
                else:
                    role = get_object(context.guild.roles, value)
                    if role:
                        settings["acas_role"] = role.id
                        save_guild_data(settings)

                        await response.edit(embed = create_embed({
                            "title": f"Set ACAS role to {role}",
                            "color": discord.Color.green(),
                        }))
                    else:
                        await response.edit(embed = create_embed({
                            "title": f"Could not get role {value}",
                            "color": discord.Color.red(),
                        })) 
            elif name == "acas_enabled":
                if not value or value.lower() == "false":
                    settings["acas_enabled"] = False
                    save_guild_data(settings)

                    await response.edit(embed = create_embed({
                        "title": "Disabled ACAS",
                        "color": discord.Color.green(),
                    }))
                elif value.lower() == "true":
                    settings["acas_enabled"] = True
                    save_guild_data(settings)

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
            elif name == "voice_exp":
                if not context.author.guild_permissions.administrator and not await self.client.is_owner(context.author):
                    await response.edit(embed = create_embed({
                        "title": f"You don't have administrator or bot creator permissions",
                        "color": discord.Color.red(),
                    }))
                    return

                if not value:
                    await response.edit(embed = create_embed({
                        "title": "No amount entered",
                        "color": discord.Color.red()
                    }))
                    return

                value = int(value)
                settings["voice_exp"] = value
                save_guild_data(settings)

                await response.edit(embed = create_embed({
                    "title": f"Set voice EXP to {value}",
                    "color": discord.Color.green(),
                }))
            else:
                await response.edit(embed = create_embed({
                    "title": f"{name} is not a valid setting",
                    "color": discord.Color.red(),
                }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not change {name} to {value}",
                "color": discord.Color.red(),
            }, {
                "Error Message": error_message,
            }))            

    @commands.command(aliases = ["settings"], description = "Retrieves a list of server specific settings in the data store.")
    async def getsettings(self, context):
        response = await context.send(embed = create_embed({
            "title": "Loading settings...",
            "color": discord.Color.gold(),
        }))

        try:
            settings = get_guild_data(context.guild.id)

            if settings.get("_id"):
                settings.pop("_id")

            if settings.get("guild_id"):
                settings.pop("guild_id")

            if len(settings["exp_channels"]) > 0:
                channels = []
                for channel_id in settings["exp_channels"]:
                    channel = get_object(context.guild.text_channels, channel_id)
                    if channel:
                        channels.append(channel.mention)
                settings["exp_channels"] = ", ".join(channels)
            else:
                settings["exp_channels"] = "None"

            if settings.get("join_channel"):
                channel = get_object(context.guild.text_channels, settings["join_channel"])
                if channel:
                    settings["join_channel"] = channel.mention

            if settings.get("default_role"):
                role = context.guild.get_role(settings["default_role"])
                if role:
                    settings["default_role"] = role.mention

            if settings.get("acas_channel"):
                channel = get_object(context.guild.text_channels, settings["acas_channel"])
                if channel:
                    settings["acas_channel"] = channel.mention

            if settings.get("acas_role"):
                role = context.guild.get_role(settings["acas_role"])
                if role:
                    settings["acas_role"] = role.mention

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

    @commands.command(description = "Gets specific info.")
    async def get(self, context, name: str, *, page: int = 1):
        response = await context.send(embed = create_embed({
            "title": f"Loading {name}...",
            "color": discord.Color.gold()
        }))

        try:
            if name == "vc_language":
                first_page = page * 25 - 25
                last_page = page * 25

                fields = {}
                for key, language_name in enumerate(list(VC_LANGUAGES.keys())):
                    if key >= first_page and key < last_page:
                        fields[language_name] = VC_LANGUAGES[language_name]

                await response.edit(embed = create_embed({
                    "title": f"VC Languages (Page {page})",
                    "inline": True,
                    "footer": f"Page {page}"
                }, fields))
            elif name == "vc_accent":
                first_page = page * 25 - 25
                last_page = page * 25

                fields = {}
                for key, language_name in enumerate(list(VC_ACCENTS.keys())):
                    if key >= first_page and key < last_page:
                        fields[language_name] = VC_ACCENTS[language_name]

                await response.edit(embed = create_embed({
                    "title": f"VC Accents",
                    "inline": True,
                    "footer": f"Page {page}"
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

    @commands.command(aliases = ["delete"], description = "Clears a set amount of text messages.", brief = "manage messages")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_messages = True))
    async def clear(self, context, amount: int = 1):
        response = await context.send(embed = create_embed({
            "title": f"Clearing {amount} messages...",
            "color": discord.Color.gold()
        }))

        try:
            deleted_messages_count = 0

            def check(context2):
                return context2.id != response.id

            deleted_messages = await context.channel.purge(limit = amount + 2, check = check)
            deleted_messages_count = len(deleted_messages) - 1

            await response.edit(embed = create_embed({
                "title": f"Deleted {deleted_messages_count} messages",
                "color": discord.Color.green()
            }), delete_after = DELETE_RESPONSE_DELAY)
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not delete {amount} messages",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command(description = "Lists the top messagers in the server.")
    async def messageleaderboard(self, context):
        response = await context.send(embed = create_embed({
            "title": "Loading message leaderboard...",
            "color": discord.Color.gold()
        }))

        try:
            members = {}
            for channel in context.guild.text_channels:
                messages = await channel.history(limit = None).flatten()
                for message in messages:
                    author_name = message.author.name
                    if not members.get(author_name):
                        members[author_name] = 1
                    else:
                        members[author_name] += 1

            members = sort_dictionary(members, True)

            await response.edit(embed = create_embed({
                "title": "Message Leaderboard"
            }, members))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not load message leaderboard",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

def setup(client):
    client.add_cog(default(client))