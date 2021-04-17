import discord
from discord.ext import commands
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://admin:QZnOT86qe3TQ@cluster0.meksl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
settings_data_store = cluster.discord_revamp.settings
 
def get_settings(guild_id: int):
    data = settings_data_store.find_one({"guild_id": guild_id}) 
    if not data:
        data = {"guild_id": guild_id}
        settings_data_store.insert_one(data)
    return data

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

class events(commands.Cog, description = "Bot and server events."):
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

def setup(client):
    client.add_cog(events(client))