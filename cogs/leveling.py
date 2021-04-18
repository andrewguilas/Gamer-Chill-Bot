import discord
from discord.ext import commands, tasks
import time
import math

from helper import create_embed, get_settings, get_user_data, save_user_data, get_all_user_data
from constants import LEVELING_UPDATE_DELAY, LEVELING_MESSAGE_COOLDOWN, LEVELING_MESSAGE_EXP, LEVELING_VOICE_EXP, LEVELING_LEVEL_DIFFICULTY, LEVELING_MAX_BOXES_FOR_RANK_EMBED, LEVELING_MAX_FIELDS_FOR_LEADERBOARD_EMBED, LEVELING_FILL_EMOJI, LEVELING_UNFILL_EMOJI

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
            guild_settings = get_settings(guild.id)

            for voice_channel in guild.voice_channels:
                for member in voice_channel.members:
                    if member.voice.self_deaf:
                        continue

                    user_data = get_user_data(member.id)
                    user_data["experience"] += guild_settings.get("LEVELING_voice_exp") or LEVELING_VOICE_EXP
                    save_user_data(user_data)

    @commands.Cog.listener()
    async def on_message(self, message):
        author = message.author

        if author.bot:
            return

        # cooldown
        guild_settings = get_settings(message.guild.id)
        level_dificulty = guild_settings.get("level_dificulty") or LEVELING_LEVEL_DIFFICULTY
        time_since_last_message = self.recent_messagers.get(author.id)
        if time_since_last_message:
            duration_since_last_message = int(time.time() - time_since_last_message)
            cooldown = int(guild_settings.get("LEVELING_message_cooldown") or LEVELING_MESSAGE_COOLDOWN)
            if duration_since_last_message < cooldown:
                return
            else:
                self.recent_messagers[author.id] = None
        else:
            self.recent_messagers[author.id] = time.time()

        # give exp
        user_data = get_user_data(author.id)
        old_level = get_level_from_experience(user_data["experience"], level_dificulty)
        user_data["experience"] += guild_settings.get("LEVELING_message_exp") or LEVELING_MESSAGE_EXP
        save_user_data(user_data)

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
            "title": f"Loading {member}'s rank",
            "color": discord.Color.gold()
        }))

        try:
            guild_settings = get_settings(context.guild.id)
            level_dificulty = guild_settings.get("level_dificulty") or LEVELING_LEVEL_DIFFICULTY

            user_data = get_user_data(member.id)
            experience = user_data["experience"]
            level = get_level_from_experience(experience, level_dificulty)
            
            experience_for_level = get_experience_from_level(level + 1, level_dificulty)

            all_user_data = get_all_user_data("experience")
            guild_user_data = []
            for data in all_user_data:
                member = context.guild.get_member(data["user_id"])
                if member:
                    guild_user_data.append(data)

            for index, member_data in enumerate(guild_user_data):
                if member_data["user_id"] == member.id:
                    rank = index + 1
                    break

            blue_boxes = int(experience / experience_for_level * LEVELING_MAX_BOXES_FOR_RANK_EMBED)
            white_boxes = (LEVELING_MAX_BOXES_FOR_RANK_EMBED - blue_boxes)
            progress_bar = blue_boxes * LEVELING_FILL_EMOJI + white_boxes * LEVELING_UNFILL_EMOJI

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

    @commands.command(description = "Retrieves the ranks of all the members in a server.")
    async def leaderboard(self, context):
        response = await context.send(embed = create_embed({
            "title": f"Loading leaderboard...",
            "color": discord.Color.gold()
        }))

        try:
            guild_settings = get_settings(context.guild.id)
            level_dificulty = guild_settings.get("level_dificulty") or LEVELING_LEVEL_DIFFICULTY

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
                    experience = member_data["experience"]
                    level = get_level_from_experience(experience, level_dificulty)
                    experience_for_level = get_experience_from_level(level + 1, level_dificulty)
                    fields[f"{rank + 1}. {member.name}"] = f"Level {level} ({experience}/{experience_for_level})"
                
                if rank == LEVELING_MAX_FIELDS_FOR_LEADERBOARD_EMBED - 1:
                    break
        
                await response.edit(embed = create_embed({
                    "title": "Leaderboard"
                }, fields))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not load leaderboard...",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

def setup(client):
    client.add_cog(leveling(client))