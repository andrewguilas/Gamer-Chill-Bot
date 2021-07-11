import discord
from discord.ext import commands
from helper import create_embed, is_guild_owner

class security(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.whitelisted = []

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if not member.id in self.whitelisted:
            try:
                await member.send(embed=create_embed({
                    'title': 'You are not whitelisted to join the server',
                    'description': 'Contact an administrator to be whitelisted',
                    'color': discord.Color.red()
                }))
            except:
                pass
            
            await member.kick()
        else:
            self.whitelisted.remove(member.id)

    @commands.command()
    @commands.check_any(commands.is_owner(), is_guild_owner(), commands.has_permissions(administrator=True))
    async def whitelist(self, context, user_id):
        response = await context.send(embed=create_embed({
            'title': f'Whitelisting {user_id}',
            'color': discord.Color.gold()
        }))

        try:
            user_id = int(user_id)
            if user_id in self.whitelisted:
                await response.edit(embed=create_embed({
                    'title': f'{user_id} is already whitelisted',
                    'color': discord.Color.red()
                }))
                return
            elif context.guild.get_member(user_id):
                await response.edit(embed=create_embed({
                    'title': f'{user_id} is already in the server',
                    'color': discord.Color.red()
                }))
                return

            self.whitelisted.append(user_id)
            await response.edit(embed=create_embed({
                'title': f'Whitelisted {user_id}',
                'color': discord.Color.green()
            }))
        except ValueError:
            await response.edit(embed=create_embed({
                'title': f'{user_id} is not a number',
                'color': discord.Color.red()
            }))
        except Exception as error_message:
            await response.edit(embed=create_embed({
                'title': f'Could not whitelist {user_id}',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))

            print(f'Could not whitelist {user_id}')
            print(error_message)

def setup(client):
    client.add_cog(security(client))
