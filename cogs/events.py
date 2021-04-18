import discord
from discord.ext import commands
from helper import get_settings, create_embed

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