import discord
from discord.ext import commands
from helper import create_embed, get_user_data, get_all_user_data, sort_dictionary
from constants import MAX_LEADERBOARD_FIELDS

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
        response = await context.send(embed = create_embed({
            'title': f'Loading Forbes...',
            'color': discord.Color.gold()
        }))

        try:
            richest_list = {}
            for user_data in get_all_user_data('money'):
                user = context.guild and context.guild.get_member(user_data['user_id']) or self.client.get_user(user_data['user_id'])
                if not user or user.bot:
                    continue

                balance = user_data['balance']
                net_worth = balance
                richest_list[user.name] = net_worth

            richest_list = sort_dictionary(richest_list, True)

            fields = {}
            for rank, member_name in enumerate(richest_list):
                net_worth = richest_list.get(member_name)
                fields[f'{rank + 1}. {member_name}'] = f'${net_worth}'
                if rank == MAX_LEADERBOARD_FIELDS - 1:
                    break

            await response.edit(embed = create_embed({
                'title': 'Forbes'
            }, fields))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                'title': 'Could not load Forbes',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))

            print('Could not load Forbes')
            print(error_message)
  
def setup(client):
    client.add_cog(economy(client))