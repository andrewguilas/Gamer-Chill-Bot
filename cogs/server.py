import discord
from discord.ext import commands
from discord import Color as discord_color

import pytz
import asyncio
import re
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

class server(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_webhooks = True))
    async def clearwebhooks(self, context, channel: discord.TextChannel = None):
        webhooks = await context.channel.webhooks()
        count = len(webhooks)
        
        if not channel:
            channel = context.channel

        if count == 0:
            await context.send(embed = create_embed(f"Success: There are no webhooks to delete in #{channel}", discord_color.green(), {
                "Webhooks": str(webhooks),
                "Channel": channel.mention,
            }))
            return

        embed = create_embed(f"Success: {count} webhooks were deleted in #{channel}", discord_color.green(), {
            "Webhooks": str(webhooks),
            "Channel": channel.mention,
        })

        try:
            for webhook in webhooks:
                await webhook.delete()
        except Exception as error_message:
            current_webhooks = await channel.webhooks()
            await context.send(embed = create_embed(f"Error: Something went wrong with deleting the webhooks in #{channel}", discord_color.red(), {
                "Webhooks": str(webhooks),
                "Amount Deleted": current_webhooks / count,
                "Channel": channel.mention,
                "Error Message": error_message,
            }))
        else:
            await context.send(embed = embed)

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(manage_webhooks = True))
    async def listwebhooks(self, context, channel: discord.TextChannel = None):
        if (not channel):
            channel = context.channel

        webhooks = await channel.webhooks()
        await context.send(embed = create_embed(f"There are {len(webhooks)} webhooks in #{channel}", None, {
            "Webhooks": str(webhooks),
            "Channel": channel.mention
        }))   

    @commands.command()
    async def messageleaderboard(self, context):
        BLACKLISTED_CHANNELS = ["army-command", "logs"]

        # create status embed
        embed = create_embed("Message Leaderboard", discord_color.gold(), {
            "Status": "Starting"
        })
        embed.set_footer(text = f"#{context.channel}")
        embed.set_author(name = context.author, icon_url = context.author.avatar_url)
        status = await context.send(embed = embed)

        # get messages
        messages = []
        for channel in context.guild.text_channels:
            if channel.name in BLACKLISTED_CHANNELS:
                continue

            embed = create_embed("Message Leaderboard", discord_color.gold(), {
                "Status": f"Scanning {channel.mention}"
            })
            embed.set_footer(text = f"#{context.channel}")
            embed.set_author(name = context.author, icon_url = context.author.avatar_url)
            await status.edit(embed = embed)

            messages = messages + await channel.history(limit = None).flatten()

        # scan saved messages
        embed = create_embed("Message Leaderboard", discord_color.gold(), {
            "Status": "Counting Scanned Messages: 0%"
        })
        embed.set_footer(text = f"#{context.channel}")
        embed.set_author(name = context.author, icon_url = context.author.avatar_url)
        await status.edit(embed = embed)
        
        member_history = {}
        message_count = len(messages)
        for index, message in enumerate(messages):
            if not member_history.get(message.author.name):
                member_history[message.author.name] = 1
            else:
                member_history[message.author.name] += 1

            if index % 100 == 0:
                embed = create_embed("Message Leaderboard", discord_color.gold(), {
                    "Status": f"Counting Scanned Messages: {round(index / message_count, 3) * 100}%"
                })
                embed.set_footer(text = f"#{context.channel}")
                embed.set_author(name = context.author, icon_url = context.author.avatar_url)
                await status.edit(embed = embed)
        
        # sort
        embed = create_embed("Message Leaderboard", discord_color.gold(), {
            "Status": f"Sorting Data"
        })
        embed.set_footer(text = f"#{context.channel}")
        embed.set_author(name = context.author, icon_url = context.author.avatar_url)
        await status.edit(embed = embed)

        sorted_member_history = {}
        sorted_keys = sorted(member_history, key = member_history.get, reverse = True)

        for w in sorted_keys:
            sorted_member_history[w] = member_history[w]

        # send data
        embed = create_embed("Message Leaderboard", discord_color.green(), sorted_member_history)
        embed.insert_field_at(index = -1, name = "TOTAL", value = message_count, inline = False)
        await status.edit(embed = embed)
    
    @commands.command()
    async def emojileaderboard(self, context):
        try:
            BLACKLISTED_CHANNELS = ["army-command", "logs"]

            # send embed

            embed = await context.send(embed = create_embed("Emoji Leaderboard", discord_color.gold(), {
                "Status": "Starting"
            }))
            await asyncio.sleep(2)

            # get messages
            messages = []
            channel_amount = len(context.guild.text_channels)
            for index, channel in enumerate(context.guild.text_channels):
                if channel.name in BLACKLISTED_CHANNELS:
                     continue

                await embed.edit(embed = create_embed("Emoji Leaderboard", discord_color.gold(), {
                    "Status": f"Retrieving messages from {channel.mention} ({round(index / channel_amount, 4) * 100}%)"
                }))

                messages = messages + await channel.history(limit = None).flatten()

            # get emojis

            await embed.edit(embed = create_embed("Emoji Leaderboard", discord_color.gold(), {
                "Status": f"Getting emojis"
            }))

            custom_emojis = await context.guild.fetch_emojis()
            custom_emojis_id = []
            for emoji in custom_emojis:
                custom_emojis_id.append(emoji.id)

            # scan messages
            emoji_history = {}
            message_amount = len(messages)
            for index, message in enumerate(messages):
                for emoji_id in custom_emojis_id:
                    occurances = len(re.findall(str(emoji_id), message.content))
                    if occurances == 0:
                        continue

                    if not emoji_history.get(emoji_id):
                        emoji_history[emoji_id] = occurances
                    else:
                        emoji_history[emoji_id] += occurances

                    if message_amount % 100 == 100:
                        await embed.edit(embed = create_embed("Emoji Leaderboard", discord_color.gold(), {
                            "Status": f"Scanning messages ({round(index / message_amount, 4) * 100}%)"
                        }))

            # sort

            await embed.edit(embed = create_embed("Emoji Leaderboard", discord_color.gold(), {
                "Status": f"Sorting Data"
            }))

            sorted_emoji_history = {}
            sorted_keys = sorted(emoji_history, key = emoji_history.get, reverse = True)

            for w in sorted_keys:
                sorted_emoji_history[w] = emoji_history[w]

            # get emoji name
            fields = {}
            for emoji_id, count in sorted_emoji_history.items():
                for emoji in custom_emojis:
                    if emoji.id == emoji_id:
                        fields[str(emoji)] = count
                        break

            # send embed
            await embed.edit(embed = create_embed("Emoji Leaderboard", None, fields))
        except Exception as error_message:
            await embed.edit(embed = create_embed(f"Error: Something went wrong when retrieving emoji leaderboard", discord_color.red(), {
                "Error Message": str(error_message)
            }))

def setup(client):
    client.add_cog(server(client))