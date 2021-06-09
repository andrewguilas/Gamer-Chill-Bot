import discord
from discord.ext import commands, tasks
import pytz
from datetime import datetime

from helper import create_embed, get_guild_data, get_all_guild_data, get_user_data, save_user_data, get_all_user_data
from constants import ACAS_BLACKLISTED_DAYS, ACAS_REMINDER_BLOCK_TIMES, ACAS_BLOCK_TIMES, ACAS_UPDATE_DELAY

class acas(commands.Cog, description = "Subscribe to different events."):
    def __init__(self, client):
        self.client = client
        self.class_alert.start()

    def cog_unload(self):
        self.class_alert.cancel()

    def cog_load(self):
        self.class_alert.start()

    @tasks.loop(seconds = ACAS_UPDATE_DELAY)
    async def class_alert(self):
        await self.client.wait_until_ready()

        now = datetime.now(tz = pytz.timezone("US/Eastern"))
        current_time = str(now.strftime("%H:%M:%S"))
        status = None
        block_number = None

        if now.today().weekday() in ACAS_BLACKLISTED_DAYS:
            return

        if current_time in ACAS_BLOCK_TIMES:
            status = "now"
            block_number = int(ACAS_BLOCK_TIMES.index(current_time)) + 1
        elif current_time in ACAS_REMINDER_BLOCK_TIMES:
            status = "early"
            block_number = int(ACAS_REMINDER_BLOCK_TIMES.index(current_time)) + 1
        else:
            return
        
        for guild_settings in get_all_guild_data():
            try:
                if not guild_settings.get("acas_enabled"):
                    continue
                
                guild = await self.client.fetch_guild(guild_settings["guild_id"])
                if not guild:
                    continue

                acas_role_id = guild_settings.get("acas_role")
                if not acas_role_id:
                    continue

                acas_role = guild.get_role(acas_role_id)
                if not acas_role:
                    continue

                acas_channel_id = guild_settings.get("acas_channel")
                if not acas_channel_id:
                    continue

                acas_channel = self.client.get_channel(acas_channel_id)
                if not acas_channel:
                    continue

                if status == "now":
                    await acas_channel.send(f"{acas_role.mention} **Block {block_number} is starting now!**")
                elif status == "early":
                    await acas_channel.send(f"{acas_role.mention} Block {block_number} is starting in 5 minutes")
            except discord.Forbidden:
                # testing and production bot uses the same data store
                # testing bot will attempt to view settings of guilds it's not connected to
                print("ERROR: Bot cannot access guild {}".format(guild_settings["guild_id"]))
    
        for user_data in get_all_user_data():
            try:
                user = self.client.get_user(user_data["user_id"])
                if not user or not user_data["acas_subscribed"]:
                    continue

                if status == "now":
                    await user.send(f"**Block {block_number} is starting now!**")
                elif status == "early":
                    await user.send(f"Block {block_number} is starting in 5 minutes")     
            except discord.Forbidden:
                print(f"ERROR: Bot cannot DM {user}")

    @commands.command(aliases = ["acas"])
    async def toggleacas(self, context):
        response = await context.send(embed = create_embed({
            "title": f"Subscribing/unsubscribing to ACAS...",
            "color": discord.Color.gold()
        }))

        try:
            if context.guild:
                guild_data = get_guild_data(context.guild.id)
                
                acas_role_id = guild_data.get("acas_role")
                if not acas_role_id:
                    await response.edit(embed = create_embed({
                        "title": "Cannot find ACAS role",
                        "color": discord.Color.red()
                    }))
                    return

                acas_role = discord.utils.get(context.guild.roles, id = acas_role_id)
                if not acas_role:
                    await response.edit(embed = create_embed({
                        "title": f"Role {acas_role_id} does not exist",
                        "color": discord.Color.red()
                    }))
                    return

                if acas_role in context.author.roles:
                    await context.author.remove_roles(acas_role)
                    await response.edit(embed = create_embed({
                        "title": "Unsubscribed from ACAS (server)",
                        "color": discord.Color.green()
                    }))
                else:
                    await context.author.add_roles(acas_role)
                    await response.edit(embed = create_embed({
                        "title": "Subscribed to ACAS (server)",
                        "color": discord.Color.green()
                    }))
            else:
                user_data = get_user_data(context.author.id)
                if user_data["acas_subscribed"]:
                    user_data["acas_subscribed"] = False
                    save_user_data(user_data)
                    await response.edit(embed = create_embed({
                        "title": "Unsubscribed from ACAS (DM)",
                        "color": discord.Color.green()
                    }))
                else:
                    user_data["acas_subscribed"] = True
                    save_user_data(user_data)
                    await response.edit(embed = create_embed({
                        "title": "Subscribed to ACAS (DM)",
                        "color": discord.Color.green()
                    }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not subscribe/unsubscribe to ACAS",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message,
            }))

def setup(client):
    client.add_cog(acas(client))