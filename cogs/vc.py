LANGUAGE = "en"
ACCENT = "com"
VOICE_IS_SLOW = False

import discord
from discord.ext import commands

from gtts import gTTS 
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://admin:QZnOT86qe3TQ@cluster0.meksl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
settings_data_store = cluster.discord_revamp.settings

def create_embed(info: {} = {}, fields: {} = {}):
    embed = discord.Embed(
        title = info.get("title") or "",
        description = info.get("description") or "",
        colour = info.get("color") or discord.Color.blue(),
        url = info.get("url") or "",
    )

    for name, value in fields.items():
        embed.add_field(name = name, value = value, inline = info.get("inline") or False)

    if info.get("author"):
        embed.set_author(name = info.author.name, url = info.author.mention, icon_url = info.author.avatar_url)
    if info.get("footer"):
        embed.set_footer(text = info.footer)
    if info.get("image"):
        embed.set_image(url = info.url)
    if info.get("thumbnail"):
        embed.set_thumbnail(url = info.thumbnail)
    
    return embed

def create_voice_file(message: str, guild_id: int):
    guild_settings = get_settings(guild_id)
    audio = gTTS(text = message, lang = guild_settings.get("vc_language") or LANGUAGE, tld = guild_settings.get("vc_accent") or ACCENT, slow = guild_settings.get("vc_slow_mode") or VOICE_IS_SLOW) 
    file_name = "TTS\\output_message.mp3"
    audio.save(file_name) 
    return file_name

def get_settings(guild_id: int):
    data = settings_data_store.find_one({"guild_id": guild_id}) 
    if not data:
        data = {"guild_id": guild_id}
        settings_data_store.insert_one(data)
    return data

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
            await voice_channel.connect()

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

    @commands.command()
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