import discord
from discord.ext import commands
from helper import create_embed, list_to_string, sort_dictionary
import os

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
                "title": "Could not get ping",
            }, {
                "Error Message": error_message
            }))

    @commands.command(description = "Retrieves an invite link for the bot.")
    async def invitebot(self, context):
        response = await context.send(embed = create_embed({
            "title": "Loading invite link for bot",
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
                "title": "Could not get ping",
            }, {
                "Error Message": error_message
            }))

    @commands.command(description = "Retrieves an invite link for the server (first channel).", brief = "create instant invite")
    @commands.check_any(commands.is_owner(), commands.has_permissions(create_instant_invite = True))
    async def invitetoserver(self, context):
        response = await context.send(embed = create_embed({
            "title": "Loading invite link for server",
            "color": discord.Color.gold()
        }))

        try:
            invite_url = await context.guild.text_channels[0].create_invite(max_age = 3600, reason = "Created through bot")
            invite_url = invite_url.url
            await response.edit(embed = create_embed({
                "title": f"Server Invite",
                "url": invite_url
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not get ping",
            }, {
                "Error Message": error_message
            }))

    @commands.command(description = "Retrieves an invite link for the channel.", brief = "create instant invite.")
    @commands.check_any(commands.is_owner(), commands.has_permissions(create_instant_invite = True))
    async def invitetochannel(self, context):
        response = await context.send(embed = create_embed({
            "title": "Loading invite link for channel",
            "color": discord.Color.gold()
        }))

        try:
            invite_url = await context.channel.create_invite(max_age = 3600, reason = "Created through bot")
            invite_url = invite_url.url
            await response.edit(embed = create_embed({
                "title": f"Channel Invite",
                "url": invite_url
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not get ping",
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
                    "Subscriptions": "help subscriptions"
                }))
            elif flag == "command":
                for command in self.client.commands:
                    command_name = command.name
                    if command_name == value:
                        cog_name = command.cog_name
                        if not cog_name:
                            cog_name = "cog"

                        aliases = list_to_string(command.aliases)
                        if len(aliases) > 0:
                            aliases = " (" + aliases + ")"

                        description = command.description
                        if description:
                            description = description
                        else:
                            description = ""

                        parameters = list_to_string(command.clean_params)
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

                    aliases = list_to_string(command.aliases)
                    if len(aliases) > 0:
                        aliases = " (" + aliases + ")"

                    description = command.description
                    if description:
                        description = description
                    else:
                        description = ""

                    parameters = list_to_string(command.clean_params)
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
                }, {
                    "join_channel (channel)": "When a member joins or leaves the server, it will be announced in this channel.",
                    "default_role (role)": "When a member joins the server, they will be given this role.",
                    "acas_channel (channel)": "If ACAS is enabled, then class alerts will be announced in this channel.",
                    "acas_role (role)": "If ACAS is enabled, then members with this role will be alerted.",
                    "acas_enabled (true/false)": "Determines if ACAS will be enabled or disabled.",
                    "prefix (string)": "The prefix used to active commands.",
                    "vc_accent (string)": "The bot's accent in the voice channel. View accents here. https://gist.github.com/Vex87/3bb2204609924fa2144f53e90d12a8d4",
                    "vc_languages (string)": "The bot's language in the voice channel. View languages here. https://gist.github.com/Vex87/3bb2204609924fa2144f53e90d12a8d4",
                    "vc_slow_mode (true/false)": "If the bot will talk at a normal or slow pace.",
                    "voice_exp (int)": "The amount of EXP given to a member for staying in a voice channel for a minute.",
                    "message_exp (int)": "The amount of EXP given to a member for sending a message.",
                    "message_cooldown (int)": "The cooldown for receiving EXP for sending messages in seconds.",
                    "level_dificulty (int)": "The dificulty to level up by experience (`experience = level * level_dificulty`).",
                }))
            elif flag == "subscriptions":
                await response.edit(embed = create_embed({
                    "title": "Subscription Events"
                }, {
                    "roblox (user_id)": "Triggered when a user is online or offline.",
                }))
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

def setup(client):
    client.add_cog(default(client))