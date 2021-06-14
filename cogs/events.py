import discord
from discord.ext import commands
from helper import get_guild_data, create_embed

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
        guild_data = get_guild_data(member.guild.id)
        join_channel_id = guild_data.get("join_channel")
        if join_channel_id:
            channel = member.guild.get_channel(join_channel_id)
            if channel:
                await channel.send(embed = create_embed({
                    "title": f"{member} joined"
                }))

        default_role_id = guild_data.get("default_role")
        if default_role_id:
            role = member.guild.get_role(default_role_id)
            if role:
                await member.add_roles(role)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild_data = get_guild_data(member.guild.id)
        join_channel_id = guild_data.get("join_channel")
        if join_channel_id:
            channel = member.guild.get_channel(join_channel_id)
            if channel:
                await channel.send(embed = create_embed({
                    "title": f"{member} left"
                }))

    @commands.Cog.listener()
    async def on_command_error(self, context, error):
        if isinstance(error, commands.NoPrivateMessage):
            await context.send(embed = create_embed({
                "title": f"Commands must be used in servers",
                "color": discord.Color.red()
            }))
        elif isinstance(error, commands.PrivateMessageOnly):
            await context.send(embed = create_embed({
                "title": f"Commands must be used in DM's",
                "color": discord.Color.red()
            }))
        elif isinstance(error, commands.MissingPermissions) or isinstance(error, commands.CheckFailure):
            await context.send(embed = create_embed({
                "title": f"You do not have permission to run this command",
                "color": discord.Color.red()
            }))
        elif isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):
            await context.send(embed = create_embed({
                "title": f"Incorrect syntax",
                "color": discord.Color.red()
            }))
        elif isinstance(error, commands.DisabledCommand):
            await context.send(embed = create_embed({
                "title": f"Command disabled",
                "color": discord.Color.red()
            }))

    @commands.Cog.listener()
    async def on_message(self, message):
        author = message.author
        if author.bot or not message.guild:
            return

        if author.id == 467789718646685706 and message.content.lower() == "ok":
            await message.delete()

def setup(client):
    client.add_cog(events(client))
