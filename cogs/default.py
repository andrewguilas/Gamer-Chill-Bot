import discord
from discord.ext import commands
from helper import create_embed, sort_dictionary, get_first_n_items, wait_for_reaction, get_guild_data, save_guild_data, get_object
from constants import MAX_LEADERBOARD_FIELDS, CHECK_EMOJI, NEXT_EMOJI, BACK_EMOJI, COMMANDS

class default(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def help(self, context):
        response = await context.send(embed=create_embed({
            'title': f'Loading commands...',
            'color': discord.Color.gold()
        }))

        try:
            pages = []
            current_page = 0
            for category, commands in COMMANDS.items():
                pages.append(create_embed({
                    'title': category,
                    'inline': True,
                }, commands))

            await response.edit(embed = pages[current_page])

            while True:
                await response.add_reaction(BACK_EMOJI)
                await response.add_reaction(NEXT_EMOJI)
                reaction, user = await wait_for_reaction(self.client, context, [BACK_EMOJI, NEXT_EMOJI], 60)

                if str(reaction.emoji) == NEXT_EMOJI:
                    if current_page + 1 >= len(pages):
                        current_page = len(pages) - 1
                    else:
                        current_page += 1
                elif str(reaction.emoji) == BACK_EMOJI:
                    if current_page == 0:
                        current_page = 0
                    else:
                        current_page -= 1

                if context.guild:
                    await response.edit(embed = pages[current_page])
                    await response.remove_reaction(reaction.emoji, user)
                else:
                    response = await context.send(embed=pages[current_page])
        except Exception as error_message:
            await response.edit(embed=create_embed({
                'title': 'Could not load commands',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))

            print('ERROR: Could not load commands')
            print(commands)

    @commands.command()
    async def userinfo(self, context, *, user: discord.Member = None):
        if not user:
            user = context.author

        response = await context.send(embed=create_embed({
            'title': f'Loading user info for {user}...',
            'color': discord.Color.gold()
        }))

        try:
            if context.guild:
                await response.edit(embed=create_embed({
                    'title': f'{user}\'s User Info',
                    'thumbnail': user.avatar_url,
                }, {
                    'Account Created': user.created_at.strftime('%m/%d/%y - %I:%M:%S %p'),
                    'Activity': ', '.join(user.activities) or 'None',
                    'Boosted Server': user.premium_since and user.premium_since.strftime('%m/%d/%y - %I:%M:%S %p') or 'No',
                    'Bot': user.bot and 'Yes' or 'No',
                    'Device': user.desktop_status and 'Desktop' or user.web_status and 'Website' or user.mobile_status and 'Mobile' or 'Unknown',
                    'Joined Server': user.joined_at.strftime('%m/%d/%y - %I:%M:%S %p'),
                    'Messages (Server)': len(await user.history(limit=None).flatten()),
                    'Nickname': user.nick,
                    'Pending': user.pending and 'Yes' or 'No',
                    'Roles': ' '.join([role.mention for role in user.roles]),
                    'Status': str(user.status).capitalize(),
                    'User ID': user.id,
                }))
            else:
                await response.edit(embed=create_embed({
                    'title': f'{user}\'s User Info',
                    'thumbnail': user.avatar_url,
                }, {
                    'Account Created': user.created_at.strftime('%m/%d/%y - %I:%M:%S %p'),
                    'Bot': user.bot and 'Yes' or 'No',
                    'User ID': user.id,
                    'Mutual Guilds': len(user.mutual_guilds),
                    'Messages (DM)': len(await user.history(limit=None).flatten()),
                }))
        except Exception as error_message:
            await response.edit(embed=create_embed({
                'title': f'Could not retrieve user info for {user}',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message,
            }))

            print(f'ERROR: Could not retrieve user info for {user}')
            print(error_message)

    @commands.command()
    @commands.guild_only()
    async def serverinfo(self, context):
        guild = context.guild

        response = await context.send(embed=create_embed({
            'title': f'Loading server info for {guild.name}',
            'color': discord.Color.gold()
        }))

        try:
            humans = len(list(filter(lambda u: not u.bot, guild.members)))
            bots = len(list(filter(lambda u: u.bot, guild.members)))
            online = len(list(filter(lambda u: str(u.status) == 'online', guild.members)))
            idle = len(list(filter(lambda u: str(u.status) == 'idle', guild.members)))
            dnd = len(list(filter(lambda u: str(u.status) == 'dnd', guild.members)))
            offline = len(list(filter(lambda u: str(u.status) == 'offline', guild.members)))

            await response.edit(embed=create_embed({
                'title': f'{guild.name} server info',
                'thumbnail': guild.icon_url,
                'inline': True,
            }, {
                'Name': guild.name,
                'ID': guild.id,
                'Server Created': guild.created_at,
                'Owner': guild.owner.mention,
                'Region': guild.region,
                'Invites': len(await guild.invites()),
                'Member Count': guild.member_count,
                'Members': f'😀 {humans} 🤖 {bots}',
                'Ban Count': len(await guild.bans()),
                'Member Statuses': f'🟩 {online} 🟨 {idle} 🟥 {dnd} ⬜ {offline}',
                'Category Count': len(guild.categories),
                'Channel Count': len(guild.channels),
                'Text Channel Count': len(guild.text_channels),
                'Voice Channel Count': len(guild.voice_channels),
                'Emoji Count': len(guild.emojis),
                'Role Count': len(guild.roles)
            }))
        except Exception as error_message:
            await response.edit(embed=create_embed({
                'title': f'Could not retrieve  server info for {guild.name}',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))

            print(f'ERROR: Could not retrieve server info for {guild.name}')
            print(error_message)

    @commands.command()
    async def messageleaderboard(self, context):
        response = await context.send(embed=create_embed({
            'title': 'Loading message leaderboard...',
            'description': f'React with {CHECK_EMOJI} to be pinged when the message leaderboard is done. This process could take several minutes or hours depending on the amount of messages in a server.',
            'color': discord.Color.gold()
        }))
        await response.add_reaction(CHECK_EMOJI)

        try:
            members = {}
            async def get_messages_in_guild(guild):
                for channel in guild.text_channels:
                    messages = await channel.history(limit = None).flatten()
                    for message in messages:
                        author = message.author
                        if not guild.get_member(author.id):
                            continue

                        if not members.get(author.name):
                            members[author.name] = 1
                        else:
                            members[author.name] += 1

            if context.guild:
                await get_messages_in_guild(context.guild)
            else:
                for guild in self.client.guilds:
                    await get_messages_in_guild(guild)

            await response.edit(embed=create_embed({
                'title': f'Loading message leaderboard (sorting leaderboard)...',
                'description': f'React with {CHECK_EMOJI} to be pinged when the message leaderboard is done',
                'color': discord.Color.gold()
            }))

            members = sort_dictionary(members, True)
            members = get_first_n_items(members, MAX_LEADERBOARD_FIELDS)

            await response.edit(embed=create_embed({
                'title': context.guild and 'Message Leaderboard (Current Server)' or 'Message Leaderboard (All Servers)'
            }, members))

            response2 = await response.channel.fetch_message(response.id)
            for reaction in response2.reactions:
                if str(reaction.emoji) == CHECK_EMOJI:
                    users = [] 
                    async for user in reaction.users():
                        if not user.bot:
                            users.append(user.mention)

                    if len(users) > 0:
                        ping = ' '.join(users)
                        await context.send(' '.join(users))
                    break

        except Exception as error_message:
            await response.edit(embed=create_embed({
                'title': 'Could not load message leaderboard',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))

            print('ERROR: Could not load message leaderboard')
            print(error_message)

    @commands.command(aliases=['settings'])
    @commands.guild_only()
    async def viewsettings(self, context):
        response = await context.send(embed=create_embed({
            'title': 'Loading settings...',
            'color': discord.Color.gold()
        }))

        try:
            guild_data = get_guild_data(context.guild.id)
            format_guild_data = {}
            for name, value in guild_data.items():
                if name in ['join_channel']:
                    channel = context.guild.get_channel(value)
                    format_guild_data[name] = channel and channel.mention or 'None'
                elif name in ['meme_channels']:
                    if len(value) == 0:
                        format_guild_data[name] = 'None'
                        continue

                    formatted_channels = []
                    for channel_id in value:
                        channel = context.guild.get_channel(channel_id)
                        if channel_id:
                            formatted_channels.append(channel.mention)
                    format_guild_data[name] = ' '.join(formatted_channels) or 'None'
                    print(formatted_channels)
                    print(format_guild_data[name])

            await response.edit(embed=create_embed({
                'title': 'Settings',
            }, format_guild_data))
        except Exception as error_message:
            await response.edit(embed=create_embed({
                'title': 'Could not load settings',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))

            print('Could not load settings')
            print(error_message)

    @commands.command()
    @commands.guild_only()
    async def set(self, context, name, *, value):
        response = await context.send(embed=create_embed({
            'title': f'Changing {name} to {value}...',
            'color': discord.Color.gold()
        }))

        try:
            guild_data = get_guild_data(context.guild.id)
            if name in ['join_channel']:
                if value == 'none':
                    guild_data[name] = None
                    save_guild_data(guild_data)
                    await response.edit(embed=create_embed({
                        'title': f'Removed {name}',
                    }))
                else:
                    channel = get_object(context.guild.text_channels, value)
                    if channel:
                        guild_data[name] = channel.id
                        save_guild_data(guild_data)
                        await response.edit(embed=create_embed({
                            'title': f'Changed {name} to {channel.name}',
                        }))
                    else:
                        await response.edit(embed=create_embed({
                            'title': f'Could not find channel {value}',
                            'color': discord.Color.red()
                        }))
                        print(f'Could not find channel {value}')
            elif name in ['meme_channels']:
                channel = get_object(context.guild.text_channels, value)
                if not channel:
                    await response.edit(embed=create_embed({
                        'title': f'Could not find channel {value}',
                        'color': discord.Color.red()
                    }))
                    print(f'Could not find channel {value}')
                    return

                if channel.id in guild_data[name]:
                    guild_data[name].remove(channel.id)
                    save_guild_data(guild_data)
                    await response.edit(embed=create_embed({
                        'title': f'Removed channel #{channel.name}',
                        'color': discord.Color.green()
                    }))
                else:
                    guild_data[name].append(channel.id)
                    save_guild_data(guild_data)
                    await response.edit(embed=create_embed({
                        'title': f'Added channel #{channel.name}',
                        'color': discord.Color.green()
                    }))
            else:
                await response.edit(embed=create_embed({
                    'title': f'{name} is an invalid setting',
                    'color': discord.Color.red()
                }))
                print(f'{name} is an invalid setting')
        except Exception as error_message:
            await response.edit(embed=create_embed({
                'title': f'Could not change {name} to {value}',
                'color': discord.Color.red()
            }, {
                'Error Message': error_message
            }))

            print(f'Could not change {name} to {value}')
            print(error_message)

def setup(client):
    client.add_cog(default(client))
