import discord
from discord.ext import commands
from helper import create_embed

class events(commands.Cog, description = 'Bot and server events.'):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_connect(self):
        print('connected') 

    @commands.Cog.listener()
    async def on_disconnect(self):
        print('disconnected')  

    @commands.Cog.listener()
    async def on_resumed(self):
        print('resumed')  

    @commands.Cog.listener()
    async def on_ready(self):
        print('ready')

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

def setup(client):
    client.add_cog(events(client))
