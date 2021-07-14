import discord
from discord.ext import commands
from helper import create_embed, get_user_data, get_all_user_data

class economy(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def bal(self, context, *, user: discord.User = None):
        if not user:
            user = context.author

        if user.bot:
            await context.send(embed=create_embed({
                'title': f'{user} is a bot',
                'color': discord.Color.red()
            }))
            return

        response = await context.send(embed=create_embed({
            'title': f'Loading {user}\'s balance',
            'color': discord.Color.gold()
        }))

        try:
            user_data = get_user_data(user.id)
            balance = user_data['balance']
            net_worth = balance

            await response.edit(embed=create_embed({
                'title': f'{user}: ${net_worth}',
            }, {
                'Balance': f'${balance}'
            }))
        except Exception as error_message:
            await response.edit(embed=create_embed({
                'title': f'Could not load {user}\'s balance',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message,
            }))

            print('Could not load {user}\'s balance')
            print(error_message)

    @commands.command()
    async def forbes(self, context):
        pass

def setup(client):
    client.add_cog(economy(client))