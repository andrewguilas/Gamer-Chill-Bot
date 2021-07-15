import discord
from discord.ext import commands
from helper import create_embed, get_guild_data

class events(commands.Cog, description = 'Bot and server events.'):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_connect(self):
        print('Connected') 

    @commands.Cog.listener()
    async def on_disconnect(self):
        print('Disconnected')  

    @commands.Cog.listener()
    async def on_resumed(self):
        print('Resumed')  

    @commands.Cog.listener()
    async def on_ready(self):
        print('Ready')

    @commands.Cog.listener()
    async def on_command_error(self, context, error):
        if isinstance(error, commands.NoPrivateMessage):
            await context.send(embed=create_embed({
                'title': f'Commands must be used in servers',
                'color': discord.Color.red()
            }))
        elif isinstance(error, commands.PrivateMessageOnly):
            await context.send(embed=create_embed({
                'title': f'Commands must be used in DM\'s',
                'color': discord.Color.red()
            }))
        elif isinstance(error, commands.MissingPermissions) or isinstance(error, commands.CheckFailure):
            await context.send(embed=create_embed({
                'title': f'You do not have permission to run this command',
                'color': discord.Color.red()
            }))
        elif isinstance(error, commands.BadArgument) or isinstance(error, commands.MissingRequiredArgument):
            await context.send(embed=create_embed({
                'title': f'Incorrect syntax',
                'color': discord.Color.red()
            }))
        elif isinstance(error, commands.DisabledCommand):
            await context.send(embed=create_embed({
                'title': f'Command disabled',
                'color': discord.Color.red()
            }))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        guild_data = get_guild_data(member.guild.id)
        if guild_data['join_channel']:
            channel = member.guild.get_channel(guild_data['join_channel'])
            if channel:
                await channel.send(embed=create_embed({
                    'title': f'{member.name} joined'
                }))

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        guild_data = get_guild_data(member.guild.id)
        if guild_data['join_channel']:
            channel = member.guild.get_channel(guild_data['join_channel'])
            if channel:
                await channel.send(embed=create_embed({
                    'title': f'{member.name} left'
                }))

def setup(client):
    client.add_cog(events(client))
