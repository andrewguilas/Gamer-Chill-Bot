import discord
from discord.ext import commands

import pytz
from datetime import datetime
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://admin:QZnOT86qe3TQ@cluster0.meksl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
settings_data_store = cluster.discord_2.settings

def save_settings(data):
    settings_data_store.update_one({"guild_id": data["guild_id"]}, {"$set": data})
    
def get_settings(guild_id: int):
    data = settings_data_store.find_one({"guild_id": guild_id}) 
    if not data:
        data = {"guild_id": guild_id}
        settings_data_store.insert_one(data)
    return data

def get_channel(text_channels: [], value):
    channel = None

    try:
        channel = discord.utils.find(lambda channel: channel.name == value, text_channels) or discord.utils.find(lambda channel: channel.mention == value, text_channels) or discord.utils.find(lambda channel: channel.id == int(value), text_channels)
    except Exception as error_message:
        pass

    return channel

def get_role(roles: [], value):
    role = None

    try:
        role = discord.utils.find(lambda role: role.name == value, roles) or discord.utils.find(lambda role: role.mention == value, roles) or discord.utils.find(lambda role: role.id == int(value), roles)
    except Exception as error_message:
        pass

    return role

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

class events(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_connect(self):
        print("connected") 

    @commands.Cog.listener()
    async def on_disconnect(self):
        print("disconnected")  

    @commands.Cog.listener()
    async def on_resumed(self):
        print("resumed")  

    @commands.Cog.listener()
    async def on_ready(self):
        print("ready")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        settings = get_settings(member.guild.id)
        if settings.get("join_channel"):
            channel = self.client.get_channel(settings["join_channel"])
            if channel:
                await channel.send(embed = create_embed({
                    "title": f"{member} joined"
                }))

        if settings.get("default_role"):
            await member.add_roles(discord.utils.get(member.guild.roles, id = settings.get("default_role")))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        settings = get_settings(member.guild.id)
        if settings.get("join_channel"):
            channel = self.client.get_channel(settings["join_channel"])
            if channel:
                await channel.send(embed = create_embed({
                    "title": f"{member} left"
                }))

    @commands.command(aliases = ["set"])
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    async def setsettings(self, context, name: str, *, value = None):
        response = await context.send(embed = create_embed({
            "title": "Changing settings...",
            "color": discord.Color.gold(),
        }, {
            "Name": name,
            "Value": value,
        }))

        try:
            settings = get_settings(context.guild.id)
            if name == "join_channel":
                if not value or value == "None":
                    settings["join_channel"] = None
                    save_settings(settings)

                    await response.edit(embed = create_embed({
                        "title": "Removed join channel",
                        "color": discord.Color.green(),
                    }))
                else:
                    channel = get_channel(context.guild.text_channels, value)
                    if channel:
                        settings["join_channel"] = channel.id
                        save_settings(settings)

                        await response.edit(embed = create_embed({
                            "title": f"Set join channel to {channel}",
                            "color": discord.Color.green(),
                        }))
                    else:
                        await response.edit(embed = create_embed({
                            "title": f"{value} is not a valid channel",
                            "color": discord.Color.red(),
                        }))
            elif name == "default_role":
                if not value or value == "None":
                    settings["default_role"] = None
                    save_settings(settings)

                    await response.edit(embed = create_embed({
                        "title": "Removed default role",
                        "color": discord.Color.green(),
                    }))
                else:
                    role = get_role(context.guild.roles, value)
                    if role:
                        settings["default_role"] = role.id
                        save_settings(settings)

                        await response.edit(embed = create_embed({
                            "title": f"Set default role to {role}",
                            "color": discord.Color.green(),
                        }))
                    else:
                        await response.edit(embed = create_embed({
                            "title": f"{value} is not a valid role",
                            "color": discord.Color.red(),
                        }))
            else:
                await response.edit(embed = create_embed({
                    "title": f"{name} is not a valid setting",
                    "color": discord.Color.red(),
                }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Unable to change settings",
                "color": discord.Color.red(),
            }, {
                "Error Message": error_message,
                "Name": name,
                "Value": value,
            }))            

    @commands.command(aliases = ["settings"])
    @commands.check_any(commands.is_owner(), commands.has_permissions(administrator = True))
    async def getsettings(self, context):
        response = await context.send(embed = create_embed({
            "title": "Loading settings...",
            "color": discord.Color.gold(),
        }))

        try:
            settings = get_settings(context.guild.id)
            await response.edit(embed = create_embed({
                "title": "Settings",
            }, settings))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Unable to load settings",
                "color": discord.Color.red(),
            }, {
                "Error Message": error_message,
            }))

def setup(client):
    client.add_cog(events(client))