CLIENT_ID = "813258687229460490"

import discord
from discord.ext import commands
from discord import Color as discord_color

import pytz
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

class default_commands(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.help_embeds = {
            "table_of_contents_embed": create_embed("Table of Contents", None, {
                "1 - Table of Contents": "List of command categories",
                "2 - Default": "In general commands",
                "3 - Fun": "Commands for fun and games",
                "4 - Moderation": "Commands for moderation",
                "5 - Server": "Commands for server management",
                "6 - Bot": "Commands for bot management"
            }),

            "default_embed": create_embed("Default", None, {
                "help": "Returns a list of bot commands. No permissions required. Included in the `default_commands` set.",
                "helpold": "A legacy help command. No permissions required. Included in the `default_commands set`.",
                "ping": "Returns the user's ping. No permissions required. Included in the `default_commands` set.",
                "invitebot": "Returns an invite link for the bot. This bot was designed for this server specifically. No permissions required. Included in the `default_commands` set.",
                "invitetoserver": "Returns an invite link for the server (first text channel). Invite permissions required. Included in the `default_commands` set.",
                "invitetochannel": "Returns an invite link for the current channel. Invite permissions required. Included in the `default_commands` set.",
                "acas": "Gives the member a role to be notified when class starts and 5 minutes before. No permissions required. Included in the `class_alert` set.",
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
                "execute <CODE>": "Executes CODE. `Bot Creator` permissions required. Included in the `bot` set.",
                "cls": "Clears the terminal in the code editor. `Bot Creator` permissions required. Included in the `bot` set."
            }),
        }
        self.ordered_help_embeds = [
            self.help_embeds["table_of_contents_embed"],
            self.help_embeds["default_embed"],
            self.help_embeds["fun_embed"],
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
        EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]
        
        current_page = 0
        new_embed = self.ordered_help_embeds[current_page]
        new_embed.set_footer(text = f"Page {current_page + 1}/{len(self.ordered_help_embeds)}", icon_url = "")
        message = await context.send(embed = new_embed)

        for emoji in EMOJIS:
            await message.add_reaction(emoji)

        while True:
            def check_reaction(reaction, user):
                if user == context.author and reaction.message.channel == context.channel:
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

def setup(client):
    client.add_cog(default_commands(client))