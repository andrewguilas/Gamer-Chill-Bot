CLIENT_ID = "813258687229460490"

import discord
from discord.ext import commands
from discord import Color as discord_color

import pytz
from datetime import datetime

def create_embed(title, color = discord_color.blue(), fields = {}, member: discord.Member = None):
    embed = discord.Embed(
        title = title,
        colour = color or discord_color.blue()
    )

    for name, value in fields.items():
        embed.add_field(
            name = name,
            value = value,
            inline = True
        )

    embed.timestamp = datetime.now(tz = pytz.timezone("US/Eastern"))
    if member:
        embed.set_author(name = member.name, icon_url = member.avatar_url)

    return embed

class default_commands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.help_embeds = {
            "table_of_contents_embed": create_embed("Table of Contents", None, {
                "1 - Table of Contents": "List of command categories",
                "2 - Default": "In general commands",
                "3 - Fun": "Commands for fun and games",
                "4 - Leveling System": "Commands for using and managing the leveling system",
                "5 - Economy System": "Commands for using and managing the economy system and lottery.",
                "6 - Stock Market": "Commands for trading on the simulated stock market.",
                "7 - Moderation": "Commands for moderation",
                "8 - Server": "Commands for server management",
                "9 - Bot": "Commands for bot management"
            }),

            "default_embed": create_embed("Default", None, {
                "help": "Returns a list of bot commands. No permissions required. Included in the `default_commands` set.",
                "helpold": "A legacy help command. No permissions required. Included in the `default_commands set`.",
                "ping": "Returns the user's ping. No permissions required. Included in the `default_commands` set.",
                "invitebot": "Returns an invite link for the bot. This bot was designed for this server specifically. No permissions required. Included in the `default_commands` set.",
                "invitetoserver": "Returns an invite link for the server (first text channel). Invite permissions required. Included in the `default_commands` set.",
                "invitetochannel": "Returns an invite link for the current channel. Invite permissions required. Included in the `default_commands` set.",
                "userinfo <USER>": "Returns info on the user. No permissions required. Included in the `default_commands set`.",
                "serverinfo": "Returns info on the server. No permissions required. Included in the `default_commands set`.",
                "acas": "Gives the member a role to be notified when class starts and 5 minutes before. No permissions required. Included in the `class_alert` set.",
                "pauseacas": "Stops the alarm system from running. No permissions required. Included in the `class_alert` set.",
                "resumecas": "Resumes the alarm system. No permissions required. Included in the `class_alert` set.",
            }),

            "fun_embed": create_embed("Fun", None, {
                "8ball <QUESTION>": "Returns a random response to a question. No permissions required. Included in the `fun_commands` set.",
                "roll <MAX_NUM = 6>": "Chooses a random number between 1 and MAX_NUM. No permissions required. Included in the `fun_commands` set.",
                "choose <CHOICES: List>": "Chooses a random item from the list. Items are seperated by spaces. No permissions required. Included in the `fun_commands` set.",
                "impersonate <MEMBER> <CHANNEL> <MESSAGE>": "Sends a MESSAGE disguised as the MEMBER in the CHANNEL. No permissions required. Included in the `fun_commands` set.",
                "tictactoe": "Creates a game of tic tac toe requiring two players. No permissions required. Included in the `tictactoe` set.",
                "sticks": "Creates a game of sticks requiring two players. No permissions required. Included in the `sticks` set.",
                "whohasbigpp": "Returns a random person in the server. No permissions required. Included in the `fun_commands` set.",
                "whohassmallpp": "Returns a random person in the server. No permissions required. Included in the `fun_commands` set.",
                "randomperson": "Returns a random person in the server. No permissions required. Included in the `fun_commands` set.",
                "meme/getmeme/m": "Returns a random meme from Reddit. No permissions required. Included in the `meme` set.",
                "getcachedmemes": "Returns a list of memes that were cached as there is a long delay when retreiving a meme from Reddit. No permissions required. Included in the `meme` set."
            }),

            "leveling_system_embed": create_embed("Leveling System", None, {
                "rank <MEMBER>": "Returns the rank of the member. No permissions required. Included in the `leveling_system set`.",
                "leaderboard": "Returns the leaderboard of the server. No permissions required. Included in the `leveling_system` set.",
                "addexperience <MEMBER> <AMOUNT>": "Gives a member a specified amount of experience. `Bot Owner` or `Administrator` permissions required. Included in the `leveling_system` set.",
            }),

