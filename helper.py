import discord
from discord.ext import commands
from pymongo import MongoClient
import os
from constants import DEFAULT_GUILD_DATA, DEFAULT_USER_DATA, IS_TESTING, LIVE_DATASTORE, TESTING_DATASTORE

MONGO_TOKEN = os.getenv("GCB_DB_TOKEN")
cluster = MongoClient(MONGO_TOKEN)
datastore_name = IS_TESTING and TESTING_DATASTORE or LIVE_DATASTORE

guild_datastore = cluster[datastore_name]["guild"]
user_datastore = cluster[datastore_name]["user"]

# guild data

def attach_default_guild_data(guild_data):
    new_guild_data = DEFAULT_GUILD_DATA.copy()
    for key in new_guild_data.keys():
        if guild_data.get(key):
            new_guild_data[key] = guild_data[key]
    return new_guild_data

def get_guild_data(guild_id: int):
    guild_data = guild_datastore.find_one({"guild_id": guild_id})
    if not guild_data:
        guild_data = DEFAULT_GUILD_DATA.copy()
        guild_data["guild_id"] = guild_id
        guild_data = attach_default_guild_data(guild_data)
        guild_datastore.insert_one(guild_data)
    else:
        guild_data = attach_default_guild_data(guild_data)
    return guild_data

def save_guild_data(guild_data):
    guild_datastore.update_one({"guild_id": guild_data["guild_id"]}, {"$set": guild_data})

def get_all_guild_data(sort_value: str = None):
    all_data = sort_value and guild_datastore.find().sort(sort_value, -1) or guild_datastore.find({})
    for index, data in all_data.items():
        all_data[index] = attach_default_guild_data(data)
    return all_data

# user data

def attach_default_user_data(user_data):
    new_user_data = DEFAULT_USER_DATA.copy()
    for key in new_user_data.keys():
        if user_data.get(key):
            new_user_data[key] = user_data[key]
    return new_user_data

def get_user_data(user_id: int):
    user_data = user_datastore.find_one({"user_id": user_id})
    if not user_data:
        user_data = DEFAULT_USER_DATA.copy()
        user_data["user_id"] = user_id
        user_data = attach_default_user_data(user_data)
        user_datastore.insert_one(user_data)
    else:
        user_data = attach_default_user_data(user_data)
    return user_data

def save_user_data(user_data):
    user_datastore.update_one({"user_id": user_data["user_id"]}, {"$set": user_data})

def get_all_user_data(sort_value: str = None):
    all_data = sort_value and user_datastore.find().sort(sort_value, -1) or user_datastore.find({})
    for index, data in all_data.items():
        all_data[index] = attach_default_user_data(data)
    return all_data

# other

def get_object(objects: [], value):
    for obj in objects:
        try:
            if obj.name == value or value == obj.mention or obj.id == int(value):
                return obj
        except:
            pass

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
        embed.set_thumbnail(url = info.get("thumbnail"))
    
    return embed

def is_guild_owner():
    def predicate(context):
        return context.guild and context.guild.owner_id == context.author.id
    return commands.check(predicate)

def check_if_authorized(context, member: discord.Member):
    author_top_role = context.author.top_role
    member_top_role = member.top_role
    
    if member == context.guild.owner: # if target is server owner
        return False
    elif context.author == context.guild.owner: # is author server owner
        return True
    elif author_top_role and member_top_role and author_top_role.position > member_top_role.position: # is author higher than member
        return True
    elif author_top_role and not member_top_role: # does author have a role and member does not 
        return True
    else:
        return False

def format_time(timestamp):
    hours = math.floor(timestamp / 60 / 60)
    minutes = math.floor((timestamp - (hours * 60 * 60)) / 60)
    seconds = math.floor((timestamp) - (hours * 60 * 60) - (minutes * 60))

    hours = str(hours)
    if len(hours) == 1:
        hours = "0" + hours

    minutes = str(minutes)
    if len(minutes) == 1:
        minutes = "0" + minutes

    seconds = str(seconds)
    if len(seconds) == 1:
        seconds = "0" + seconds

    timestamp_text = f"{hours}:{minutes}:{seconds}"
    return timestamp_text

def sort_dictionary(dictionary, is_reversed = False):
    sorted_dictionary = {}
    sorted_list = sorted(dictionary.items(), key = lambda x: x[1], reverse = is_reversed)
    for value in sorted_list:
        sorted_dictionary[value[0]] = value[1]
    return sorted_dictionary
