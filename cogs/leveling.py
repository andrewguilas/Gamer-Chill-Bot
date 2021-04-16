UPDATE_DELAY = 30
MESSAGE_COOLDOWN = 30
MESSAGE_EXP = 5
LEVEL_DIFFICULTY = 20
MAX_BOXES_FOR_RANK_EMBED = 10

FILL_EMOJI = "🟦"
UNFILL_EMOJI = "⬜"

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

def get_experience_from_level(level, level_dificulty):
    return level * level_dificulty

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

    @commands.command(description = "Retrieves the user's level, experience, and rank.")
    async def rank(self, context, member: discord.Member = None):
        if not member:
            member = context.author
    
        response = await context.send(embed = create_embed({
            "title": f"Loading {member}'s rank...",
            "color": discord.Color.gold()
        }))

        try:
            level = None
            experience = None
            experience_for_level = None
            rank = None
            progress_bar = None

            guild_settings = get_settings(context.guild.id)
            level_dificulty = guild_settings.get("level_dificulty") or LEVEL_DIFFICULTY

            user_data = get_leveling_data(member.id)
            experience = user_data["experience"]
            level = get_level_from_experience(experience, level_dificulty)
            
            experience_for_level = get_experience_from_level(level + 1, level_dificulty)

            member_data = leveling_data_store.find().sort("experience", -1)
            for index, member_data in enumerate(member_data):
                if member_data["user_id"] == member.id:
                    rank = index + 1
                    break

            blue_boxes = int(experience / experience_for_level * MAX_BOXES_FOR_RANK_EMBED)
            white_boxes = (MAX_BOXES_FOR_RANK_EMBED - blue_boxes)
            progress_bar = blue_boxes * FILL_EMOJI + white_boxes * UNFILL_EMOJI

            await response.edit(embed = create_embed({
                "title": f"{member}'s rank...",
            }, {
                "Level": f"{level} ({experience}/{experience_for_level})",
                "Rank": rank,
                "Progress Bar": progress_bar
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not load {member}'s rank...",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

def setup(client):
    client.add_cog(subscriptions(client))