            "economy_system_embed": create_embed("Economy System", None, {
                "wealth <MEMBER = SELF>": "Returns the net worth of the member. The net worth includes their pocket and bank account. No permissions required. Included in the `economy_system` set.",
                "forbes": "Returns a list of the richest people on the server and their net worth. No permissions required. Included in the `economy_system` set.",
                "withdraw <AMOUNT>": "Transfers money from the member's bank account to their pocket. No permissions required. Included in the `economy_system` set.",
                "deposit <AMOUNT>": "Transfers money from the member's pocket to their bank account. No permissions required. Included in the `economy_system` set.",
                "give <RECEIVER = SELF> <AMOUNT>": "Transfers money from the user's pocket to the receiver's pocket. No permissions required. the Included in the `economy_system` set.",
                "wire <RECEIVER = SELF> <AMOUNT>": "Transfers money from hte user's bank account to the receiver's bank account. No permissions required. Included in the `economy_system` set.",
                "addmoney <MEMBER> <AMOUNT>": "Prints and gives money to the specified member. `Bot Creator` or `Administrator` permissions required. Included in the `economy_system` set.",
                "lotteryinfo": "Displays the current lottery's info. No permissions required. Included in the `lottery` set.",
                "buytickets <COUNT>": "Purchases tickets to enter the lottery. No permissions required. Included in the `lottery` set.",
                "createlottery <TIMESTAMP ENDING> <TICKET PRICE> <INITIAL PRICE>": "Creates a lottery for others to join. The `TIMESTAMP ENDING` must be in the epoch format. No permissions required. Included in the `lottery` set.",
                "endlottery": "Ends the current lottery and rewards the winner with the grand prize. `Administrator` permissions required. Included in the `lottery` set.",
                "cancellottery": "Ends the current lottery and refunds all members that have purchased tickets. `Administrator` permissions required. Included in the `lottery` set.",
            }),

            "stock_market_embed": create_embed("Economy System", None, {
                "getprice <TICKER>": "Returns the most recent closed price of the stock. No permissions required. Included in the `stock_market` set.",
                "portfolio": "Returns the portfolio of the user. No permissions required. Included in the `stock_market` set.",
                "buyshares <TICKER> <SHARES>": "Buys the amount of shares of a stock using money from their bank account and sends the shares to their portfolio. No permissions required. Included in the `stock_market` set.",
                "sellshares <TICKER> <SHARES>": "Sells the amount of shares from a person's portfolio and sends the money to their bank account. No permissions required. Included in the `stock_market` set.",
            }),

            "moderation_embed": create_embed("Moderation", None, {
                "clear <AMOUNT = 1>": "Deletes AMOUNT of messages in the channel. `Manage Messages` permissions required. Included in the `moderation_commands` set.",
                "kick <MEMBER> <REASON = None>": "Kicks a MEMBER from the server with an optional reason. `Kick Members` permissions required. Included in the `moderation_commands` set.",
                "ban <MEMBER> <REASON>": "Bans a MEMBER from the server with an optional reason, preventing them from rejoining. `Ban Members` permissions required. Included in the `moderation_commands` set.",
                "unban <MEMBER>": "Unbans a MEMBER from the server allowing them to rejoin. `Ban Members` permissions required. Included in the `moderation_commands` set.",
                "nick <MEMBER = Self> <NICKNAME = None>": "Adds a nickname to the member if provided, else, it would remove its nickname. `Manage Messages` permissions required. Included in the `moderation_commands` set.",
                "mute <MEMBER = Self>": "Mutes or unmutes the member. `Mute Members` permissions required. Included in the `moderation_commands` set.",
                "deafen <MEMBER = Self>": "Deafens or undeafens the member. `Deafen Members` permissions required. Included in the `moderation_commands` set.",
                "move <MEMBER>": "Moves the member into the specified voice channel. `Move Member` permissions required. Included in the `moderation_commands` set.",
            }),

            "server_embed": create_embed("Server", None, {
                "listwebhooks <CHANNEL>": "Lists the webhooks for that CHANNEL. `Manage Webooks` permissions required. Included in the `server` set.",
                "clearwebhooks <CHANNEL>": "Deletes all the webhooks for that CHANNEL. `Manage Webooks` permissions required. Included in the `server` set.",
                "messageleaderboard": "Returns a sorted list of people and the amount of messages they've sent in the server. Unscanned channels are #logs and #army-command. Will take several minutes to finish running. No permissions required. Included in the `server` set.",
                "emojileaderboard": "Returns a sorted list of custom emojis and the amount of messages which included that emoji. Unscanned channels are #logs and #army-command. Will take several minutes to finish running. No permissions required. Included in the `server` set.",
            }),

