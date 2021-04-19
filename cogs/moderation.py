import discord
from discord.ext import commands

from helper import create_embed, check_if_authorized

class moderation(commands.Cog, description = "Server and member management commands for moderation."):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ["delete"], description = "Clears a set amount of text messages.", brief = "bot creator or manage messages")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_messages = True))
    async def clear(self, context, amount: int = 1):
        DELETE_RESPONSE_DELAY = 3

        response = await context.send(embed = create_embed({
            "title": "Clearing messages...",
            "color": discord.Color.gold()
        }))

        deleted_messages_count = 0

        try:
            def check(context2):
                return context2.id != response.id

            deleted_messages = await context.channel.purge(limit = amount + 2, check = check)
            deleted_messages_count = len(deleted_messages) - 1
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not delete messages",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))
        else:
            await response.edit(embed = create_embed({
                "title": f"Deleted {deleted_messages_count} messages",
                "color": discord.Color.green()
            }), delete_after = DELETE_RESPONSE_DELAY)

    @commands.command(description = "Kicks a member from the server. They can join back.", brief = "bot creator or kick members")
    @commands.check_any(commands.is_owner(), commands.has_permissions(kick_members = True))
    async def kick(self, context, member: discord.Member, *, reason: str = None):
        response = await context.send(embed = create_embed({
            "title": f"Kicking {member}...",
            "color": discord.Color.gold()
        }, {
            "Reason": reason
        }))

        try:
            if not check_if_authorized(context, member):
                await response.edit(embed = create_embed({
                    "title": f"You cannot kick {member}",
                    "color": discord.Color.red()
                }, {
                    "Reason": reason
                }))
                return

            await member.kick(reason = reason)
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not kick {member}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message,
                "Reason": reason
            }))
        else:
            await response.edit(embed = create_embed({
                "title": f"{member} was kicked",
                "color": discord.Color.green()
            }, {
                "Reason": reason
            }))

    @commands.command(description = "Bans a member from the server. They cannot join back unless unbanned,", brief = "bot creator or ban members")
    @commands.check_any(commands.is_owner(), commands.has_permissions(ban_members = True))
    async def ban(self, context, member: discord.Member, *, reason = None):
        response = await context.send(embed = create_embed({
            "title": f"Banning {member}...",
            "color": discord.Color.gold()
        }, {
            "Reason": reason
        }))

        try:
            if not check_if_authorized(context, member):
                await response.edit(embed = create_embed({
                    "title": f"You cannot ban {member}",
                    "color": discord.Color.red()
                }, {
                    "Reason": reason
                }))
                return

            await member.ban(reason = reason)
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not ban {member}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message,
                "Reason": reason
            }))
        else:
            await response.edit(embed = create_embed({
                "title": f"{member} was banned",
                "color": discord.Color.green()
            }, {
                "Reason": reason
            }))

    @commands.command(description = "Unbans a banned member from the server, allowing them to join back.", brief = "bot creator or ban members")
    @commands.check_any(commands.is_owner(), commands.has_permissions(ban_members = True))
    async def unban(self, context, *, user: discord.User):
        response = await context.send(embed = create_embed({
            "title": f"Unbanning {user}...",
            "color": discord.Color.gold()
        }))

        try:
            if not user:
                await response.edit(embed = create_embed({
                    "title": f"Could not find {user}",
                    "color": discord.Color.red()
                }))
                return

            await context.guild.unban(user)
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not unban {user}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message,
            }))
        else:
            await response.edit(embed = create_embed({
                "title": f"{user} was unbanned",
                "color": discord.Color.green()
            }))

    @commands.command(description = "Gives/removes a role from a member.", brief = "bot creator or manage roles")
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_roles = True))
    async def role(self, context, member: discord.Member, *, role: discord.Role):
        response = await context.send(embed = create_embed({
            "title": f"Giving/removing {role} from {member}",
            "color": discord.Color.gold()
        }))

        gave_role = True

        try:
            if context.author != context.guild.owner and role.position >= member.top_role.position:
                await response.edit(embed = create_embed({
                    "title": "You don't have the power to give members this role",
                    "color": discord.Color.red()
                }))
                return

            if role in member.roles:
                await member.remove_roles(role)
                gave_role = False
            else:
                await member.add_roles(role)
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not give/remove {role} from {member}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))
        else:
            await response.edit(embed = create_embed({
                "title": "{fill_text} {role} {fill_text_2} {member}".format(
                    fill_text = gave_role and "Gave" or "Removed",
                    role = role,
                    member = member,
                    fill_text_2 = gave_role and "to" or "from"
                ),
                "color": discord.Color.green()
            }))

    @commands.command(aliases = ["nickname", "name"], description = "Changes the nickname of a member.", brief = "bot creator or change_nickname")
    @commands.check_any(commands.is_owner(), commands.has_permissions(change_nickname = True))
    async def nick(self, context, member: discord.Member, *, new_nickname: str = None): 
        response = await context.send(embed = create_embed({
            "title": f"Changing {member}'s nickname to {new_nickname}",
            "color": discord.Color.gold()
        }))
        
        try:
            if not check_if_authorized(context, member):
                await response.edit(embed = create_embed({
                    "title": f"You cannot change {member}'s nickname",
                    "color": discord.Color.red()
                }))
                return

            await member.edit(nick = new_nickname)
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not change {member}'s nickname to {new_nickname}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))
        else:
            await response.edit(embed = create_embed({
                "title": f"Changed {member}'s nickname to {new_nickname}",
                "color": discord.Color.green()
            }))

    @commands.command(aliases = ["silence"], description = "Mutes/unmutes the member in the voice channel.", brief = "bot creator or mute members")
    @commands.check_any(commands.is_owner(), commands.has_permissions(mute_members = True))
    async def mute(self, context, member: discord.Member = None): 
        if not member:
            member = context.author

        response = await context.send(embed = create_embed({
            "title": f"Muting/unmuting {member}...",
            "color": discord.Color.gold()
        }))

        if not member.voice or not member.voice.channel:
            await response.edit(embed = create_embed({
                "title": f"{member} is not connected to a voice channel",
                "color": discord.Color.red()
            }))
            return

        will_mute = not member.voice.mute

        try:
            await member.edit(mute = will_mute)
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not {status} {member}".format(
                    status = will_mute and "mute" or "unmute",
                    member = member
                ),
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))
        else:
            await response.edit(embed = create_embed({
                "title": "{status} {member}".format(
                    status = will_mute and "Muted" or "Unmuted",
                    member = member
                ),
                "color": discord.Color.green()
            }))

    @commands.command(description = "Deafens/undeafens the member in the voice channel.", brief = "bot creator or mute members")
    @commands.check_any(commands.is_owner(), commands.has_permissions(mute_members = True))
    async def deafen(self, context, member: discord.Member = None): 
        if not member:
            member = context.author

        response = await context.send(embed = create_embed({
            "title": f"Deafening/undeafening {member}...",
            "color": discord.Color.gold()
        }))

        if not member.voice or not member.voice.channel:
            await response.edit(embed = create_embed({
                "title": f"{member} is not connected to a voice channel",
                "color": discord.Color.red()
            }))
            return

        will_deafen = not member.voice.deaf

        try:
            await member.edit(deafen = will_deafen)
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not {status} {member}".format(
                    status = will_deafen and "deafen" or "undeafen",
                    member = member
                ),
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))
        else:
            await response.edit(embed = create_embed({
                "title": "{status} {member}".format(
                    status = will_deafen and "Deafened" or "Undeafened",
                    member = member
                ),
                "color": discord.Color.green()
            }))

    @commands.command(description = "Moves the member to the voice channel.", brief = "bot creator or move members")
    @commands.check_any(commands.is_owner(), commands.has_permissions(move_members = True))
    async def move(self, context, member: discord.Member, *, voice_channel: discord.VoiceChannel): 
        response = await context.send(embed = create_embed({
            "title": f"Moving {member} to {voice_channel}...",
            "color": discord.Color.gold()
        }))

        if not member.voice or not member.voice.channel:
            await response.edit(embed = create_embed({
                "title": f"{member} is not connected to a voice channel",
                "color": discord.Color.red()
            }))
            return

        try:
            await member.move_to(voice_channel)
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not move {member} to {voice_channel}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))
        else:
            await response.edit(embed = create_embed({
                "title": f"Moved {member} to {voice_channel}",
                "color": discord.Color.green()
            }))

def setup(client):
    client.add_cog(moderation(client))