import discord
from discord.ext import commands
from gtts import gTTS 
from mutagen.mp3 import MP3
import asyncio
import os
from helper import create_embed
from constants import TEMP_PATH, TTS_PATH

def create_voice_file(message):
    audio = gTTS(text=message) 
    if not os.path.isdir(TEMP_PATH):
        os.mkdir(TEMP_PATH)
    audio.save(TTS_PATH) 
    return TTS_PATH

class vc(commands.Cog):
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
                response = 'joined'
            elif before.channel == voice_client.channel:
                response = 'left'

            if response:
                voice_file = create_voice_file(f'{user.nick or user.name} {response}')
                voice_client.stop()
                voice_client.play(discord.FFmpegPCMAudio(voice_file))

    @commands.command(aliases = ['summon'])
    @commands.guild_only()
    async def join(self, context):
        response = await context.send(embed=create_embed({
            'title': 'Joining the voice channel...',
            'color': discord.Color.gold()
        }))

        try:
            user_voice = context.author.voice
            if not user_voice:
                await response.edit(embed=create_embed({
                    'title': 'You are not in a voice channel',
                    'color': discord.Color.red()
                }))
                return

            voice_channel = user_voice.channel
            if not voice_channel:
                await response.edit(embed=create_embed({
                    'title': 'You are not in a voice channel',
                    'color': discord.Color.red()
                }))
                return

            voice_client = context.voice_client
            if voice_client and voice_client.channel != voice_channel:
                await voice_client.disconnect()
            elif voice_client and voice_client.channel == voice_channel:
                await response.edit(embed=create_embed({
                    'title': 'Bot is already connected to the voice channel',
                    'color': discord.Color.red()
                }))
                return
            voice_client = await voice_channel.connect()

            voice_file = create_voice_file('Gamer Chill Bot Joined')
            voice_client.stop()
            voice_client.play(discord.FFmpegPCMAudio(voice_file))

            await response.edit(embed=create_embed({
                'title': f'Joined {voice_channel}',
                'color': discord.Color.green()
            }))
        except Exception as error_message:
            await response.edit(embed=create_embed({
                'title': 'Could not join the voice channel',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))

            print('ERROR: Could not join VC')
            print(error_message)

    @commands.command()
    @commands.guild_only()
    async def leave(self, context):
        response = await context.send(embed=create_embed({
            'title': 'Leaving the voice channel...',
            'color': discord.Color.gold()
        }))

        try:
            voice_channel_name = None
            voice_client = context.voice_client

            if voice_client and voice_client.channel:
                voice_file = create_voice_file('Gamer Chill Bot is Leaving')
                voice_client.stop()
                voice_client.play(discord.FFmpegPCMAudio(voice_file))
                await asyncio.sleep(MP3(voice_file).info.length)

                voice_channel_name = voice_client.channel.name
                await voice_client.disconnect()
            else:
                await response.edit(embed=create_embed({
                    'title': 'Bot is not in a voice channel',
                    'color': discord.Color.red()
                }))
                return

            await response.edit(embed=create_embed({
                'title': f'Left {voice_channel_name}',
                'color': discord.Color.green()
            }))
        except Exception as error_message:
            await response.edit(embed=create_embed({
                'title': 'Could not leave the voice channel',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))

            print('ERROR: Could not leave VC')
            print(error_message)

    @commands.command()
    @commands.guild_only()
    async def say(self, context, *, message: str):
        response = await context.send(embed=create_embed({
            'title': f'Saying {message}...',
            'color': discord.Color.gold()
        }))

        try:
            user_voice = context.author.voice
            if not user_voice:
                await response.edit(embed=create_embed({
                    'title': 'You are not in a voice channel',
                    'color': discord.Color.red()
                }))
                return

            voice_channel = user_voice.channel
            if not voice_channel:
                await response.edit(embed=create_embed({
                    'title': 'You are not in a voice channel',
                    'color': discord.Color.red()
                }))
                return

            voice_client = context.voice_client
            if voice_client and voice_client.channel != voice_channel:
                await voice_client.disconnect()
            if not voice_client or voice_client.channel != voice_channel:
                voice_client = await voice_channel.connect()
                voice_file = create_voice_file('Gamer Chill Bot Joined')
                voice_client.stop()
                voice_client.play(discord.FFmpegPCMAudio(voice_file))
                await asyncio.sleep(MP3(voice_file).info.length + 1)
            
            voice_file = create_voice_file(message)
            voice_client.stop()
            voice_client.play(discord.FFmpegPCMAudio(voice_file))

            await response.edit(embed=create_embed({
                'title': f'Said {message}',
                'color': discord.Color.green()
            }))
        except Exception as error_message:
            await response.edit(embed=create_embed({
                'title': f'Could not say {message}',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message,
            }))

            print('ERROR: Could not say {message}')
            print(error_message)

def setup(client):
    client.add_cog(vc(client))