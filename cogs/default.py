import discord
from discord.ext import commands
import os
import asyncio
import pdb

from helper import create_embed, get_guild_data, save_guild_data, get_object, sort_dictionary, get_first_n_items, is_number, get_object
from constants import SETTINGS, GET_FLAGS, VC_ACCENTS, VC_LANGUAGES, DELETE_RESPONSE_DELAY, MAX_LEADERBOARD_FIELDS, CHECK_EMOJI, NEXT_EMOJI, BACK_EMOJI, COMMANDS, CHANGE_EMOJI, DEFAULT_GUILD_DATA, WAIT_DELAY

class default(commands.Cog, description = "Default bot commands."):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.guild_only()
    async def help(self, context):
        response = await context.send(embed = create_embed({
            "title": f"Loading commands...",
            "color": discord.Color.gold()
        }))

        try:
            pages = []
            current_page = 0
            for category, commands in COMMANDS.items():
                pages.append(create_embed({
                    "title": category,
                    "inline": True,
                }, commands))

            await response.edit(embed = pages[current_page])

            while True:
                def check_response(reaction, user):
                    return user == context.author and reaction.message == response

                try:
                    await response.add_reaction(BACK_EMOJI)
                    await response.add_reaction(NEXT_EMOJI)

                    reaction, user = await self.client.wait_for("reaction_add", check = check_response, timeout = 60)

                    if str(reaction.emoji) == NEXT_EMOJI:
                        if current_page + 1 >= len(pages):
                            current_page = len(pages) - 1
                        else:
                            current_page += 1
                    elif str(reaction.emoji) == BACK_EMOJI:
                        if current_page == 0:
                            current_page = 0
                        else:
                            current_page -= 1

                    await response.edit(embed = pages[current_page])
                    await response.remove_reaction(reaction.emoji, user)
                except asyncio.TimeoutError:
                    await response.edit(embed = pages[current_page])
                    await response.clear_reactions()
                    return
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not load commands",
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
                "Created Account": user.created_at,
                "Joined Server": user.joined_at,
                "Subscribed to Nitro": user.premium_since,
                "Is Bot": user.bot,
                "Is Pending": user.pending,
                "Roles": roles,
                "Top Role": user.top_role,
                "Activity": user.activity and user.activity.name or "None",
                "Device": user.desktop_status and "Desktop" or user.mobile_status and "Mobile" or user.web_status and "Web" or "Unknown",
                "Status": user.status,
                "Is In VC": user.voice and user.voice.channel or "False",
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

        try:
            humans = len(list(filter(lambda u: not u.bot, guild.members)))
            bots = len(list(filter(lambda u: u.bot, guild.members)))
            online = len(list(filter(lambda u: str(u.status) == "online", guild.members)))
            idle = len(list(filter(lambda u: str(u.status) == "idle", guild.members)))
            dnd = len(list(filter(lambda u: str(u.status) == "dnd", guild.members)))
            offline = len(list(filter(lambda u: str(u.status) == "offline", guild.members)))

            await response.edit(embed = create_embed({
                "title": f"{guild.name} server info",
                "thumbnail": guild.icon_url,
                "inline": True,
            }, {
                "Name": guild.name,
                "ID": guild.id,
                "Server Created": guild.created_at,
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

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator=True))
    async def settings(self, context):
        response = await context.send(embed=create_embed({
            "title": "Loading settings...",
            "color": discord.Color.gold()
        }))        

        try:
            while True:
                guild_data = get_guild_data(context.guild.id)
                
                # format settings

                if guild_data.get("_id"):
                    guild_data.pop("_id")
                if guild_data.get("guild_id"):
                    guild_data.pop("guild_id")
                if guild_data.get("bank_balance"):
                    guild_data.pop("bank_balance")

                if guild_data.get("exp_channels") and len(guild_data["exp_channels"]) > 0:
                    channels = []
                    for channel_id in guild_data["exp_channels"]:
                        channel = context.guild.get_channel(channel_id)
                        if channel:
                            channels.append(channel.mention)
                    guild_data["exp_channels"] = ", ".join(channels)                    
                else:
                    guild_data["exp_channels"] = "None"

                if guild_data.get("join_channel"):
                    channel = context.guild.get_channel(guild_data["join_channel"])
                    guild_data["join_channel"] = channel.mention
                else:
                    guild_data["join_channel"] = "None"

                if guild_data.get("default_role"):
                    role = context.guild.get_role(guild_data["default_role"])
                    guild_data["default_role"] = role.mention
                else:
                    guild_data["default_role"] = "None"

                if guild_data.get("acas_channel"):
                    channel = context.guild.get_channel(guild_data["acas_channel"])
                    guild_data["acas_channel"] = channel.mention
                else:
                    guild_data["acas_channel"] = "None"

                if guild_data.get("acas_role"):
                    role = context.guild.get_role(guild_data["acas_role"])
                    guild_data["acas_role"] = role.mention
                else:
                    guild_data["acas_role"] = "None"

                if guild_data.get("bank_manager"):
                    member = await context.guild.fetch_member(guild_data["bank_manager"])
                    if member:
                        guild_data["bank_manager"] = member.mention
                    else:
                        guild_data["bank_manager"] = "None"

                await response.edit(embed=create_embed({
                    "title": "Settings",
                    "inline": True,
                    "description": f"Press {CHANGE_EMOJI} to change settings"
                }, guild_data))

                # change settings

                def check_reaction(reaction, user):
                    return user == context.author and reaction.message == response and str(reaction.emoji) == CHANGE_EMOJI

                try:
                    await response.add_reaction(CHANGE_EMOJI)
                    await self.client.wait_for("reaction_add", check=check_reaction, timeout=60)
                    await response.clear_reaction(CHANGE_EMOJI)
                except asyncio.TimeoutError:
                    await response.edit(embed=create_embed({
                        "title": "Settings",
                        "inline": True,
                    }, guild_data))
                    await response.clear_reaction(CHANGE_EMOJI)
                    return

                # get setting to change

                await response.edit(embed=create_embed({
                    "title": "Type the setting you would like to change",
                    "color": discord.Color.gold(),
                    "inline": True
                }, guild_data))

                def check_message(message):
                    return message.author == context.author and message.channel == context.channel

                setting_name = None

                try:
                    message = await self.client.wait_for("message", check=check_message, timeout=60)
                    await message.delete()
                    setting_name = message.content.lower()
                except asyncio.TimeoutError:
                    await response.edit(embed=create_embed({
                        "title": "You did not respond in time",
                        "inline": True,
                        "color": discord.Color.red(),
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                    continue

                if not setting_name:
                    await response.edit(embed=create_embed({
                        "title": "You did not enter a setting to change",
                        "color": discord.Color.red(),
                        "inline": True
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                    continue

                settings_list = list(DEFAULT_GUILD_DATA.keys())
                settings_list.remove("guild_id")
                settings_list.remove("bank_balance")
                if not setting_name in settings_list:
                    await response.edit(embed=create_embed({
                        "title": f"{setting_name} is an invalid setting",
                        "color": discord.Color.red(),
                        "inline": True,
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                    continue

                # get value to change the setting to

                await response.edit(embed=create_embed({
                    "title": f"Type the value you would like to set {setting_name} to",
                    "color": discord.Color.gold(),
                    "inline": True
                }, guild_data))

                setting_value = None

                try:
                    message = await self.client.wait_for("message", check=check_message, timeout=60)
                    await message.delete()
                    setting_value = message.content
                except asyncio.TimeoutError:
                    await response.edit(embed=create_embed({
                        "title": "You did not respond in time",
                        "inline": True,
                        "color": discord.Color.red(),
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                    continue

                if not setting_value:
                    await response.edit(embed=create_embed({
                        "title": "You did not enter a value",
                        "color": discord.Color.red(),
                        "inline": True
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                    continue

                # change settings

                if setting_name == "prefix":
                    setting_value = setting_value.lower()

                    if len(setting_value) > 1:
                        await response.edit(embed=create_embed({
                            "title": "Prefix must be one letter",
                            "color": discord.Color.red(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue

                    if is_number(setting_value):
                        await response.edit(embed=create_embed({
                            "title": "Prefix must be a letter",
                            "color": discord.Color.red(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue

                    new_guild_data = get_guild_data(context.guild.id)
                    guild_data["prefix"] = setting_value
                    new_guild_data["prefix"] = setting_value
                    save_guild_data(new_guild_data)

                    await response.edit(embed=create_embed({
                        "title": f"Changed prefix to {setting_value}",
                        "color": discord.Color.green(),
                        "inline": True,
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                elif setting_name == "vc_language":
                    setting_value = setting_value.lower()
                    
                    if not VC_LANGUAGES.get(setting_value):
                        await response.edit(embed=create_embed({
                            "title": f"{setting_value} is an invalid language",
                            "color": discord.Color.red(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue

                    new_guild_data = get_guild_data(context.guild.id)
                    guild_data["vc_language"] = setting_value
                    new_guild_data["vc_language"] = setting_value
                    save_guild_data(new_guild_data)

                    await response.edit(embed=create_embed({
                        "title": f"Changed VC language to {setting_value}",
                        "color": discord.Color.green(),
                        "inline": True,
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                elif setting_name == "vc_accent":
                    setting_value = setting_value.lower()
                    
                    if not VC_ACCENTS.get(setting_value):
                        await response.edit(embed=create_embed({
                            "title": f"{setting_value} is an invalid accent",
                            "color": discord.Color.red(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue

                    new_guild_data = get_guild_data(context.guild.id)
                    guild_data["vc_accent"] = setting_value
                    new_guild_data["vc_accent"] = setting_value
                    save_guild_data(new_guild_data)

                    await response.edit(embed=create_embed({
                        "title": f"Changed VC accent to {setting_value}",
                        "color": discord.Color.green(),
                        "inline": True,
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                elif setting_name == "vc_slow_mode":
                    setting_value = setting_value.lower()
                    if setting_value == "true":
                        new_guild_data = get_guild_data(context.guild.id)
                        guild_data["vc_slow_mode"] = True
                        new_guild_data["vc_slow_mode"] = True
                        save_guild_data(new_guild_data)

                        await response.edit(embed=create_embed({
                            "title": "Turned on VC slow mode",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                    elif setting_value == "false":
                        new_guild_data = get_guild_data(context.guild.id)
                        guild_data["vc_slow_mode"] = False
                        new_guild_data["vc_slow_mode"] = False
                        save_guild_data(new_guild_data)

                        await response.edit(embed=create_embed({
                            "title": "Turned off VC slow mode",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                    else:
                        await response.edit(embed=create_embed({
                            "title": f"{setting_value} is an invalid value",
                            "color": discord.Color.red(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                elif setting_name == "message_cooldown":
                    setting_value = int(setting_value)
                    
                    new_guild_data = get_guild_data(context.guild.id)
                    guild_data["message_cooldown"] = setting_value
                    new_guild_data["message_cooldown"] = setting_value
                    save_guild_data(new_guild_data)

                    await response.edit(embed=create_embed({
                        "title": f"Set message cooldown to {setting_value}",
                        "color": discord.Color.green(),
                        "inline": True,
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                elif setting_name == "exp_per_message":
                    setting_value = int(setting_value)
                    
                    new_guild_data = get_guild_data(context.guild.id)
                    guild_data["exp_per_message"] = setting_value
                    new_guild_data["exp_per_message"] = setting_value
                    save_guild_data(new_guild_data)

                    await response.edit(embed=create_embed({
                        "title": f"Set EXP per message to {setting_value}",
                        "color": discord.Color.green(),
                        "inline": True,
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                elif setting_name == "exp_channels":
                    channel = get_object(context.guild.text_channels, setting_value)
                    if not channel:
                        await response.edit(embed=create_embed({
                            "title": f"Could not find text chanel {setting_value}",
                            "color": discord.Color.red(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue

                    new_guild_data = get_guild_data(context.guild.id)
                    if channel.id in new_guild_data["exp_channels"]:
                        new_guild_data["exp_channels"].remove(channel.id)
                        save_guild_data(new_guild_data)

                        if len(new_guild_data["exp_channels"]) > 0:
                            exp_channels = []
                            for point_channel_id in new_guild_data["exp_channels"]:
                                point_channel = context.guild.get_channel(point_channel_id)
                                if point_channel:
                                    exp_channels.append(point_channel.mention)
                            guild_data["exp_channels"] = ", ".join(exp_channels)
                        else:
                            guild_data["exp_channels"] = "None"
                        
                        await response.edit(embed=create_embed({
                            "title": f"Removed {channel} from EXP channels",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                    else:
                        new_guild_data["exp_channels"].append(channel.id)
                        save_guild_data(new_guild_data)

                        if len(new_guild_data["exp_channels"]) > 0:
                            exp_channels = []
                            for point_channel_id in new_guild_data["exp_channels"]:
                                point_channel = context.guild.get_channel(point_channel_id)
                                if point_channel:
                                    exp_channels.append(point_channel.mention)
                            guild_data["exp_channels"] = ", ".join(exp_channels)
                        else:
                            guild_data["exp_channels"] = "None"
                        
                        await response.edit(embed=create_embed({
                            "title": f"Added {channel} to EXP channels",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                elif setting_name == "join_channel":
                    if setting_value.lower() == "none":
                        new_guild_data = get_guild_data(context.guild.id)
                        new_guild_data["join_channel"] = None
                        guild_data["join_channel"] = "None"
                        save_guild_data(new_guild_data)

                        await response.edit(embed=create_embed({
                            "title": "Removed join channel",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue
                    else:
                        channel = get_object(context.guild.text_channels, setting_value)
                        if not channel:
                            await response.edit(embed=create_embed({
                                "title": f"Could not find channel {setting_value}",
                                "color": discord.Color.red(),
                                "inline": True,
                            }, guild_data))
                            await asyncio.sleep(WAIT_DELAY)
                            continue

                        new_guild_data = get_guild_data(context.guild.id)
                        new_guild_data["join_channel"] = channel.id
                        guild_data["join_channel"] = channel.mention
                        save_guild_data(new_guild_data)

                        await response.edit(embed=create_embed({
                            "title": f"Set join channel to {channel.name}",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                elif setting_name == "default_role":
                    if setting_value.lower() == "none":
                        new_guild_data = get_guild_data(context.guild.id)
                        new_guild_data["default_role"] = None
                        guild_data["default_role"] = "None"
                        save_guild_data(new_guild_data)

                        await response.edit(embed=create_embed({
                            "title": "Removed default role",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue
                    else:
                        role = get_object(context.guild.roles, setting_value)
                        if not channel:
                            await response.edit(embed=create_embed({
                                "title": f"Could not find role {setting_value}",
                                "color": discord.Color.red(),
                                "inline": True,
                            }, guild_data))
                            await asyncio.sleep(WAIT_DELAY)
                            continue

                        new_guild_data = get_guild_data(context.guild.id)
                        new_guild_data["default_role"] = role.id
                        guild_data["default_role"] = role.mention
                        save_guild_data(new_guild_data)

                        await response.edit(embed=create_embed({
                            "title": f"Set default role to {role.name}",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                elif setting_name == "acas_channel":
                    if setting_value.lower() == "none":
                        new_guild_data = get_guild_data(context.guild.id)
                        new_guild_data["acas_channel"] = None
                        guild_data["acas_channel"] = "None"
                        save_guild_data(new_guild_data)

                        await response.edit(embed=create_embed({
                            "title": "Removed ACAS channel",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue
                    else:
                        channel = get_object(context.guild.text_channels, setting_value)
                        if not channel:
                            await response.edit(embed=create_embed({
                                "title": f"Could not find channel {setting_value}",
                                "color": discord.Color.red(),
                                "inline": True,
                            }, guild_data))
                            await asyncio.sleep(WAIT_DELAY)
                            continue

                        new_guild_data = get_guild_data(context.guild.id)
                        new_guild_data["acas_channel"] = channel.id
                        guild_data["acas_channel"] = channel.mention
                        save_guild_data(new_guild_data)

                        await response.edit(embed=create_embed({
                            "title": f"Set acas channel to {channel.name}",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                elif setting_name == "acas_role":
                    if setting_value.lower() == "none":
                        new_guild_data = get_guild_data(context.guild.id)
                        new_guild_data["acas_role"] = None
                        guild_data["acas_role"] = "None"
                        save_guild_data(new_guild_data)

                        await response.edit(embed=create_embed({
                            "title": "Removed ACAS role",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                        continue
                    else:
                        role = get_object(context.guild.roles, setting_value)
                        if not channel:
                            await response.edit(embed=create_embed({
                                "title": f"Could not find role {setting_value}",
                                "color": discord.Color.red(),
                                "inline": True,
                            }, guild_data))
                            await asyncio.sleep(WAIT_DELAY)
                            continue

                        new_guild_data = get_guild_data(context.guild.id)
                        new_guild_data["acas_role"] = role.id
                        guild_data["acas_role"] = role.mention
                        save_guild_data(new_guild_data)

                        await response.edit(embed=create_embed({
                            "title": f"Set ACAS role to {role.name}",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                elif setting_name == "acas_enabled":
                    setting_value = setting_value.lower()
                    if setting_value == "true":
                        new_guild_data = get_guild_data(context.guild.id)
                        guild_data["acas_enabled"] = True
                        new_guild_data["acas_enabled"] = True
                        save_guild_data(new_guild_data)

                        await response.edit(embed=create_embed({
                            "title": "Enabled ACAS",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                    elif setting_value == "false":
                        new_guild_data = get_guild_data(context.guild.id)
                        guild_data["acas_enabled"] = False
                        new_guild_data["acas_enabled"] = False
                        save_guild_data(new_guild_data)

                        await response.edit(embed=create_embed({
                            "title": "Disabled ACAS",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                    else:
                        await response.edit(embed=create_embed({
                            "title": f"{setting_value} is an invalid value",
                            "color": discord.Color.red(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                elif setting_name == "voice_exp":
                    setting_value = int(setting_value)
                    
                    new_guild_data = get_guild_data(context.guild.id)
                    guild_data["voice_exp"] = setting_value
                    new_guild_data["voice_exp"] = setting_value
                    save_guild_data(new_guild_data)

                    await response.edit(embed=create_embed({
                        "title": f"Set voice EXP to {setting_value}",
                        "color": discord.Color.green(),
                        "inline": True,
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                elif setting_name == "money_per_level":
                    setting_value = int(setting_value)
                    
                    new_guild_data = get_guild_data(context.guild.id)
                    guild_data["money_per_level"] = setting_value
                    new_guild_data["money_per_level"] = setting_value
                    save_guild_data(new_guild_data)

                    await response.edit(embed=create_embed({
                        "title": f"Set money per level to {setting_value}",
                        "color": discord.Color.green(),
                        "inline": True,
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
                elif setting_name == "bank_manager":
                    if setting_value.lower() == "none":
                        new_guild_data = get_guild_data(context.guild.id)
                        new_guild_data["bank_manager"] = None
                        save_guild_data(new_guild_data)

                        if not guild_data["bank_manager"] or guild_data["bank_manager"] == "None":
                            await response.edit(embed=create_embed({
                                "title": f"Bank has no bank manager",
                                "color": discord.Color.red(),
                                "inline": True,
                            }, guild_data))
                        else:
                            guild_data["bank_manager"] = "None"
                            await response.edit(embed=create_embed({
                                "title": "Fired current bank manager",
                                "color": discord.Color.green(),
                                "inline": True,
                            }, guild_data))

                        await asyncio.sleep(WAIT_DELAY)
                    else:
                        member = get_object(context.guild.members, setting_value)
                        if not member:
                            await response.edit(embed=create_embed({
                                "title": f"Could not find member {setting_value}",
                                "color": discord.Color.red(),
                                "inline": True,
                            }, guild_data))
                            await asyncio.sleep(WAIT_DELAY)
                            continue
                        
                        new_guild_data = get_guild_data(context.guild.id)
                        guild_data["bank_manager"] = member.mention
                        new_guild_data["bank_manager"] = member.id
                        save_guild_data(new_guild_data)

                        await response.edit(embed=create_embed({
                            "title": f"Hired {member.name} as a bank manager",
                            "color": discord.Color.green(),
                            "inline": True,
                        }, guild_data))
                        await asyncio.sleep(WAIT_DELAY)
                else:
                    await response.edit(embed=create_embed({
                        "title": f"{setting_name} is an invalid setting",
                        "color": discord.Color.red(),
                        "inline": True,
                    }, guild_data))
                    await asyncio.sleep(WAIT_DELAY)
        except Exception as error_message:
            await response.edit(embed=create_embed({
                "title": "Could not load settings",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command(enabled=False, aliases = ["delete"], description = "Clears a set amount of text messages.", brief = "manage messages")
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
            "description": f"React with {CHECK_EMOJI} to be pinged when the message leaderboard is done",
            "color": discord.Color.gold()
        }))
        await response.add_reaction(CHECK_EMOJI)

        try:
            members = {}
            for channel in context.guild.text_channels:
                messages = await channel.history(limit = None).flatten()
                for message in messages:
                    author_name = message.author.name
                    if not context.guild.get_member(message.author.id):
                        continue

                    if not members.get(author_name):
                        members[author_name] = 1
                    else:
                        members[author_name] += 1

            members = sort_dictionary(members, True)
            members = get_first_n_items(members, MAX_LEADERBOARD_FIELDS)
            await response.edit(embed = create_embed({
                "title": "Message Leaderboard"
            }, members))

            response2 = await response.channel.fetch_message(response.id)
            for reaction in response2.reactions:
                if str(reaction.emoji) == CHECK_EMOJI:
                    users = [] 
                    async for user in reaction.users():
                        if not user.bot:
                            users.append(user.mention)

                    if len(users) > 0:
                        ping = " ".join(users)
                        await context.send(" ".join(users))
                    break

        except Exception as error_message:
            # traceback.print_exc()
            await response.edit(embed = create_embed({
                "title": "Could not load message leaderboard",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

def setup(client):
    client.add_cog(default(client))
