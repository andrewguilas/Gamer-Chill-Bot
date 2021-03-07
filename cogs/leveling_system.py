MIN_MSG_EXP_GAIN, MAX_MSG_EXP_GAIN = 4, 8
MIN_VC_EXP_GAIN, MAX_VC_EXP_GAIN = 1, 2
STARTING_LEVEL = 1
STARTING_EXPERIENCE = 0
LEVEL_DIFFICULTY = 20
MAX_BOXES_FOR_RANK_EMBED = 20
MAX_FIELDS_FOR_LEADERBOARD_EMBED = 10
BOT_CHANNEL = 813757261045563432
MESSAGE_COOLDOWN = 30

import discord
from discord import Color as discord_color
from discord.ext import commands

import math
import pytz
import os
import random
import asyncio
import time
from datetime import datetime
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://admin:QZnOT86qe3TQ@cluster0.meksl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
leveling = cluster.discord.leveling
recent_messagers = {}

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

def is_guild_owner():
    def predicate(ctx):
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id
    return commands.check(predicate)

def get_total_experience_of_level(level):
    return level * LEVEL_DIFFICULTY

def get_data(user_id):
    return leveling.find_one({"id": user_id})

def save_data(user_id, data):
    leveling.update_one({"id": user_id}, {"$set": data})

def insert_data(data):
    leveling.insert_one(data)

def give_experience(user_id, amount):
    new_level = False

    # cooldown for gaining EXP
    if recent_messagers.get(user_id):
        if time.time() - recent_messagers[user_id] < MESSAGE_COOLDOWN:
            return new_level
        else:
            recent_messagers[user_id] = None
    else:
        recent_messagers[user_id] = time.time()   

    stats = get_data(user_id)
    if not stats:
        insert_data({
            "id": user_id, 
            "level": STARTING_LEVEL, 
            "experience": STARTING_EXPERIENCE, 
            "total_experience": STARTING_EXPERIENCE
        })
        return False

    level = stats["level"]
    experience = stats["experience"] + amount
    total_experience = stats["total_experience"] + amount

    if experience >= get_total_experience_of_level(level):
        level += 1
        experience = 0
        new_level = level

    save_data(user_id, {
        "level": level,
        "experience": experience,
        "total_experience": total_experience,
    })

    return new_level

class leveling_system(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        random_experience_gain = random.randint(MIN_MSG_EXP_GAIN, MAX_MSG_EXP_GAIN)
        new_level = give_experience(message.author.id, random_experience_gain)
        if new_level:
            await message.channel.send(embed = create_embed(f"{message.author} leveled to level {new_level}"))

    @commands.Cog.listener()
    async def on_voice_state_update(self, user, before, after):
        level_up_channel = self.client.get_channel(BOT_CHANNEL)

        # check if user joined the vc
        if before.channel != after.channel and after.channel:
            while True:
                await asyncio.sleep(60)

                # check if user left the vc
                if not user.voice:
                    break
                
                # check if the vc is deafened
                if user.voice.self_deaf:
                    continue

                random_experience_gain = random.randint(MIN_VC_EXP_GAIN, MAX_VC_EXP_GAIN)
                new_level = give_experience(user.id, random_experience_gain)
                if new_level:
                    await level_up_channel.send(embed = create_embed(f"{user} leveled to level {new_level}"))

    @commands.command()
    async def rank(self, context, member: discord.Member = None):
        if not member:
            member = context.author

        stats = leveling.find_one({"id": member.id})
        level = stats and stats["level"] or STARTING_LEVEL
        experience = stats and stats["experience"] or STARTING_EXPERIENCE
        rank = 0

        boxes = int(experience / get_total_experience_of_level(level) * MAX_BOXES_FOR_RANK_EMBED)

        member_stats = leveling.find().sort("experience", -1)
        for member_stat in member_stats:
            rank += 1
            if stats["id"] == member_stat["id"]:
                break

        embed = create_embed(f"{member}'s rank", None, {
            "Name": member.mention,
            "Level": level,
            "Experience": f"{experience}/{get_total_experience_of_level(level)}",
            "Rank": rank,
            "Progress Bar": boxes * ":blue_square:" + (MAX_BOXES_FOR_RANK_EMBED - boxes) * ":white_large_square:"
        })
        embed.set_author(name = member, icon_url = member.avatar_url)
        embed.set_thumbnail(url = member.avatar_url)
        await context.send(embed = embed)

    @commands.command()
    async def leaderboard(self, context):
        if context.author.bot:
            return

        embed = await context.send(embed = create_embed("Leaderboard", discord_color.gold(), {
            "Status": "Loading leaderboard..."
        }))

        member_stats = leveling.find().sort("total_experience", -1)
        fields = {}
        for place, member_stat in enumerate(member_stats):
            try:
                member = context.guild.get_member(member_stat["id"])
                experience = member_stat["experience"]
                level = member_stat["level"]
                fields[f"{place + 1}. {member.name}"] = f"Level {level} ({experience}/{get_total_experience_of_level(level)})"
            except:
                pass

            if place == MAX_FIELDS_FOR_LEADERBOARD_EMBED - 1:
                break

        await embed.edit(embed = create_embed("Leaderboard", None, fields))

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    async def setlevel(self, context, member: discord.Member, amount: int = None):
        if not amount:
            return

        data = get_data(member.id)
        data["level"] += amount
        save_data(member.id, data)
        await context.send(embed = create_embed(f"Set {member}'s level to {amount}"))

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    async def setexperience(self, context, member: discord.Member, amount: int = None):
        data = get_data(member.id)
        data["experience"] += amount
        data["total_experience"] += amount

        if data["experience"] >= get_total_experience_of_level(data["level"]):
            data["level"] += 1
            data["experience"] = 0

        save_data(member.id, data)
        await context.send(embed = create_embed(f"Set {member}'s experience to {amount}"))

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    async def settotalexperience(self, context, member: discord.Member, amount: int = None):
        data = get_data(member.id)
        data["experience"] += amount
        data["total_experience"] += amount

        if data["experience"] >= get_total_experience_of_level(data["level"]):
            data["level"] += 1
            data["experience"] = 0

        save_data(member.id, data)
        await context.send(embed = create_embed(f"Set {member}'s total experience to {amount}"))

    @commands.command()
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    async def addexperience(self, context, member: discord.Member, amount: int = None):
        give_experience(member.id, amount)
        await context.send(embed = create_embed(f"Gave {member} {amount} experience"))

def setup(client):
    client.add_cog(leveling_system(client))