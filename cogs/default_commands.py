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

class default_commands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
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

    @commands.command()
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

    @commands.command()
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

    @commands.command()
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

    """
    @commands.command()
    async def help(self, context):
        EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
        
        current_page = 0
        new_embed = self.ordered_help_embeds[current_page]
        new_embed.set_footer(text = f"Page {current_page + 1}/{len(self.ordered_help_embeds)}", icon_url = "")
        message = await context.send(embed = new_embed)

        for emoji in EMOJIS:
            await message.add_reaction(emoji)

        while True:
            def check_reaction(reaction, user):
                if user == context.author and reaction.message.channel == context.channel and reaction.message.id == message.id:
                    if str(reaction.emoji) in EMOJIS:
                        return True

            chosen_reaction, user = await self.client.wait_for("reaction_add", check = check_reaction)

            for index, emoji in enumerate(EMOJIS):
                if emoji == chosen_reaction.emoji:
                    current_page = index
                    break

            new_embed = self.ordered_help_embeds[current_page]
            new_embed.set_footer(text = f"Page {current_page + 1}/{len(self.ordered_help_embeds)}", icon_url = "")
            await message.edit(embed = new_embed)
            await chosen_reaction.remove(user)
    """

    @commands.command()
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

    @commands.command()
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