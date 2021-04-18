import discord
from discord.ext import commands
from pymongo import MongoClient
import math

from secrets import MONGO_TOKEN
from constants import DEFAULT_GUILD_SETTINGS

cluster = MongoClient(MONGO_TOKEN)
settings_data_store = cluster.discord_revamp.settings

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

def get_settings(guild_id: int):
    data = settings_data_store.find_one({"guild_id": guild_id}) 
    if not data:
        data = DEFAULT_GUILD_SETTINGS.copy()
        settings_data_store.insert_one(data)
    return data

def save_settings(data):
    settings_data_store.update_one({"guild_id": data["guild_id"]}, {"$set": data})

def get_channel(text_channels: [], value):
    channel = None

    try:
        channel = discord.utils.find(lambda channel: channel.name == value, text_channels) or discord.utils.find(lambda channel: channel.mention == value, text_channels) or discord.utils.find(lambda channel: channel.id == int(value), text_channels)
    except Exception:
        pass

    return channel

def get_role(roles: [], value):
    role = None

    try:
        role = discord.utils.find(lambda role: role.name == value, roles) or discord.utils.find(lambda role: role.mention == value, roles) or discord.utils.find(lambda role: role.id == int(value), roles)
    except Exception:
        pass

    return role

def is_guild_owner():
    def predicate(context):
        return context.guild and context.guild.owner_id == context.author.id
    return commands.check(predicate)

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

def list_to_string(list: []):
    string = ""
    for index, value in enumerate(list):
        if index > 0:
            string = string + ", "
        string = string + value
    return string

def sort_dictionary(dictionary, is_reversed = False):
    sorted_dictionary = {}
    sorted_list = sorted(dictionary.items(), key = lambda x: x[1], reverse = is_reversed)
    for value in sorted_list:
        sorted_dictionary[value[0]] = value[1]
    return sorted_dictionary

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
