LANGUAGE = "en"

# discord
import discord
from discord import Color as discord_color
from discord.ext import commands, tasks

# embed
import pytz
from datetime import datetime

# vc
from gtts import gTTS 
import os
import shutil

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
        if user == self.client.user:
            return

        response = None
        voice_channel = after.channel

        if before.channel != after.channel:
            if after.channel:
                response = "joined the voice channel"
            else:
                response = "left the voice channel"

        if response:
            response = f"{user.nick or user.name} {response}"
            bot_voice_client = self.client.voice_clients and self.client.voice_clients[0]
            if bot_voice_client and bot_voice_client.channel == voice_channel:
                voice_file = create_voice_file(response)
                bot_voice_client.play(discord.FFmpegPCMAudio(voice_file))

    @commands.command()
    async def join(self, context):
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

        try:
            await voice_channel.connect()
        except Exception as error_message:
            await context.send(embed = create_embed("ERROR: Something went wrong when trying to connect to the voice channel", {
                "Voice Channel": voice_channel,
                "Error Message": error_message,
            }, {
                "color": discord_color.red(),
                "member": context.author,
            }))
            return
        else:
            await context.send(embed = create_embed("SUCCESS: Joined the voice channel", {
                "Voice Channel": voice_channel,
            }, {
                "color": discord_color.green(),
                "member": context.author,
            }))

    @commands.command()
    async def leave(self, context):
        bot_voice_client = self.client.voice_clients
        if bot_voice_client:
            bot_voice_client = bot_voice_client[0]
            
        if bot_voice_client.channel:
            voice_channel_to_leave = str(bot_voice_client.channel)
            try:
                await bot_voice_client.disconnect()
            except Exception as error_message:
                await context.send(embed = create_embed("ERROR: Something went wrong when trying to disconnect from the voice channel", {
                    "Voice Channel Left": voice_channel_to_leave,
                    "Error Message": error_message,
                }, {
                    "color": discord_color.red(),
                    "member": context.author,
                }))
                return

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

def setup(client):
    client.add_cog(vc(client))