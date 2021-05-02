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
        if author.bot:
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
            user_data["money"] += guild_settings.get("money_per_level") or LEVELING_MONEY_PER_LEVEL * new_level
            await message.channel.send(embed = create_embed({
                "title": f"{message.author} leveled up to level {new_level}",
            }))

        save_user_data(user_data)

    @commands.command(description = "Retrieves the user's level, experience, and rank.")
    async def rank(self, context, member: discord.Member = None):
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
                if context.guild.get_member(data["user_id"]):
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

    @commands.command(description = "Retrieves the ranks of all the members in a server.")
    async def leaderboard(self, context):
        response = await context.send(embed = create_embed({
            "title": f"Loading leaderboard...",
            "color": discord.Color.gold()
        }))

        try:
            all_user_data = get_all_user_data("experience")
            guild_user_data = []
            for user_data in all_user_data:
                member = context.guild.get_member(user_data["user_id"])
                if member:
                    guild_user_data.append(user_data)

            fields = {}
            for rank, member_data in enumerate(guild_user_data):
                member = context.guild.get_member(member_data["user_id"])
                if member:
                    level = get_level_from_experience(member_data["experience"], LEVELING_LEVEL_DIFFICULTY)
                    experience = member_data["experience"] - get_experience_from_level(level, LEVELING_LEVEL_DIFFICULTY)
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

def setup(client):
    client.add_cog(leveling(client))
