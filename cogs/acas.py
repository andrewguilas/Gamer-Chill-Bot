BLACKLISTED_DAYS = [4, 5, 6]
REMINDER_BLOCK_TIMES = ["09:20:00", "10:50:00", "12:35:00", "14:35:00"]
BLOCK_TIMES = ["09:25:00", "10:55:00", "12:40:00", "14:40:00"]

import discord
from discord.ext import commands, tasks

import math
import pytz
import os
import asyncio
from datetime import datetime

from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://admin:QZnOT86qe3TQ@cluster0.meksl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
settings_data_store = cluster.discord_revamp.settings

def get_settings(guild_id: int):
    data = settings_data_store.find_one({"guild_id": guild_id}) 
    if not data:
        data = {"guild_id": guild_id}
        settings_data_store.insert_one(data)
    return data

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
        embed.set_thumbnail(url = info.thumbnail)
    
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
        current_time = str(now.strftime("%H:%M:%S"))
        status = None
        block_number = None

        if now.today().weekday() in BLACKLISTED_DAYS or self.is_paused:
            return

        if current_time in BLOCK_TIMES:
            status = "now"
            block_number = int(BLOCK_TIMES.index(current_time)) + 1
        elif current_time in REMINDER_BLOCK_TIMES:
            status = "early"
            block_number = int(REMINDER_BLOCK_TIMES.index(current_time)) + 1
        else:
            return
        
        all_guild_settings = list(settings_data_store.find({}))
        for guild_settings in all_guild_settings:
            guild = await self.client.fetch_guild(guild_settings["guild_id"])
            if not guild:
                continue

            if guild_settings["acas_enabled"] == False:
                continue

            acas_role_id = guild_settings.get("acas_role")
            if not acas_role_id:
                continue

            acas_role = guild.get_role(acas_role_id)
            if not acas_role:
                continue

            acas_channel_id = guild_settings.get("acas_channel")
            if not acas_channel_id:
                continue

            acas_channel = self.client.get_channel(acas_channel_id)
            if not acas_channel:
                continue

            if status == "now":
                await acas_channel.send(f"{acas_role.mention} **Block {block_number} is starting now!**")
            elif status == "early":
                await acas_channel.send(f"{acas_role.mention} Block {block_number} is starting in 5 minutes")

    @commands.command(aliases = ["toggleacas"], description = "Gives/removes the ACAS role to/from the member.")
    async def acas(self, context):
        will_give_role = True
        member = context.author
        response = await context.send(embed = create_embed({
            "title": "Giving ACAS role...",
            "color": discord.Color.gold(),
        }))

        try:
            guild_data = get_settings(context.guild.id)
            acas_role_id = guild_data.get("acas_role")
            if not acas_role_id:
                await response.edit(embed = create_embed({
                    "title": "Cannot find ACAS role",
                    "color": discord.Color.red()
                }))
                return

            acas_role = discord.utils.get(context.guild.roles, id = acas_role_id)
            if not acas_role:
                await response.edit(embed = create_embed({
                    "title": f"Role {acas_role_id} does not exist",
                    "color": discord.Color.red()
                }))
                return

            if acas_role in member.roles:
                await member.remove_roles(acas_role)
                will_give_role = False
            else:
                await member.add_roles(acas_role)

        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not give/remove ACAS role",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))
        else:
            await response.edit(embed = create_embed({
                "title": "{} ACAS role".format(will_give_role and "Gave" or "Removed"),
                "color": discord.Color.green()
            }))

def setup(client):
    client.add_cog(class_alert(client))