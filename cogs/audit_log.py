CHANNEL_ID = 813453150886428742

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
            inline = True
        )

    embed.timestamp = datetime.now(tz = pytz.timezone("US/Eastern"))

    return embed

class audit_log(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.help_embeds = {
            "table_of_contents_embed": create_embed("Table of Contents", None, {
                "1 - Table of Contents": "List of event categories.",
                "2 - Bot": "Events for bot management.",
                "3 - Message": "Events for member sent messages.",
                "4 - Reaction": "Events for member reactions for messages.",
                "5 - Channel": "Events for server channels.",
                "6 - Member": "Events for server members.",
                "7 - Role": "Events for server roles.",
                "8 - Guild": "Events for server management."
            }),

            "bot_embed": create_embed("Bot", None, {
                "connect": "Fires when the bot is started. Events will run but commands will not run.",
                "disconnect": "Fires when the bot's connection has diconnected. Bot will not run.",
                "resumed": "Fires when the bot's connected was disconnected and has reconnected. Bot will run.",
                "ready": "Fires when the bot is ready to be used. Events and commands will run.",
            }),
            "message_embed": create_embed("Message", None, {
                "on_type": "Fires when a member starts typing in a text channel.",
                "message": "Fires when a member sends in a message in a text channel.",
                "message_delete": "Fires when a member's message is deleted.",
                "bulk_message_delete": "Fires when several messages were deleted.",
                "message_edit": "Fires when a member edit's their message.",
            }),
            "reaction_embed": create_embed("Reaction", None, {
                "reaction_add": "Fires when a member adds a reaction to a message.",
                "reaction_remove": "Fires when a member removes their reaction from a message.",
                "reaction_clear": "Fires when all of the reactions of a message were removed.",
            }),
            "channel_embed": create_embed("Channel", None, {
                "guild_channel_delete": "Fires when a channel was deleted.",
                "guild_change_create": "Fires when a channel was created.",
                "guild_change_update": "Fires when a channel's category, permissions, name, position; or a text channel's slow mode delay or topic; or a voice channel's bitrate or user limit; or a category's channels were updated.",
            }),
            "member_embed": create_embed("Member", None, {
                "member_join": "Fires when a member joins the server.",
                "member_remove": "Fires when a member leaves the server",
                "member_update": "Fires when a member's activity, nickname, roles, or pending status was updated.",
                "user_update": "Fires when a user's name or avatar was changed.",
            }),
            "role_embed": create_embed("Role", None, {
                "guild_role_create": "Fires when a role was created.",
                "guild_role_delete": "Fires when a role was deleted.",
                "guild_role_update": "Fires when a role's color, ability to mention, name, position, and permissions were changed.",
            }),
            "guild_embed": create_embed("Guild", None, {
                "guild_update": "please remind to finish this, there's about 50+ sub-events",
                "guild_emojis_update": "Fires when a guild adds or removes an emoji.",
                "voice_state_update": "Fires when a member joins, leaves, mutes, unmutes, is server muted, is unserver muted, is deafened, is undeafened, is server deafened, is unserver deafened, starts streaming, stops streaming, turns on their camera, turns off their camera a voice channel.",
                "member_ban": "Fires when a member was banned from the server.",
                "member_unban": "Fires when a member was unbanned from the server.",
                "invite_create": "Fires when an invite was created for the server.",
                "invite_delete": "Fires when an invite was deleted for the server.",
            }),
        }
        
        self.ordered_help_embeds = [
            self.help_embeds["table_of_contents_embed"],
            self.help_embeds["bot_embed"],
            self.help_embeds["message_embed"],
            self.help_embeds["reaction_embed"],
            self.help_embeds["channel_embed"],
            self.help_embeds["member_embed"],
            self.help_embeds["role_embed"],
            self.help_embeds["guild_embed"],
        ]

    @commands.command()
    async def listevents(self, context):
        EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣"]
        
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

    # bot

    @commands.Cog.listener()
    async def on_connect(self):
        print("Bot has connected") 

    @commands.Cog.listener()
    async def on_disconnect(self):
        print("Bot has disconnected")  

    @commands.Cog.listener()
    async def on_resumed(self):
        print("Bot has resumed")  

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot has started")
        logs_channel = self.client.get_channel(CHANNEL_ID)
        await logs_channel.send(embed = create_embed("Bot has started", None, {
            "Type": "Ready"
        }))

    """

    @commands.Cog.listener()
    async def on_error(self, event):
        logs_channel = self.client.get_channel(CHANNEL_ID)
        await logs_channel.send(embed = create_embed("An internal error occured", discord_color.red(), {
            "Type": "Error",
            "ErrorMessage": str(event)
        })) 

    @commands.Cog.listener()
    async def on_command_error(self, context, event):
        logs_channel = self.client.get_channel(CHANNEL_ID)
        embed = create_embed("An error occured when executing a command", discord_color.red(), {
            "Type": "Command Error",
            "Error Message": str(event),
            "Message": context.message.content,
            "Message ID": context.message.jump_url,
            "Author": context.message.author,
            "Channel": context.message.channel.mention,
            "Created At": context.message.created_at.strftime("%m/%d/%Y %H:%M:%S")
        })
        embed.set_footer(text = f"#{logs_channel}")
        embed.set_author(name = context.author, icon_url = context.author.avatar_url)
        await logs_channel.send(embed = embed) 

    """

    # message

    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        logs_channel = self.client.get_channel(CHANNEL_ID)
        embed = create_embed(f"{user} has started typing in #{channel}", discord_color.gold(), {
            "Type": "Typing",
            "User": user.mention,
            "Channel": channel.mention
        })
        embed.set_footer(text = f"#{logs_channel}")
        embed.set_author(name = user, icon_url = user.avatar_url)
        await logs_channel.send(embed = embed)

    @commands.Cog.  listener()
    async def on_message(self, context):
        if (context.author.bot):
            return

        logs_channel = self.client.get_channel(CHANNEL_ID)
        embed = create_embed(f"{context.author} has sent a message in #{context.channel}", None, {
            "Type": "Message",
            "Message": context.content or str(context.embeds),
            "Message ID": context.jump_url,
            "Author": context.author.mention,
            "Channel": context.channel.mention,
            "Created At": context.created_at.strftime("%m/%d/%Y %H:%M:%S")
        })
        embed.set_footer(text = f"#{logs_channel}")
        embed.set_author(name = context.author, icon_url = context.author.avatar_url)
        await logs_channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_message_delete(self, context):
        if (context.author.bot):
            return

        logs_channel = self.client.get_channel(CHANNEL_ID)
        embed = create_embed(f"{context.author}'s' message was deleted in #{context.channel}", None, {
            "Type": "Message Delete",
            "Message": context.content or str(context.embeds),
            "Message ID": context.jump_url,
            "Author": context.author.mention,
            "Channel": context.channel.mention,
            "Created At": context.created_at.strftime("%m/%d/%Y %H:%M:%S")
        })
        embed.set_footer(text = f"#{logs_channel}")
        embed.set_author(name = context.author, icon_url = context.author.avatar_url)
        await logs_channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages):
        logs_channel = self.client.get_channel(CHANNEL_ID)
        for index, context in enumerate(messages):
            if (not context):
                continue
                
            embed = create_embed(f"{context.author}'s' message was deleted in #{context.channel}", None, {
                "Type": "Bulk Message Delete",
                "Message": context.content or str(context.embeds),
                "Message ID": context.jump_url,
                "Author": context.author.mention,
                "Channel": context.channel.mention,
                "Created At": context.created_at.strftime("%m/%d/%Y %H:%M:%S"),
                "Bulk Index": f"{index}/{len(messages)}"
            })
            embed.set_footer(text = f"#{logs_channel}")
            embed.set_author(name = context.author, icon_url = context.author.avatar_url)
            await logs_channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_message_edit(self, previous_context, new_context):
        if (new_context.author.bot):
            return

        logs_channel = self.client.get_channel(CHANNEL_ID)
        embed = create_embed(f"{new_context.author} has edited a message in #{new_context.channel}", None, {
            "Type": "Message Edit",
            "Previous Message": previous_context.content or str(previous_context.embeds),
            "New Message": new_context.content or str(new_context.embeds),
            "Message ID": new_context.jump_url,
            "Author": new_context.author.mention,
            "Created At": new_context.created_at,
            "Channel": new_context.channel.mention
        })
        embed.set_footer(text = f"#{logs_channel}")
        embed.set_author(name = new_context.author, icon_url = new_context.author.avatar_url)
        await logs_channel.send(embed = embed)

    # reaction

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        logs_channel = self.client.get_channel(CHANNEL_ID)
        context = reaction.message
        embed = create_embed(f"{user} has added the reaction `{reaction}` to a message by {context.author} in #{context.channel}", None, {
            "Type": "Reaction Add",
            "User": user.mention,
            "Message": context.content or str(context.embeds) or str(context.embeds),
            "Message ID": context.jump_url,
            "Author": context.author.mention,
            "Created At": context.created_at,
            "Channel": context.channel.mention
        })
        embed.set_footer(text = f"#{logs_channel}")
        embed.set_author(name = user, icon_url = user.avatar_url)
        await logs_channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        logs_channel = self.client.get_channel(CHANNEL_ID)
        context = reaction.message
        embed = create_embed(f"{user} has removed the reaction `{reaction}` from a message by {context.author} in #{context.channel}", None, {
            "Type": "Reaction Remove",
            "User": user.mention,
            "Message": context.content or str(context.embeds) or str(context.embeds),
            "Message ID": context.jump_url,
            "Author": context.author.mention,
            "Created At": context.created_at,
            "Channel": context.channel.mention
        })
        embed.set_footer(text = f"#{logs_channel}")
        embed.set_author(name = user, icon_url = user.avatar_url)
        await logs_channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_reaction_clear(self, context, reactions):
        logs_channel = self.client.get_channel(CHANNEL_ID)
        context = reactions[0].message
        embed = create_embed(f"{len(reactions)} reactions were removed from a message by {context.author} in #{context.channel}", None, {
            "Type": "Reaction Clear",
            "Reactions": str(reactions),
            "Message": context.content or str(context.embeds) or str(context.embeds),
            "Message ID": context.jump_url,
            "Author": context.author.mention,
            "Created At": context.created_at,
            "Channel": context.channel.mention
        })
        embed.set_footer(text = f"#{logs_channel}")
        await logs_channel.send(embed = embed)

    # channel

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        logs_channel = self.client.get_channel(CHANNEL_ID)
        embed = create_embed(f"The {channel} channel was deleted", None, {
            "Type": "Guild Channel Delete",
            "Category": channel.category,
            "Position": channel.position,
            "Created At": channel.created_at,
            "Roles": channel.changed_roles,
            "Overwrites": channel.overwrites,
            "Permissions Synced": channel.permissions_synced
        })
        embed.set_footer(text = f"#{logs_channel}")
        await logs_channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        logs_channel = self.client.get_channel(CHANNEL_ID)
        embed = create_embed(f"The {channel} channel was deleted", None, {
            "Type": "Guild Channel Delete",
            "Category": channel.category,
            "Position": channel.position,
            "Created At": channel.created_at,
            "Roles": channel.changed_roles,
            "Overwrites": channel.overwrites,
            "Permissions Synced": channel.permissions_synced,
            "Invite Link (1 Hour)": await channel.create_invite(
                max_age = 3600,
                reasion = "Automatically created by Gamer Chill Bot upon the creation of the channel."
            )
        })
        embed.set_footer(text = f"#{logs_channel}")
        await logs_channel.send(embed = embed)
    
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        logs_channel = self.client.get_channel(CHANNEL_ID)
        
        if before.category != after.category:
            embed = create_embed(f"The category of {after} was changed from {before.category} to {after.category}", None, {
                "Type": "Guild Channel Update",
                "Channel": after.mention
            })
            embed.set_footer(text = f"#{logs_channel}")
            await logs_channel.send(embed = embed)
        
        if before.changed_roles != after.changed_roles:
            history = []

            for role in before.changed_roles:
                if not role in after.changed_roles:
                    history.append(f"Removed {role}")

            for role in after.changed_roles:
                if not role in before.changed_roles:
                    history.append(f"Added {role}")

            embed = create_embed(f"The permissions of {after} was changed", None, {
                "Type": "Guild Channel Update",
                "Permissions Changed": str(history),
                "Channel": after.mention
            })
            embed.set_footer(text = f"#{logs_channel}")
            await logs_channel.send(embed = embed)

        if before.name != after.name:
            embed = create_embed(f"#{before}'s name was changed to #{after}", None, {
                "Type": "Guild Channel Update",
                "Channel": after.mention
            })
            embed.set_footer(text = f"#{logs_channel}")
            await logs_channel.send(embed = embed)

        if before.position != after.position:
            embed = create_embed(f"#{after}'s position was changed from {before.position} to {after.position}", None, {
                "Type": "Guild Channel Update",
                "Channel": after.mention
            })
            embed.set_footer(text = f"#{logs_channel}")
            await logs_channel.send(embed = embed)

        if after.type == "text":
            if before.slowmode_delay != after.slowmode_delay:
                embed = create_embed(f"#{after}'s slowmode delay was changed from {before.slowmode_delay} to {after.slowmode_delay}", None, {
                    "Type": "Guild Channel Update",
                    "Channel": after.mention
                })
                embed.set_footer(text = f"#{logs_channel}")
                await logs_channel.send(embed = embed)

            if before.topic != after.topic:
                embed = create_embed(f"#{after}'s topic was changed from {before.topic} to {after.topic}", None, {
                    "Type": "Guild Channel Update",
                    "Channel": after.mention
                })
                embed.set_footer(text = f"#{logs_channel}")
                await logs_channel.send(embed = embed)
        elif after.type == "voice":
            if before.bitrate != after.bitrate:
                embed = create_embed(f"#{after}'s bitrate was changed from {before.bitrate} to {after.bitrate}", None, {
                    "Type": "Guild Channel Update",
                    "Channel": after.mention
                })
                embed.set_footer(text = f"#{logs_channel}")
                await logs_channel.send(embed = embed)

            if before.user_limit != after.user_limit:
                create_embed(f"#{after}'s user limit was changed from {before.user_limit} to {after.bitrate}", None, {
                    "Type": "Guild Channel Update",
                    "Channel": after.mention
                })
                embed.set_footer(text = f"#{logs_channel}")
                await logs_channel.send(embed = embed)
        elif after.type == "category":
            if before.text_channels != after.text_channels:
                history = []

                for channel in before.text_channels:
                    if not channel in after.text_channels:
                        history.append(f"Removed {channel}")

                for channel in after.text_channels:
                    if not channel in before.text_channels:
                        history.append(f"Added {channel}")

                embed = create_embed(f"#{after}'s text channels were updated", None, {
                    "Type": "Guild Channel Update",
                    "Text Channel Changes": str(history),
                    "Channel": after.mention
                })
                embed.set_footer(text = f"#{logs_channel}")
                await logs_channel.send(embed = embed)

            if before.voice_channels != after.voice_channels:
                history = []
                
                for channel in before.voice_channels:
                    if not channel in after.voice_channels:
                        history.append(f"Removed {channel}")

                for channel in after.voice_channels:
                    if not channel in before.voice_channels:
                        history.append(f"Added {channel}")

                embed = create_embed(f"#{after}'s voice channels were updated", None, {
                    "Type": "Guild Channel Update",
                    "Text Channel Changes": str(history),
                    "Channel": after.mention
                })
                embed.set_footer(text = f"#{logs_channel}")
                await logs_channel.send(embed = embed)

    # member

    @commands.Cog.listener()
    async def on_member_join(self, member):
        logs_channel = self.client.get_channel(CHANNEL_ID)

        role = discord.utils.get(member.guild.roles, name = "Lieutenant")
        await member.add_roles(role)

        embed = create_embed(f"{member} has joined the server", None, {
            "Type": "Member Join",
            "Pending": member.pending,
            "Account Created": member.created_at
        })
        embed.set_footer(text = f"#{logs_channel}")
        embed.set_author(name = member, icon_url = member.avatar_url)
        await logs_channel.send(embed = embed)

        embed = discord.Embed(
            title = "if you are reading this, then my bot works"
        )
        embed.set_author(name = member, icon_url = member.avatar_url)
        await member.send(embed = embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        logs_channel = self.client.get_channel(CHANNEL_ID)
        embed = create_embed(f"{member} has left the server", None, {
            "Type": "Member Remove",
            "Account Created": member.created_at
        })
        embed.set_footer(text = f"#{logs_channel}")
        embed.set_author(name = member, icon_url = member.avatar_url)
        await logs_channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_member_update(self, before_user, after_user):
        logs_channel = self.client.get_channel(CHANNEL_ID)

        if before_user.activity != after_user.activity:
            before_activity = before_user.activity and before_user.activity.name or "nothing"
            after_activity = after_user.activity and after_user.activity.name or "nothing"
            embed = create_embed(f"{after_user} was doing {before_activity} and is now doing {after_activity}", None, {
                "Type": "Member Update",
                "User": after_user.mention
            })
            embed.set_footer(text = f"#{logs_channel}")
            embed.set_author(name = after_user, icon_url = after_user.avatar_url)
            await logs_channel.send(embed = embed)

        if before_user.nick != after_user.nick:
            before_nick = before_user.nick or "nothing"
            after_nick = after_user.nick or "nothing"
            embed = create_embed(f"{after_user}'s nickname was changed from {before_nick} to {after_nick}", None, {
                "Type": "Member Update",
                "User": after_user.mention,
                "Account Created": after_user.created_at,
                "Joined": after_user.joined_at
            })
            embed.set_footer(text = f"#{logs_channel}")
            embed.set_author(name = after_user, icon_url = after_user.avatar_url)
            await logs_channel.send(embed = embed)

        if before_user.roles != after_user.roles:
            role_history = []

            for role in before_user.roles:
                if (not role in after_user.roles):
                    role_history.append(f"Removed {role.mention}")

            for role in after_user.roles:
                if (not role in before_user.roles):
                    role_history.append(f"Added {role.mention}")

            embed = create_embed(f"{after_user}'s roles were changed", None, {
                "Type": "Member Update",
                "Roles Changed": str(role_history),
                "User": after_user.mention,
                "Account Created": after_user.created_at,
                "Joined": after_user.joined_at
            })
            embed.set_footer(text = f"#{logs_channel}")
            embed.set_author(name = after_user, icon_url = after_user.avatar_url)
            await logs_channel.send(embed = embed)

        if before_user.pending != after_user.pending:
            embed = create_embed(f"{after_user} is pending for the server", None, {
                "Type": "Member Update",
                "User": after_user.mention,
                "Account Created": after_user.created_at,
                "Joined": after_user.joined_at
            })
            embed.set_footer(text = f"#{logs_channel}")
            embed.set_author(name = after_user, icon_url = after_user.avatar_url)
            await logs_channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_user_update(self, before_user, after_user):
        logs_channel = self.client.get_channel(CHANNEL_ID)

        if (before_user.name != after_user.name) or (before_user.discriminator != after_user.discriminator):
            embed = create_embed(f"{after_user}'s name was changed from {before_user} to {after_user}", None, {
                "Type": "User Update",
                "User": after_user.mention,
                "Account Created": after_user.created_at
            })
            embed.set_footer(text = f"#{logs_channel}")
            embed.set_author(name = after_user, icon_url = after_user.avatar_url)
            await logs_channel.send(embed = embed)

        if (before_user.avatar_url != after_user.avatar_url):
            embed = create_embed(f"{after_user}'s profile picture was changed", None, {
                "Type": "User Update",
                "Previous Profile Picture": before_user.avatar_url,
                "Current Profile Picture": after_user.avatar_url,
                "User": after_user.mention,
                "Account Created": after_user.created_at
            })
            embed.set_footer(text = f"#{logs_channel}")
            embed.set_author(name = after_user, icon_url = after_user.avatar_url)
            embed.set_thumbnail(url = after_user.avatar_url)
            await logs_channel.send(embed = embed)

    # role

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        logs_channel = self.client.get_channel(CHANNEL_ID)
        embed = create_embed(f"The role {role.mention} was created", None, {
            "Type": "Guild Role Create",
            "ID": role.id
        })
        embed.set_footer(text = f"#{logs_channel}")
        await logs_channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        logs_channel = self.client.get_channel(CHANNEL_ID)
        embed = create_embed(f"The role {role.mention} was deleted", None, {
            "Type": "Guild Role Delete",
            "ID": role.id,
            "Created At": role.created_at.strftime("%m/%d/%Y %H:%M:%S")
        })
        embed.set_footer(text = f"#{logs_channel}")
        await logs_channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        logs_channel = self.client.get_channel(CHANNEL_ID)

        if before.color != after.color:
            embed = create_embed(f"@{after}'s color was changed from {before.color} to {after.color}", None, {
                "Type": "Guild Role Update",
                "Integer Color Value": after.color.value,
                "Role": after.mention
            })
            embed.set_footer(text = f"#{logs_channel}")
            await logs_channel.send(embed = embed)

        if before.mentionable != after.mentionable:
            fill_text = after.mentionable and "now" or "no longer"
            embed = create_embed(f"@{after} is {fill_text} mentionable", None, {
                "Type": "Guild Role Update",
                "Role": after.mention
            })
            embed.set_footer(text = f"#{logs_channel}")
            await logs_channel.send(embed = embed)

        if before.name != after.name:
            embed = create_embed(f"@{after}'s name was changed from {before} to {after}", None, {
                "Type": "Guild Role Update",
                "Role": after.mention
            })
            embed.set_footer(text = f"#{logs_channel}")
            await logs_channel.send(embed = embed)

        if before.position != after.position:
            embed = create_embed(f"@{after}'s position was changed from {before} to {after}", None, {
                "Type": "Guild Role Update",
                "Role": after.mention
            })
            embed.set_footer(text = f"#{logs_channel}")
            await logs_channel.send(embed = embed)

        if before.permissions != after.permissions:
            history = []

            for permission in before.permissions:
                if (not permission in after.permissions):
                    history.append(f"Removed {permission}")

            for permission in after.permissions:
                if (not permission in before.permissions):
                    history.append(f"Added {permission}")

            embed = create_embed(f"@{after}'s permissions were changed", None, {
                "Type": "Guild Role Update",
                "Permissions Changed": str(history),
                "Role": after.mention
            })
            embed.set_footer(text = f"#{logs_channel}")
            await logs_channel.send(embed = embed)

    # guild

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        print("continue")

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, before, after):
        logs_channel = self.client.get_channel(CHANNEL_ID)
        history = []

        for emoji in before:
            if (not emoji in after):
                history.append(f"Removed {emoji}")

        for emoji in after:
            if (not emoji in before):
                history.append(f"Added {emoji}")

        embed = create_embed(f"The server's emojis were changed", None, {
            "Type": "Guide Emojis Update",
            "Changes": str(history)
        })
        embed.set_footer(text = f"#{logs_channel}")
        await logs_channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, user, before, after):
        logs_channel = self.client.get_channel(CHANNEL_ID)
        focused_channel = after.channel or before.channel

        if before.channel != after.channel:
            fill_text = after.channel and "joined" or "left"
            embed = create_embed(f"{user} has {fill_text} #{focused_channel}", None, {
                "Type": "Voice State Update",
                "User": user.mention,
                "Channel": focused_channel.mention
            })
            embed.set_author(name = user, icon_url = user.avatar_url)
            embed.set_footer(text = f"#{logs_channel}")
            await logs_channel.send(embed = embed)

        if before.self_mute != after.self_mute:
            fill_text = after.self_mute and "muted" or "unmuted"
            embed = create_embed(f"{user} has {fill_text} themself in `#{focused_channel}`", None, {
                "Type": "Voice State Update",
                "User": user.mention,
                "Channel": focused_channel.mention
            })
            embed.set_author(name = user, icon_url = user.avatar_url)
            embed.set_footer(text = f"#{logs_channel}")
            await logs_channel.send(embed = embed)

        if before.mute != after.mute:
            fill_text = after.mute and "server muted" or "unserver muted"
            embed = create_embed(f"{user} has been {fill_text} in #{focused_channel}", None, {
                "Type": "Voice State Update",
                "User": user.mention,
                "Channel": focused_channel.mention
            })
            embed.set_author(name = user, icon_url = user.avatar_url)
            embed.set_footer(text = f"#{logs_channel}")
            await logs_channel.send(embed = embed)

        if before.self_deaf != after.self_deaf:
            fill_text = after.self_deaf and "deafened" or "undeafened"
            embed = create_embed(f"{user} has {fill_text} themself in #{focused_channel}", None, {
                "Type": "Voice State Update",
                "User": user.mention,
                "Channel": focused_channel.mention
            })
            embed.set_author(name = user, icon_url = user.avatar_url)
            embed.set_footer(text = f"#{logs_channel}")
            await logs_channel.send(embed = embed)

        if before.deaf != after.deaf:
            fill_text = after.deaf and "server deafened" or "unserver deafened"
            embed = create_embed(f"{user} has been {fill_text} in #{focused_channel}", None, {
                "Type": "Voice State Update",
                "User": user.mention,
                "Channel": focused_channel.mention
            })
            embed.set_author(name = user, icon_url = user.avatar_url)
            embed.set_footer(text = f"#{logs_channel}")
            await logs_channel.send(embed = embed)

        if before.self_stream != after.self_stream:
            fill_text = after.self_stream and "started streaming" or "stopped streaming"
            embed = create_embed(f"{user} has {fill_text} in #{focused_channel}", None, {
                "Type": "Voice State Update",
                "User": user.mention,
                "Channel": focused_channel.mention
            })
            embed.set_author(name = user, icon_url = user.avatar_url)
            embed.set_footer(text = f"#{logs_channel}")
            await logs_channel.send(embed = embed)

        if before.self_video != after.self_video:
            fill_text = after.self_video and "turned on their camera" or "turned off their camera"
            embed = create_embed(f"{user} has {fill_text} in #{focused_channel}", None, {
                "Type": "Voice State Update",
                "User": user.mention,
                "Channel": focused_channel.mention
            })
            embed.set_author(name = user, icon_url = user.avatar_url)
            embed.set_footer(text = f"#{logs_channel}")
            await logs_channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        logs_channel = self.client.get_channel(CHANNEL_ID)
        embed = create_embed(f"{user} was banned from the server", None, {
            "Type": "Member Ban",
        })
        embed.set_author(name = user, icon_url = user.avatar_url)
        embed.set_footer(text = f"#{logs_channel}")
        await logs_channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_member_unban(self, user):
        logs_channel = self.client.get_channel(CHANNEL_ID)
        embed = create_embed(f"{user} was unbanned from the server", None, {
            "Type": "Member Unan",
        })
        embed.set_author(name = user, icon_url = user.avatar_url)
        embed.set_footer(text = f"#{logs_channel}")
        await logs_channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        logs_channel = self.client.get_channel(CHANNEL_ID)
        embed = create_embed(f"{invite.inviter} has created an invite for {invite.channel.mention}", None, {
            "Type": "Invite Create",
            "Code": invite.code,
            "Link": invite.link,
            "Temporary Membership": invite.temporary,
            "Uses": f"{invite.uses} / {invite.max_uses}",
            "Max Age": invite.max_age,
        })
        embed.set_author(name = invite.inviter, icon_url = invite.inviter.avatar_url)
        embed.set_footer(text = f"#{logs_channel}")
        await logs_channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        logs_channel = self.client.get_channel(CHANNEL_ID)
        embed = create_embed(f"{invite.inviter}'s  invite' for {invite.channel.mention} was deleted", None, {
            "Type": "Invite Delete",
            "Code": invite.code,
            "Link": invite.link,
            "Temporary Membership": invite.temporary,
            "Uses": f"{invite.uses} / {invite.max_uses}",
            "Created At": invite.created_at,
            "Max Age": invite.max_age,
            "Revoked": invite.revoked
        })
        embed.set_author(name = invite.inviter, icon_url = invite.inviter.avatar_url)
        embed.set_footer(text = f"#{logs_channel}")
        await logs_channel.send(embed = embed)

def setup(client):
    client.add_cog(audit_log(client))