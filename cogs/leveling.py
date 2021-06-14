import discord
from discord.ext import commands, tasks
import time
import math

from helper import create_embed, get_guild_data, get_user_data, save_user_data, get_all_user_data
from constants import LEVELING_UPDATE_DELAY, LEVELING_LEVEL_DIFFICULTY, MAX_FILL, FILL_EMOJI, UNFILL_EMOJI, MAX_LEADERBOARD_FIELDS

def get_level_from_experience(experience, level_dificulty):
    return math.floor(experience / level_dificulty)

def get_experience_from_level(level, level_dificulty):
    return level * level_dificulty

class leveling(commands.Cog, description = "Leveling system commands."):
    def __init__(self, client):
        self.client = client
        self.recent_messagers = {}
        self.watch_members.start()

    def cog_unload(self):
        self.watch_members.cancel()

    def cog_load(self):
        self.watch_members.start()

    @tasks.loop(seconds = LEVELING_UPDATE_DELAY)
    async def watch_members(self):
        await self.client.wait_until_ready()

        for guild in self.client.guilds:
            guild_settings = get_guild_data(guild.id)

            for voice_channel in guild.voice_channels:
                if voice_channel == guild.afk_channel or len(voice_channel.members) < 2:
                    continue

                for member in voice_channel.members:
                    if member.bot or member.voice.self_deaf:
                        continue

                    # give exp
                    user_data = get_user_data(member.id)
                    old_level = get_level_from_experience(user_data["experience"], LEVELING_LEVEL_DIFFICULTY)
                    user_data["experience"] += guild_settings["voice_exp"]

                    new_level = get_level_from_experience(user_data["experience"], LEVELING_LEVEL_DIFFICULTY)
                    if old_level != new_level:
                        user_data["money"] += guild_settings["money_per_level"]
                    save_user_data(user_data)

    @commands.Cog.listener()
    async def on_message(self, message):
        author = message.author
        if author.bot or not message.guild:
            return

        # cooldown
        guild_settings = get_guild_data(message.guild.id)
        time_since_last_message = self.recent_messagers.get(author.id)
        if time_since_last_message and time.time() - time_since_last_message < guild_settings["message_cooldown"]:
            return
        self.recent_messagers[author.id] = time.time()

        # give exp
        user_data = get_user_data(author.id)
        old_level = get_level_from_experience(user_data["experience"], LEVELING_LEVEL_DIFFICULTY)
        user_data["experience"] += guild_settings["exp_per_message"]

        new_level = get_level_from_experience(user_data["experience"], LEVELING_LEVEL_DIFFICULTY)
        if old_level != new_level:
            user_data["money"] += guild_settings.get("money_per_level") * new_level
            await message.channel.send(embed = create_embed({
                "title": f"You leveled up to level {new_level}",
            }))

        save_user_data(user_data)

    @commands.command()
    async def rank(self, context, *, member: discord.Member = None):
        if not member:
            member = context.author
    
        if member.bot:
            await context.send(embed = create_embed({
                "title": f"{member} is a bot",
                "color": discord.Color.red()
            }))
            return

        response = await context.send(embed = create_embed({
            "title": f"Loading {member}'s rank...",
            "color": discord.Color.gold()
        }))

        try:
            user_data = get_user_data(member.id)
            level = get_level_from_experience(user_data["experience"], LEVELING_LEVEL_DIFFICULTY)
            experience = user_data["experience"] - get_experience_from_level(level, LEVELING_LEVEL_DIFFICULTY)
            experience_for_level = get_experience_from_level(level + 1, LEVELING_LEVEL_DIFFICULTY) - get_experience_from_level(level, LEVELING_LEVEL_DIFFICULTY)

            all_user_data = get_all_user_data("experience")
            guild_user_data = []
            for data in all_user_data:
                if context.guild and context.guild.get_member(data["user_id"]) or self.client.get_user(data["user_id"]):
                    guild_user_data.append(data)

            for index, member_data in enumerate(guild_user_data):
                if member_data["user_id"] == member.id:
                    rank = index + 1
                    break

            blue_boxes = int(experience / experience_for_level * MAX_FILL)
            white_boxes = (MAX_FILL - blue_boxes)
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
                "title": f"Could not load {member}'s rank",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command()
    async def leaderboard(self, context):
        response = await context.send(embed = create_embed({
            "title": f"Loading leaderboard...",
            "color": discord.Color.gold()
        }))

        try:
            fields = {}
            for user_data in get_all_user_data("experience"):
                member = context.guild and context.guild.get_member(user_data["user_id"]) or self.client.get_user(user_data["user_id"])
                if member:
                    rank = len(fields) + 1
                    level = get_level_from_experience(user_data["experience"], LEVELING_LEVEL_DIFFICULTY)
                    experience = user_data["experience"] - get_experience_from_level(level, LEVELING_LEVEL_DIFFICULTY)
                    experience_for_level = get_experience_from_level(level + 1, LEVELING_LEVEL_DIFFICULTY) - get_experience_from_level(level, LEVELING_LEVEL_DIFFICULTY)
                    fields[f"{rank + 1}. {member.name}"] = f"Level {level} ({experience}/{experience_for_level})"
                
                    if rank == MAX_LEADERBOARD_FIELDS - 1:
                        break
        
            await response.edit(embed = create_embed({
                "title": "Leaderboard"
            }, fields))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not load leaderboard",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command()
    @commands.guild_only()
    async def daily(self, context):
        response = await context.send(embed=create_embed({
            "title": "Claiming daily reward...",
            "color": discord.Color.gold()
        }))

        try:
            user_data = get_user_data(context.author.id)
            streak_message = ""
            if time.time() - user_data["claimed_daily_timestamp"] < 60 * 60 * 24:
                time_remaining_text = ""
                seconds = (60 * 60 * 24) - math.floor(time.time() - user_data["claimed_daily_timestamp"])
                if seconds < 60:
                    time_remaining_text = f"{seconds} second(s)"
                else:
                    minutes = math.floor(seconds / 60)
                    if minutes < 60:
                        time_remaining_text = f"{minutes} minute(s)"
                    else:
                        hours = math.floor(minutes / 60)
                        time_remaining_text = f"{hours} hour(s)"

                await response.edit(embed=create_embed({
                    "title": f"You must wait {time_remaining_text} to claim your daily reward",
                    "color": discord.Color.red()
                }))
                return
            else:
                if time.time() - user_data["claimed_daily_timestamp"] < 60 * 60 * 24 * 2:
                    user_data["daily_streak"] += 1
                    streak_message = "Your streak is {} days.".format(user_data["daily_streak"])
                elif user_data["daily_streak"] != 0:
                    streak_message = "You lost your streak of {} days.".format(user_data["daily_streak"])
                    user_data["daily_streak"] = 1
                user_data["claimed_daily_timestamp"] = round(time.time())

            guild_settings = get_guild_data(context.guild.id)
            old_level = get_level_from_experience(user_data["experience"], LEVELING_LEVEL_DIFFICULTY)
            user_data["experience"] += guild_settings["daily_exp"] * user_data["daily_streak"]

            new_level = get_level_from_experience(user_data["experience"], LEVELING_LEVEL_DIFFICULTY)
            if old_level != new_level:
                user_data["money"] += guild_settings.get("money_per_level") * new_level
                save_user_data(user_data)
                await response.edit(embed = create_embed({
                    "title": f"You claimed your daily reward and leveled up to level {new_level}. {streak_message}",
                    "color": discord.Color.green()
                }))
            else:
                save_user_data(user_data)
                await response.edit(embed = create_embed({
                    "title": f"You claimed your daily reward. {streak_message}",
                    "color": discord.Color.green()
                }))
        except Exception as error_message:
            await response.edit(embed=create_embed({
                "title": "Could not claim daily reward",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

def setup(client):
    client.add_cog(leveling(client))
