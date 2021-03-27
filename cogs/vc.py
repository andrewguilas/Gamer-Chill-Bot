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
    
def get_account_data(user_id):
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
        
    @commands.Cog.listener()
    async def on_voice_state_update(self, user, before, after):
        # check if user is a bot
        if user == self.client.user:
            return

        response = None

        voice_client = self.client.voice_clients and self.client.voice_clients[0]
        if not voice_client:
            return
            
        if before.channel != after.channel:
            if after.channel == voice_client.channel:
                response = "joined"
            else:
                response = "left"

            response = f"{user.nick or user.name} {response}"
            voice_file = create_voice_file(response)
            voice_client.stop()
            voice_client.play(discord.FFmpegPCMAudio(voice_file))

    @commands.command()
    async def join(self, context):
        embed = await context.send(embed = create_embed("Joining the voice channel...", {}, {
            "color": discord_color.gold(),
            "member": context.author,
        }))

        try:
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

            voice_client = context.voice_client
            if voice_client and voice_client.channel != voice_channel:
                await voice_client.disconnect()
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

        voice_channel_name = None
        try:
            voice_client = context.voice_client
            if voice_client and voice_client.channel:
                voice_channel_name = voice_client.channel.name
                await voice_client.disconnect()
            else:
                await embed.edit(embed = create_embed("ERROR: Bot is not in a voice channel", {}, {
                    "color": discord_color.red(),
                    "member": context.author,
                }))
        except Exception as error_message:
                await embed.edit(embed = create_embed("ERROR: Something went wrong when trying to disconnect the bot from the voice channel", {
                    "Voice Channel": voice_channel_name or "Unknown",
                    "Error Message": error_message,
                }, {
                    "color": discord_color.red(),
                    "member": context.author,
                }))
                return
        else:
            await embed.edit(embed = create_embed("SUCCESS: Left the voice channel", {
                "Voice Channel": voice_channel_name,
            }, {
                "color": discord_color.green(),
                "member": context.author,
            }))

    @commands.command()
    async def say(self, context, *, message: str):
        embed = await context.send(embed = create_embed("Saying message...", {
            "Message": message,
        }, {
            "color": discord_color.gold(),
            "member": context.author,
        }))

        try:
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

            voice_client = context.voice_client
            # bot is not in a vc
            if not voice_client:
                voice_client = await voice_channel.connect()
            # bot is in another vc
            elif voice_client.channel != voice_channel:
                await voice_client.disconnect()
                voice_client = await voice_channel.connect()

            voice_file = create_voice_file(message)
            voice_client.stop()
            voice_client.play(discord.FFmpegPCMAudio(voice_file))
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

def setup(client):
    client.add_cog(vc(client))