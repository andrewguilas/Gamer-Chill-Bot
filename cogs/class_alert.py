BLACKLISTED_DAYS = [4, 5, 6]
AUDIT_CHANNEL_ID = 813453150886428742
REMINDER_BLOCK_TIMES = ["09:20:00", "10:50:00", "12:35:00", "14:35:00"]
BLOCK_TIMES = ["09:25:00", "10:55:00", "12:40:00", "14:40:00"]
GUILD_ID = 651133204492845066
ROLE_ID = 816706859015995432
CHANNEL_ID = 816702193675403324

import discord
from discord import Color as discord_color
from discord.ext import commands, tasks

import math
import pytz
import os
import asyncio
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

class class_alert(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.is_paused = False
        self.class_alert.start()

    def cog_unload(self):
        self.class_alert.cancel()

    def cog_load(self):
        self.class_alert.start()

    @tasks.loop(seconds = 1)
    async def class_alert(self):
        await self.client.wait_until_ready()

        now = datetime.now(tz = pytz.timezone("US/Eastern"))
        
        if (now.today().weekday() in BLACKLISTED_DAYS) or (self.is_paused):
            return

        try:
            guild = await self.client.fetch_guild(GUILD_ID)
            role = guild.get_role(ROLE_ID)
            channel = self.client.get_channel(CHANNEL_ID)
            current_time = str(now.strftime("%H:%M:%S"))

            if current_time in BLOCK_TIMES:
                await channel.send(f"{role.mention} **Block {int(REMINDER_BLOCK_TIMES.index(current_time)) + 1} is starting now!**")
            elif current_time in REMINDER_BLOCK_TIMES:
                await channel.send(f"{role.mention} Block {int(BLOCK_TIMES.index(current_time)) + 1} is starting in 5 minutes")
        except Exception as error_message:
            logs_channel = self.client.get_channel(AUDIT_CHANNEL_ID)
            await logs_channel.send(embed = create_embed("ERROR: Something went wrong when running a class alert", discord_color.red(), {
                "Error Message": error_message
            }))

    @commands.command()
    async def acas(self, context):
        member = context.author
        role = discord.utils.get(context.guild.roles, id = ROLE_ID)
        will_give_role = True

        if role in member.roles:
            await member.remove_roles(role)
            will_give_role = False
        else:
            await member.add_roles(role)

        fill_text = will_give_role and "now" or "will no longer"
        await context.send(embed = create_embed(f"{member}, you will {fill_text} be notified 5 mintes and on the minute class starts", discord_color.green()))

    @commands.command()
    async def pauseacas(self, context):
        self.is_paused = False
        await context.send(embed = create_embed("SUCCESS: ACAS is now paused and will not alarm since there is no school today", discord_color.green()))

    @commands.command()
    async def resumeacas(self, context):
        self.is_paused = True
        await context.send(embed = create_embed("SUCCESS: ACAS has resumed and will alarm as there is school today", discord_color.green()))          

def setup(client):
    client.add_cog(class_alert(client))