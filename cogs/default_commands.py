CLIENT_ID = "813258687229460490"

import discord
from discord.ext import commands

import pytz
from datetime import datetime

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
        embed.set_thumbnail(url = info["thumbnail"])
    
    return embed

def list_to_string(list: []):
    string = ""
    for index, value in enumerate(list):
        if index > 0:
            string = string + ", "
        string = string + value
    return string

def sort_dictionary(dictionary):
    sorted_dictionary = {}
    sorted_list = sorted(dictionary.items(), key = lambda x: x[1])
    for value in sorted_list:
        sorted_dictionary[value[0]] = value[1]
    return sorted_dictionary

class default_commands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ["latency"], description = "Retrieves the client to bot latency.")
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

    @commands.command(aliases = ["cmds", "commands"], description = "Retrieves a list of all the bot commands.")
    async def help(self, context):
        response = await context.send(embed = create_embed({
            "title": "Loading commands...",
            "color": discord.Color.gold()
        }))

        commands = {}
        for command in self.client.commands:
            cog_name = command.cog_name
            if cog_name:
                cog_name = cog_name + "."
            else:
                cog_name = "_"

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

            commands[f"{cog_name}{command_name}{aliases}{parameters}"] = f"{description}{brief}" or "\u200b"

        commands = sort_dictionary(commands)

        await response.edit(embed = create_embed({
            "title": "Commands",
            "inline": False,
        }, commands))

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
    client.add_cog(default_commands(client))