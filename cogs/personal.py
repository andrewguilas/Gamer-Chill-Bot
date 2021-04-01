STATUS_URL = "http://api.roblox.com/users/USER_ID/onlinestatus/"
USERNAME_URL = "http://api.roblox.com/users/USER_ID"
USER_ID = 353933582
UPDATE_DELAY = 5
USER_TO_NOTIFY = 496001579292295169

OFFLINE_EMOJI = "🔴"
ONLINE_EMOJI = "🟢"

import discord
from discord import Color as discord_color
from discord.ext import commands, tasks

import math
import pytz
import os
import asyncio

import requests
import time

from datetime import datetime

def create_embed(title, fields: {} = {}, info: {} = {}):
    embed = discord.Embed(
        title = title,
        colour = info.get("color") or discord_color.blue(),
        timestamp = datetime.now(tz = pytz.timezone("US/Eastern"))
    )

    for name, value in fields.items():
        embed.add_field(
            name = name,
            value = value,
            inline = True
        )

    if info.get("member"):
        embed.set_author(name = info["member"], icon_url = info["member"].avatar_url)

    return embed

class personal(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.is_online = False
        self.roblox_user_status.start()

    def cog_unload(self):
        self.roblox_user_status.cancel()

    def cog_load(self):
        self.roblox_user_status.start()

    @tasks.loop(seconds = UPDATE_DELAY)
    async def roblox_user_status(self):
        user = await self.client.fetch_user(USER_TO_NOTIFY)
        user_data = requests.get(USERNAME_URL.replace("USER_ID", str(USER_ID))).json()
        status_data = requests.get(STATUS_URL.replace("USER_ID", str(USER_ID))).json()

        status = status_data["LastLocation"].lower()
        is_online = status == "online" or status == "playing"
        if self.is_online != is_online:
            self.is_online = is_online
            await user.send("{status_emoji} {username} is **{status}** ({current_time})".format(
                status_emoji = self.is_online and ONLINE_EMOJI or OFFLINE_EMOJI,
                username = user_data["Username"],
                status = self.is_online and "online" or "offline",
                current_time = datetime.now(tz = pytz.timezone("US/Eastern")).strftime("%m/%d/%y - %I:%M %p")
            ))

def setup(client):
    client.add_cog(personal(client))