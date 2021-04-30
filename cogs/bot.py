import discord
from discord.ext import commands
import os
import sys
import time

from helper import create_embed, get_guild_data, save_guild_data, get_object, is_guild_owner, format_time, get_first_n_items
from constants import VERSION_LOGS, VC_LANGUAGES, VC_ACCENTS, MAX_LEADERBOARD_FIELDS

class bot(commands.Cog, description = "Bot management and settings."):
    def __init__(self, client):
        self.client = client
        self.uptime = time.time()

    @commands.command(description = "Runs code through the bot.", brief = "server owner")
    @commands.check_any(commands.is_owner(), is_guild_owner())
    async def run(self, context, *, code):
        response = await context.send(embed = create_embed({
            "title": "Running code...",
            "color": discord.Color.gold(),
        }, {
            "Code": code,
        }))

        try:
            exec(code)
            await response.edit(embed = create_embed({
                "title": "Ran code",
                "color": discord.Color.green(),
            }, {
                "Code": code,
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not run code",
                "color": discord.Color.red(),
            }, {
                "Error Message": error_message,
                "Code": code,
            }))

    @commands.command(description = "Clears the terminal's logs.", brief = "bot creator")
    @commands.check_any(commands.is_owner())
    async def cls(self, context):
        response = await context.send(embed = create_embed({
            "title": "Clearing terminal",
            "color": discord.Color.gold(),
        }))

        try:
            os.system("cls" if os.name == "nt" else "clear")
            await response.edit(embed = create_embed({
                "title": "Terminal cleared",
                "color": discord.Color.green(),
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not clear terminal",
                "color": discord.Color.red(),
            }, {
                "Error Message": error_message,
            }))
    
    @commands.command(description = "Changes the bot's activity in its profile.", brief = "server owner")
    @commands.check_any(commands.is_owner(), is_guild_owner())
    async def changeactivity(self, context, *, activity = None):
        response = await context.send(embed = create_embed({
            "title": f"Changing the bot's activity to {activity}",
            "color": discord.Color.gold(),
        }))

        try:
            await self.client.change_presence(activity = discord.Game(name = activity or ""))
            await response.edit(embed = create_embed({
                "title": f"Changed bot's activity to {activity}",
                "color": discord.Color.green(),
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not change the bot's activity to {activity}",
                "color": discord.Color.red(),
            }, {
                "Error Message": error_message,
            }))

    @commands.command(description = "Changes the bot's status in its profile. Possible statuses are online, offline, dnd, and idle.", brief = "server owner")
    @commands.check_any(commands.is_owner(), is_guild_owner())
    async def changestatus(self, context, *, status: str = "online"):
        response = await context.send(embed = create_embed({
            "title": f"Changing the bot's status to {status}",
            "color": discord.Color.gold(),
        }))

        try:
            await self.client.change_presence(status = discord.Status[status])
            await response.edit(embed = create_embed({
                "title": f"Changed bot's status to {status}",
                "color": discord.Color.green(),
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not change the bot's status to {status}",
                "color": discord.Color.red(),
            }, {
                "Error Message": error_message,
            }))

    @commands.command(description = "Restarts the bot if it is being hosted on a server. Stops the bot if it is being hosted locally.", brief = "server owner")
    @commands.check_any(commands.is_owner(), is_guild_owner())
    async def restart(self, context):
        await context.send(embed = create_embed({
            "title": "Restarting bot, no confirmation message after completion...",
            "color": discord.Color.gold(),
        }))

        sys.exit()

    @commands.command(description = "Retrieves the Python and discord.py version the bot is running on.")
    async def version(self, context):
        response = await context.send(embed = create_embed({
            "title": "Loading version...",
            "color": discord.Color.gold()
        }))

        try:
            python_version = sys.version_info
            python_version_text = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
            discordpy_version_text = discord.__version__

            await response.edit(embed = create_embed({
                "title": "Bot Version",
            }, {
                "Python": python_version_text,
                "discord.py": discordpy_version_text
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not get version",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command(description = "Retrieves the bot's uptime, connected servers, members watching and users watching.")
    async def botinfo(self, context):
        response = await context.send(embed = create_embed({
            "title": "Loading bot info...",
            "color": discord.Color.gold()
        }))

        try:
            uptime = round(time.time() - self.uptime)
            uptime_text = format_time(uptime)

            connected_servers = 0
            members_watching = 0
            user_ids = []

            for guild in self.client.guilds:
                connected_servers += 1
                for member in guild.members:
                    members_watching += 1
                    if not member.id in user_ids:
                        user_ids.append(member.id)

            users_watching = len(user_ids)

            await response.edit(embed = create_embed({
                "title": "Bot Info",
            }, {
                "Uptime": uptime_text,
                "Connected Servers": connected_servers,
                "Members Watching": members_watching,
                "Users Watching": users_watching
            }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not load bot info",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command()
    async def updatelog(self, context, page: int = 1):
        response = await context.send(embed = create_embed({
            "title": f"Loading update log...",
            "color": discord.Color.gold()
        }))

        try:
            first_page = page * MAX_LEADERBOARD_FIELDS - MAX_LEADERBOARD_FIELDS
            last_page = page * MAX_LEADERBOARD_FIELDS

            fields = {}
            for key, version in enumerate(list(VERSION_LOGS.keys())):
                if key >= first_page and key < last_page:
                    fields[version] = VERSION_LOGS[version]

            await response.edit(embed = create_embed({
                "title": "Update Log",
                "footer": f"Page {page}"
            }, fields))
        except Exception as error_message:
            create_embed({
                "title": f"Could not load update log",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            })

def setup(client):
    client.add_cog(bot(client))