UPDATE_DELAY = 30
MESSAGE_COOLDOWN = 30
MESSAGE_EXP = 5
LEVEL_DIFFICULTY = 20

import discord
from discord.ext import commands, tasks
from datetime import datetime
from pymongo import MongoClient
import time
import math

cluster = MongoClient("mongodb+srv://admin:QZnOT86qe3TQ@cluster0.meksl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
leveling_data_store = cluster.discord_revamp.leveling
settings_data_store = cluster.discord_revamp.settings

def get_settings(guild_id: int):
    data = settings_data_store.find_one({"guild_id": guild_id}) 
    if not data:
        data = {"guild_id": guild_id}
        settings_data_store.insert_one(data)
    return data

def get_level_from_experience(experience, level_dificulty):
    return math.floor(experience / level_dificulty)

def save_leveling_data(data):
    leveling_data_store.update_one({"user_id": data["user_id"]}, {"$set": data})
    
def get_leveling_data(user_id: int):
    data = leveling_data_store.find_one({"user_id": user_id}) 
    if not data:
        data = {"user_id": user_id, "experience": 0}
        leveling_data_store.insert_one(data)
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

class subscriptions(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.recent_messagers = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        author = message.author

        if author.bot:
            return

        # cooldown
        guild_settings = get_settings(message.guild.id)
        level_dificulty = guild_settings.get("level_dificulty") or LEVEL_DIFFICULTY
        time_since_last_message = self.recent_messagers.get(author.id)
        if time_since_last_message:
            duration_since_last_message = int(time.time() - time_since_last_message)
            cooldown = int(guild_settings.get("message_cooldown") or MESSAGE_COOLDOWN)
            if duration_since_last_message < cooldown:
                return
            else:
                self.recent_messagers[author.id] = None
        else:
            self.recent_messagers[author.id] = time.time()

        # give exp
        user_data = get_leveling_data(author.id)
        old_level = get_level_from_experience(user_data["experience"], level_dificulty)
        user_data["experience"] += guild_settings.get("message_exp") or MESSAGE_EXP
        save_leveling_data(user_data)

        # check level
        new_level = get_level_from_experience(user_data["experience"], level_dificulty)
        if old_level != new_level:
            await message.channel.send(embed = create_embed({
                "title": f"{message.author} leveled up to level {new_level}",
            }))

def setup(client):
    client.add_cog(subscriptions(client))