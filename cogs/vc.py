import discord
from discord.ext import commands
from gtts import gTTS 
from mutagen.mp3 import MP3
import asyncio

from helper import create_embed, get_settings
from constants import VC_LANGUAGE, VC_ACCENT, VC_VOICE_IS_SLOW

def create_voice_file(message: str, guild_id: int):
    guild_settings = get_settings(guild_id)
    audio = gTTS(text = message, lang = guild_settings.get("vc_language") or VC_LANGUAGE, tld = guild_settings.get("vc_accent") or VC_ACCENT, slow = guild_settings.get("vc_slow_mode") or VC_VOICE_IS_SLOW) 
    file_name = "TTS\\output_message.mp3"
    audio.save(file_name) 
    return file_name

class vc(commands.Cog, description = "Bot management for voice channels."):
    def __init__(self, client):
        self.client = client
        
    @commands.Cog.listener()
    async def on_voice_state_update(self, user, before, after):
        if user == self.client.user:
            return

        response = None

        voice_client = user.guild.voice_client
        if not voice_client:
            return
            
        if before.channel != after.channel:
            if after.channel == voice_client.channel:
                response = "joined"
            elif before.channel == voice_client.channel:
                response = "left"

            if response:
                response = f"{user.nick or user.name} {response}"
                voice_file = create_voice_file(response, user.guild.id)
                voice_client.stop()
                voice_client.play(discord.FFmpegPCMAudio(voice_file))

    @commands.command(aliases = ["summon"], description = "Makes the bot join the voice channel.")
    async def join(self, context):
        response = await context.send(embed = create_embed({
            "title": "Joining the voice channel...",
            "color": discord.Color.gold()
        }))

        try:
            user_voice = context.author.voice
            if not user_voice:
                await response.edit(embed = create_embed({
                    "title": "You are not in a voice channel",
                    "color": discord.Color.red()
                }))
                return

            voice_channel = user_voice.channel
            if not voice_channel:
                await response.edit(embed = create_embed({
                    "title": "You are not in a voice channel",
                    "color": discord.Color.red()
                }))
                return

            voice_client = context.voice_client
            if voice_client and voice_client.channel != voice_channel:
                await voice_client.disconnect()
            elif voice_client and voice_client.channel == voice_channel:
                await response.edit(embed = create_embed({
                    "title": "Bot is already connected to the voice channel",
                    "color": discord.Color.red()
                }))
                return
            voice_client = await voice_channel.connect()

            voice_file = create_voice_file("Gamer Chill Bot Joined", context.guild.id)
            voice_client.stop()
            voice_client.play(discord.FFmpegPCMAudio(voice_file))

            await response.edit(embed = create_embed({
                "title": f"Joined {voice_channel}",
                "color": discord.Color.green()
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not join voice channel",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))
            return

    @commands.command(description = "Makes the bot leave the voice channel.")
    async def leave(self, context):
        response = await context.send(embed = create_embed({
            "title": "Leaving the voice channel...",
            "color": discord.Color.gold()
        }))

        try:
            voice_channel_name = None
            voice_client = context.voice_client

            if voice_client and voice_client.channel:
                voice_file = create_voice_file("Gamer Chill Bot is Leaving", context.guild.id)
                voice_client.stop()
                voice_client.play(discord.FFmpegPCMAudio(voice_file))
                await asyncio.sleep(MP3(voice_file).info.length)

                voice_channel_name = voice_client.channel.name
                await voice_client.disconnect()
            else:
                await response.edit(embed = create_embed({
                    "title": "Bot is not in a voice channel",
                    "color": discord.Color.red()
                }))
                return

            await response.edit(embed = create_embed({
                "title": f"Left {voice_channel_name}",
                "color": discord.Color.green()
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not leave the voice channel",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))
            return

    @commands.command(description = "Says a TTS message in the voice channel.")
    async def say(self, context, *, message: str):
        response = await context.send(embed = create_embed({
            "title": "Saying message...",
            "color": discord.Color.gold()
        }, {
            "Message": message
        }))

        try:
            user_voice = context.author.voice
            if not user_voice:
                await response.edit(embed = create_embed({
                    "title": "You are not in a voice channel",
                    "color": discord.Color.red()
                }))
                return

            voice_channel = user_voice.channel
            if not voice_channel:
                await response.edit(embed = create_embed({
                    "title": "You are not in a voice channel",
                    "color": discord.Color.red()
                }))
                return

            voice_client = context.voice_client
            if voice_client and voice_client.channel != voice_channel:
                await voice_client.disconnect()
            if not voice_client or voice_client.channel != voice_channel:
                voice_client = await voice_channel.connect()

                voice_file = create_voice_file("Gamer Chill Bot Joined", context.guild.id)
                voice_client.stop()
                voice_client.play(discord.FFmpegPCMAudio(voice_file))
                await asyncio.sleep(MP3(voice_file).info.length + 1)
            
            voice_file = create_voice_file(message, context.guild.id)
            voice_client.stop()
            voice_client.play(discord.FFmpegPCMAudio(voice_file))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not say message",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message,
                "Message": message
            }))
        else:
            await response.edit(embed = create_embed({
                "title": "Message said",
                "color": discord.Color.green()
            }, {
                "Message": message
            }))

def setup(client):
    client.add_cog(vc(client))