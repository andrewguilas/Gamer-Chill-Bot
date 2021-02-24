import discord
from discord import Color as discord_color
from discord.ext import commands

import math
import pytz
from datetime import datetime

def create_embed(title, color = discord_color.default(), fields = {}):
    embed = discord.Embed(
        title = title,
        colour = color or discord_color.default()
    )

    for name, value in fields.items():
        embed.add_field(
            name = name,
            value = value,
            inline = False
        )

    embed.timestamp = datetime.now(tz = pytz.timezone("US/Eastern"))

    return embed

class moderation_commands(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_messages = True))
    async def clear(self, context, amount = 1):
        try:
            deleted_messages = await context.channel.purge(limit = amount + 1)
            deleted_messages_count = len(deleted_messages) - 1
        except Exception as error_message:
            await context.send(embed = create_embed(f"Error: Something went wrong when deleting {str(amount)} messages", discord_color.red(), {
                "Error Message": str(error_message)
            }))
        else:
            await context.send(embed = create_embed(f"Success: {str(deleted_messages_count)} messages were deleted", discord_color.green()))

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(kick_members = True))
    async def kick(self, context, member: discord.Member, *, reason = None):
        try:
            await member.kick(reason = reason)
        except Exception as error_message:
            embed = discord.Embed(
                title = f"Error: Something went wrong when kicking {str(member)}",
                colour = discord_color.red()
            )
            
            embed.add_field(
                name = "Error Message",
                value = str(error_message)
            )

            await context.send(embed = embed)
        else:
            await context.send(embed = discord.Embed(
                title = f"Success: {str(member)} was kicked", 
                colour = discord_color.green()
            ))

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(ban_members = True))
    async def ban(self, context, member: discord.Member, *, reason = None):
        try:
            await member.ban(reason = reason)
        except Exception as error_message:
            embed = discord.Embed(
                title = f"Error: Something went wrong when banning {str(member)}",
                colour = discord_color.red()
            )
            
            embed.add_field(
                name = "Error Message",
                value = str(error_message)
            )

            await context.send(embed = embed)
        else:
            await context.send(embed = discord.Embed(
                title = f"Success: {str(member)} was banned", 
                colour = discord_color.green()
            ))

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(ban_members = True))
    async def unban(self, context, *, member):
        try:
            banned_users = await context.guild.bans()
            member_name, member_discriminator = member.split("#")

            for ban_entry in banned_users:
                user = ban_entry.user

                if (user.name, user.discriminator) == (member_name, member_discriminator):
                    await context.guild.unban(user)
                    break
        except Exception as error_message:
            embed = discord.Embed(
                title = f"Error: Something went wrong when unbanning {str(member)}",
                colour = discord_color.red()
            )
            
            embed.add_field(
                name = "Error Message",
                value = str(error_message)
            )

            await context.send(embed = embed)
        else:
            await context.send(embed = discord.Embed(
                title = f"Success: {str(member)} was unbanned", 
                colour = discord_color.green()
            ))

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_roles = True))
    async def role(self, context, member: discord.Member, *, role: discord.Role):
        will_add_role = True

        try:
            if role in member.roles:
                await member.remove_roles(role)
                will_add_role = False
            else:
                await member.add_roles(role)
        except Exception as error_message:
            embed = discord.Embed(
                title = will_add_role and f"Error: Something went wrong when giving the role `{str(role)}` to {str(member)}" or f"Error: Something went wrong when removing the role `{str(role)}` from {str(member)}",
                colour = discord_color.red()
            )
            
            embed.add_field(
                name = "Error Message",
                value = str(error_message)
            )

            await context.send(embed = embed)
        else:
            await context.send(embed = discord.Embed(
                title = will_add_role and f"Success: The role `{str(role)}` given to {str(member)}" or f"Success: The role `{str(role)}` removed from {str(member)}", 
                colour = discord_color.green()
            ))

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(change_nickname = True))
    async def nick(self, context, member: discord.Member = None, *, new_nickname: str = ""): 
        if (not member):
            member = context.author

        try:
            await member.edit(nick = new_nickname)
        except Exception as error_message:
            fill_text = new_nickname and f"changing the nickname of {member} to {new_nickname}" or f"removing the nickname of {member}"
            await context.send(embed = create_embed(f"Error: Something went wrong when {fill_text}", discord_color.red(), {
                "Error Message": str(error_message)
            }))
        else:
            fill_text = new_nickname and f"changed to {new_nickname}" or "removed"
            await context.send(embed = create_embed(f"Success: {member}'s nickname was {fill_text}", color = discord_color.green()))

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(mute_members = True))
    async def mute(self, context, member: discord.Member = None): 
        if (not member):
            member = context.author

        will_mute = not member.voice.mute

        try:
            await member.edit(mute = will_mute)
        except Exception as error_message:
            fill = will_mute and "muting" or "unmuting"
            await context.send(embed = create_embed(f"Error: Something went wrong when {fill} {member}", discord_color.red(), {
                "Error Message": str(error_message)
            }))
        else:
            fill = will_mute and "muted" or "unmuted"
            await context.send(embed = create_embed(f"Success: {member} was {fill}", color = discord_color.green()))

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(mute_members = True))
    async def deafen(self, context, member: discord.Member = None): 
        if (not member):
            member = context.author

        will_deafen = not member.voice.deaf

        try:
            await member.edit(deafen = will_deafen)
        except Exception as error_message:
            fill = will_deafen and "deafening" or "undeafening"
            await context.send(embed = create_embed(f"Error: Something went wrong when {fill} {member}", discord_color.red(), {
                "Error Message": str(error_message)
            }))
        else:
            fill = will_deafen and "deafened" or "undeafened"
            await context.send(embed = create_embed(f"Success: {member} was {fill}", color = discord_color.green()))

def setup(client):
    client.add_cog(moderation_commands(client))