            "bot_embed": create_embed("Bot", None, {
                "load <SET>": "Loads <SET> to update. `Administrator` permissions required. Not included in a set.",
                "unload <SET>": "Loads <SET> to update. `Administrator` permissions required. Not included in a set.",
                "reload <SET>": "Unloads and loads <SET> to update. `Administrator` permissions required. Not included in a set.",
                "update": "Unloads and loads all sets to update. `Administrator` permissions required. Not included in a set.",
                "listevents": "Lists events that can be triggered in the audit log. No permissions required. Included in the audit_log set.",
                "execute <CODE>": "Executes CODE. `Bot Creator` or `Server Owner` permissions required. Included in the `bot` set.",
                "cls": "Clears the terminal in the code editor. `Bot Creator` permissions required. Included in the `bot` set.",
                "changeactivity <STRING>": "Changes the bot's activity. `Bot Creator` or `Server Owner` permissions required. Included in the `bot` set.",
                "changestatus <online/idle/dnd/offline>": "Changes the bot's status. `Bot Creator` or `Server Owner` permissions required. Included in the `bot` set."
            }),
        }
        self.ordered_help_embeds = [
            self.help_embeds["table_of_contents_embed"],
            self.help_embeds["default_embed"],
            self.help_embeds["fun_embed"],
            self.help_embeds["leveling_system_embed"],
            self.help_embeds["economy_system_embed"],
            self.help_embeds["stock_market_embed"],
            self.help_embeds["moderation_embed"],
            self.help_embeds["server_embed"],
            self.help_embeds["bot_embed"],
        ]

    @commands.command()
    async def ping(self, context):
        ping = round(self.client.latency * 1000)
        await context.send(embed = create_embed(f"Your ping is {str(ping)} ms"))

    @commands.command()
    async def invitebot(self, context):
        embed = create_embed("Invite")
        embed.url = discord.utils.oauth_url(client_id = CLIENT_ID, permissions = discord.Permissions(8))
        await context.send(embed = embed)

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(create_instant_invite = True))
    async def invitetoserver(self, context):
        invite_link = await context.guild.text_channels[0].create_invite(max_age = 3600, reason = "Created through bot command.")
        embed = create_embed(f"Server Invite Code: {invite_link.code}", None, {
            "Channel": context.guild.text_channels[0].mention,
            "Max Age": "1 Hour"
        })
        embed.url = invite_link.url
        await context.send(embed = embed)

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(create_instant_invite = True))
    async def invitetochannel(self, context):
        invite_link = await context.channel.create_invite(max_age = 3600, reason = "Created through bot command.")
        embed = create_embed(f"#{context.channel} Invite Code: {invite_link.code}", None, {
            "Channel": context.channel.mention,
            "Max Age": "1 Hour"
        })
        embed.url = invite_link.url
        await context.send(embed = embed)

    @commands.command()
    async def helpold(self, context):
        await context.send(embed = create_embed("Default", None, {
            "help": "Returns a list of bot commands. No permissions required. Included in the `default_commands` set.",
            "ping": "Returns the user's ping. No permissions required. Included in the `default_commands` set.",
            "invitebot": "Returns an invite link for the bot. This bot was designed for this server specifically. No permissions required. Included in the `default_commands` set.",
            "invitetoserver": "Returns an invite link for the server (first text channel). Invite permissions required. Included in the `default_commands` set.",
            "invitetochannel": "Returns an invite link for the current channel. Invite permissions required. Included in the `default_commands` set.",
        }))

        await context.send(embed = create_embed("Bot Management", None, {
            "load <SET>": "Loads <SET> to update. `Administrator` permissions required. Not included in a set.",
            "unload <SET>": "Loads <SET> to update. `Administrator` permissions required. Not included in a set.",
            "reload <SET>": "Unloads and loads <SET> to update. `Administrator` permissions required. Not included in a set.",
            "update": "Unloads and loads all sets to update. `Administrator` permissions required. Not included in a set.",
            "listevents": "Lists events that can be triggered in the audit log. No permissions required. Included in the audit_log set.",
        }))

        await context.send(embed = create_embed("Server", None, {
            "listwebhooks <CHANNEL>": "Lists the webhooks for that CHANNEL. `Manage Webooks` permissions required. Included in the `server` set.",
            "clearwebhooks <CHANNEL>": "Deletes all the webhooks for that CHANNEL. `Manage Webooks` permissions required. Included in the `server` set.",
        }))

        await context.send(embed = create_embed("Moderation", None, {
            "clear <AMOUNT = 1>": "Deletes AMOUNT of messages in the channel. `Manage Messages` permissions required. Included in the `moderation_commands` set.",
            "kick <MEMBER> <REASON = None>": "Kicks a MEMBER from the server with an optional reason. `Kick Members` permissions required. Included in the `moderation_commands` set.",
            "ban <MEMBER> <REASON>": "Bans a MEMBER from the server with an optional reason, preventing them from rejoining. `Ban Members` permissions required. Included in the `moderation_commands` set.",
            "unban <MEMBER>": "Unbans a MEMBER from the server allowing them to rejoin. `Ban Members` permissions required. Included in the `moderation_commands` set.",
            "nick <MEMBER = Self> <NICKNAME = None>": "Adds a nickname to the member if provided, else, it would remove its nickname. `Manage Messages` permissions required. Included in the `moderation_commands` set.",
            "mute <MEMBER = Self>": "Mutes or unmutes the member. `Mute Members` permissions required. Included in the `moderation_commands` set.",
            "deafen <MEMBER = Self>": "Deafens or undeafens the member. `Deafen Members` permissions required.",
        }))

        await context.send(embed = create_embed("Bot", None, {
            "execute <CODE>": "Executes CODE. `Bot Creator` permissions required. Included in the `bot` set.",
            "cls": "Clears the terminal in the code editor. `Bot Creator` permissions required. Included in the `bot` set."
        }))

        await context.send(embed = create_embed("Fun", None, {
            "8ball <QUESTION>": "Returns a random response to a question. No permissions required. Included in the `fun_commands` set.",
            "roll <MAX_NUM = 6>": "Chooses a random number between 1 and MAX_NUM. No permissions required. Included in the `fun_commands` set.",
            "choose <CHOICES: List>": "Chooses a random item from the list. Items are seperated by spaces. No permissions required. Included in the `fun_commands` set.",
            "impersonate <MEMBER> <CHANNEL> <MESSAGE>": "Sends a MESSAGE disguised as the MEMBER in the CHANNEL. No permissions required. Included in the `fun_commands` set.",
            "tictactoe": "Create a game of tic tac toe. No permissions required. Included in the `tictactoe` set."
        }))

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

    @commands.command()
    async def userinfo(self, context, user: discord.Member = None):
        if not user:
            user = context.author

        roles = []
        for role in user.roles:
            roles.append(role.name)

        embed = create_embed(f"{user}'s User Info", None, {
            "Name": user,
            "User ID": user.id,
            "Nickname": user.nick,
            "Account Creation Date": user.created_at,
            "Join Date": user.joined_at,
            "Premium Join Date": user.premium_since,
            "Is a Bot": user.bot,
            "Is Pending": user.pending,
            "Roles": roles,
            "Top Role": user.top_role,
            "Activity": user.activity and user.activity.name or "None",
            "Device": user.desktop_status and "Desktop" or user.mobile_status and "Mobile" or user.web_status and "Web" or "Unknown",
            "Status": user.status,
            "Is In Voice Channel": user.voice and user.voice.channel or "False",
        }, user)
        embed.set_thumbnail(url = user.avatar_url)
        await context.send(embed = embed)

    @commands.command()
    async def serverinfo(self, context):
        guild = context.guild

        humans = 0
        bots = 0

        online = 0
        idle = 0
        dnd = 0
        offline = 0

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

        embed = create_embed("Server Info", None, {
            "Name": guild.name,
            "ID": guild.id,
            "Creation Date": guild.created_at,
            "Owner": guild.owner.mention,
            "Region": guild.region,
            "Invites": len(await guild.invites()),
            "Member Count": guild.member_count,
            "Human Count": humans,
            "Bot Count": bots,
            "Ban Count": len(await guild.bans()),
            "Member Statuses": f"🟩 {online} 🟨 {idle} 🟥 {dnd} ⬜ {offline}",
            "Category Count": len(guild.categories),
            "Channel Count": len(guild.channels),
            "Text Channel Count": len(guild.text_channels),
            "Voice Channel Count": len(guild.voice_channels),
            "Emoji Count": len(guild.emojis),
            "Role Count": len(guild.roles)
        })
        embed.set_thumbnail(url = guild.icon_url)
        await context.send(embed = embed)

def setup(client):
    client.add_cog(default_commands(client))