import discord
from discord.ext import commands
import math
import asyncio
import dotenv
import os
from pymongo import MongoClient
from constants import IS_TESTING, TEST_DATASTORE, PRODUCTION_DATASTORE, DEFAULT_GUILD_DATA, DEFAULT_USER_DATA

dotenv.load_dotenv('.env')
DB_TOKEN = os.getenv('DB_TOKEN')
cluster = MongoClient(DB_TOKEN)
datastore_name = IS_TESTING and TEST_DATASTORE or PRODUCTION_DATASTORE
guild_datastore = cluster[datastore_name]["guild"]
user_datastore = cluster[datastore_name]["user"]

# guild data

def attach_default_guild_data(guild_data):
    new_guild_data = DEFAULT_GUILD_DATA.copy()
    for key in new_guild_data.keys():
        new_value = guild_data.get(key)
        if new_value:
            new_guild_data[key] = new_value
    return new_guild_data

def get_guild_data(guild_id: int):
    guild_data = guild_datastore.find_one({"guild_id": guild_id})
    if guild_data:
        guild_data = attach_default_guild_data(guild_data)
    else:
        guild_data = DEFAULT_GUILD_DATA.copy()
        guild_data["guild_id"] = guild_id
        guild_data = attach_default_guild_data(guild_data)
        guild_datastore.insert_one(guild_data)
    return guild_data

def save_guild_data(guild_data):
    guild_datastore.update_one({"guild_id": guild_data["guild_id"]}, {"$set": guild_data})

# user data

def attach_default_user_data(user_data):
    new_user_data = DEFAULT_USER_DATA.copy()
    for key in new_user_data.keys():
        new_value = user_data.get(key)
        if new_value:
            new_user_data[key] = new_value
    return new_user_data

def get_user_data(user_id: int):
    user_data = user_datastore.find_one({"user_id": user_id})
    if user_data:
        user_data = attach_default_user_data(user_data)
    else:
        user_data = DEFAULT_USER_DATA.copy()
        user_data["user_id"] = user_id
        user_data = attach_default_user_data(user_data)
        user_datastore.insert_one(user_data)
    return user_data

def save_user_data(user_data):
    user_datastore.update_one({"user_id": user_data["user_id"]}, {"$set": user_data})

def get_all_user_data(sort_value=None):
    all_data = sort_value and user_datastore.find().sort(sort_value, -1) or user_datastore.find({})
    formatted_all_data = [attach_default_user_data(data) for data in all_data]
    return formatted_all_data

# misc

def get_object(objects, value):
    for obj in objects:
        try:
            if obj.name == value or value == obj.mention or str(obj.id) in value or obj.id == int(value):
                return obj
        except:
            pass

def create_embed(info={}, fields={}):
    embed = discord.Embed(
        title = info.get('title') or '',
        description = info.get('description') or '',
        colour = info.get('color') or discord.Color.blue(),
        url = info.get('url') or f'',
    )

    for name, value in fields.items():
        embed.add_field(name=name, value=value, inline=info.get('inline') or False)

    if info.get('author'):
        embed.set_author(name=info.author.name, url=info.author.mention, icon_url=info.author.avatar_url)
    if info.get('footer'):
        embed.set_footer(text=info.get('footer'))
    if info.get('image'):
        embed.set_image(url=info.url)
    if info.get('thumbnail'):
        embed.set_thumbnail(url=info.get('thumbnail'))
    
    return embed

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
        hours = '0' + hours

    minutes = str(minutes)
    if len(minutes) == 1:
        minutes = '0' + minutes

    seconds = str(seconds)
    if len(seconds) == 1:
        seconds = '0' + seconds

    timestamp_text = f'{hours}:{minutes}:{seconds}'
    return timestamp_text

def sort_dictionary(dictionary, is_reversed=False):
    sorted_dictionary = {}
    sorted_list = sorted(dictionary.items(), key=lambda x: x[1], reverse=is_reversed)
    for value in sorted_list:
        sorted_dictionary[value[0]] = value[1]
    return sorted_dictionary

def get_first_n_items(dictionary, number):
    new_dictionary = {}
    for index in list(dictionary)[:number]:
        new_dictionary[index] = dictionary.get(index)
    return new_dictionary

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def attach_prefix_to_number(number, prefix):
    if number < 0:
        number = abs(number)
        return f'-{prefix}{number}'
    elif number > 0:
        return f'+{prefix}{number}'
    elif number == 0:
        return f'{prefix}{number}'

def attach_suffix_to_number(number, suffix):
    if number < 0:
        number = abs(number)
        return f'-{number}{suffix}'
    elif number > 0:
        return f'+{number}{suffix}'
    elif number == 0:
        return f'{number}{suffix}'

async def wait_for_reaction(client, context, emoji=None, timeout=30):
    def check_response(reaction, user):
        if user == context.author and reaction.message.channel == context.channel:
            if emoji:
                return type(emoji) == list and reaction.emoji in emoji or reaction.emoji == emoji
            else:
                return True

    try:
        reaction, user = await client.wait_for('reaction_add', check=check_response, timeout=timeout)
        return reaction, user
    except asyncio.TimeoutError:
        return None, None

async def wait_for_message(client, context, timeout=30):
    def check_message(message):
        return message.author == context.author

    try:
        message = await client.wait_for('message', check=check_message, timeout=timeout)
        return message
    except asyncio.TimeoutError:
        return None
