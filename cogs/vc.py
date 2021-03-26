LANGUAGE = "en"
DEFAULT_ACCOUNT_DATA = {
    "id": None,
    "vc_name": None,
}

# discord
import discord
from discord import Color as discord_color
from discord.ext import commands, tasks

# embed
import pytz
from datetime import datetime

# vc
import os
import shutil
from gtts import gTTS 
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://admin:QZnOT86qe3TQ@cluster0.meksl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
account_data_store = cluster.discord.account

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

def save_account_data(data):
    account_data_store.update_one({"id": data["id"]}, {"$set": data})
    
def get_account_data(user_id: int):
    data = account_data_store.find_one({"id": user_id})
    if not data:
        data = DEFAULT_ACCOUNT_DATA
        data["id"] = user_id
        account_data_store.insert_one(data)
    return data 

def delete_contents(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def create_voice_file(message):
    audio = gTTS(text = message, lang = LANGUAGE, slow = False) 
    file_name = "TTS\\output_message.mp3"
    delete_contents("TTS")
    audio.save(file_name) 
    return file_name

class vc(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.nicknames = {}   

        vc_names = list(account_data_store.find({}))
        for data in vc_names:
            self.nicknames[data["id"]] = data["vc_name"]

    @commands.Cog.listener()
    async def on_voice_state_update(self, user, before, after):
        if user == self.client.user:
            return

        response = None
        voice_channel = after.channel

        if before.channel != after.channel:
            if after.channel:
                response = "joined"
            else:
                response = "left"

        if response:
            user_name = self.nicknames.get(user.id)
            if not user_name:
                data = get_account_data(user.id)
                user_name = data["vc_name"]
                self.nicknames[user.id] = user_name
                
            if not user_name:
                user_name = user.nick or user.name

            response = f"{user_name} {response}"
            print(response)
            bot_voice_client = self.client.voice_clients and self.client.voice_clients[0]
            if bot_voice_client and bot_voice_client.channel == before.channel or bot_voice_client.channel == after.channel:
                voice_file = create_voice_file(response)
                bot_voice_client.play(discord.FFmpegPCMAudio(voice_file))

    @commands.command()
    async def join(self, context):
        embed = await context.send(embed = create_embed("Joining the voice channel...", {}, {
            "color": discord_color.gold(),
            "member": context.author,
        }))

        user_voice = context.author.voice
        if not user_voice:
            await embed.edit(embed = create_embed("You are not in a voice channel", {}, {
                "color": discord_color.red(),
                "member": context.author,
            }))
            return

        voice_channel = user_voice.channel
        if not voice_channel:
            await embed.edit(embed = create_embed("You are not in a voice channel", {}, {
                "color": discord_color.red(),
                "member": context.author,
            }))
            return

        bot_voice_client = self.client.voice_clients and self.client.voice_clients[0]
        if bot_voice_client and bot_voice_client.channel != voice_channel:
            try:
                await bot_voice_client.disconnect()
            except Exception as error_message:
                await embed.edit(embed = create_embed("ERROR: Something went wrong when trying to connect to the voice channel", {
                    "Voice Channel": voice_channel,
                    "Error Message": error_message,
                }, {
                    "color": discord_color.red(),
                    "member": context.author,
                }))
                return

        try:
            await voice_channel.connect()
        except Exception as error_message:
            await embed.edit(embed = create_embed("ERROR: Something went wrong when trying to connect to the voice channel", {
                "Voice Channel": voice_channel,
                "Error Message": error_message,
            }, {
                "color": discord_color.red(),
                "member": context.author,
            }))
            return
        else:
            await embed.edit(embed = create_embed("SUCCESS: Joined the voice channel", {
                "Voice Channel": voice_channel,
            }, {
                "color": discord_color.green(),
                "member": context.author,
            }))

    @commands.command()
    async def leave(self, context):
        embed = await context.send(embed = create_embed("Leaving the voice channel...", {}, {
            "color": discord_color.gold(),
            "member": context.author,
        }))

        bot_voice_client = self.client.voice_clients and self.client.voice_clients[0]
        if not bot_voice_client.channel:
            await embed.edit(embed = create_embed("ERROR: Bot is not in a voice channel", {}, {
                "color": discord_color.red(),
                "member": context.author,
            }))
            return

        voice_channel_to_leave = str(bot_voice_client.channel)
        try:
            await bot_voice_client.disconnect()
        except Exception as error_message:
            await embed.edit(embed = create_embed("ERROR: Something went wrong when trying to disconnect from the voice channel", {
                "Voice Channel": voice_channel_to_leave,
                "Error Message": error_message,
            }, {
                "color": discord_color.red(),
                "member": context.author,
            }))
        else:
            await embed.edit(embed = create_embed("SUCCESS: Left the voice channel", {
                "Voice Channel": voice_channel_to_leave,
            }, {
                "color": discord_color.green(),
                "member": context.author,
            }))

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.member)
    async def say(self, context, *, message: str):
        embed = await context.send(embed = create_embed("Saying message...", {
            "Message": message,
        }, {
            "color": discord_color.gold(),
            "member": context.author,
        }))

        try:
            # join channel
            user_voice = context.author.voice
            if not user_voice:
                await context.send(embed = create_embed("You are not in a voice channel", {}, {
                    "color": discord_color.red(),
                    "member": context.author,
                }))
                return

            voice_channel = user_voice.channel
            if not voice_channel:
                await context.send(embed = create_embed("You are not in a voice channel", {}, {
                    "color": discord_color.red(),
                    "member": context.author,
                }))
                return

            bot_voice_client = self.client.voice_clients and self.client.voice_clients[0]
            if bot_voice_client and bot_voice_client.channel != voice_channel:
                try:
                    await bot_voice_client.disconnect()
                except Exception as error_message:
                    await context.send(embed = create_embed("ERROR: Something went wrong when trying to connect to the voice channel", {
                        "Voice Channel": voice_channel,
                        "Error Message": error_message,
                    }, {
                        "color": discord_color.red(),
                        "member": context.author,
                    }))
                    return

            if bot_voice_client and bot_voice_client.channel != voice_channel or not bot_voice_client:
                try:
                    bot_voice_client = await voice_channel.connect()
                except Exception as error_message:
                    await context.send(embed = create_embed("ERROR: Something went wrong when trying to connect to the voice channel", {
                        "Voice Channel": voice_channel,
                        "Error Message": error_message,
                    }, {
                        "color": discord_color.red(),
                        "member": context.author,
                    }))
                    return

            # say text
            voice_file = create_voice_file(message)
            bot_voice_client.play(discord.FFmpegPCMAudio(voice_file))

        except Exception as error_message:
            await embed.edit(embed = create_embed("ERROR: Something went wrong when saying the message", {
                "Message": message,
                "Error Message": error_message,
            }, {
                "color": discord_color.red(),
                "member": context.author,
            }))
        else:
            await embed.edit(embed = create_embed("SUCCESS: Message said", {
                "Message": message,
            }, {
                "color": discord_color.green(),
                "member": context.author,
            }))

    @commands.command()
    async def changevcname(self, context, *, name: str = None):
        user = context.author
        embed = await context.send(embed = create_embed(f"Changing voice channel name to {name}...", {}, {
            "color": discord_color.gold(),
            "member": user,
        }))

        self.nicknames[user.id] = name
        user_data = get_account_data(user.id)
        user_data["vc_name"] = name
        save_account_data(user_data)

        await embed.edit(embed = create_embed(f"Voice channel name changed to {name}", {}, {
            "color": discord_color.green(),
            "member": user,
        }))

def setup(client):
    client.add_cog(vc(client))