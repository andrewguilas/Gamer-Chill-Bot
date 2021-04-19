import discord
from discord.ext import commands, tasks
import pytz
from datetime import datetime

from constants import ACAS_BLACKLISTED_DAYS, ACAS_REMINDER_BLOCK_TIMES, ACAS_BLOCK_TIMES, ACAS_UPDATE_DELAY
from helper import get_settings, create_embed, get_all_guild_data

class class_alert(commands.Cog, description = "Class alert."):
    def __init__(self, client):
        self.client = client
        self.class_alert.start()

    def cog_unload(self):
        self.class_alert.cancel()

    def cog_load(self):
        self.class_alert.start()

    @tasks.loop(seconds = ACAS_UPDATE_DELAY)
    async def class_alert(self):
        #! check if paused

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
        
        all_guild_settings = get_all_guild_data()
        for guild_settings in all_guild_settings:
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
    @commands.command(aliases = ["toggleacas"], description = "Gives/removes the ACAS role to/from the member.")
    async def acas(self, context):
        member = context.author
        response = await context.send(embed = create_embed({
            "title": "Giving/removing ACAS role...",
            "color": discord.Color.gold(),
        }))

        try:
            guild_data = get_settings(context.guild.id)
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

            if acas_role in member.roles:
                await member.remove_roles(acas_role)
                await response.edit(embed = create_embed({
                    "title": "Removed ACAS role",
                    "color": discord.Color.green()
                }))
            else:
                await member.add_roles(acas_role)
                await response.edit(embed = create_embed({
                    "title": "Gave ACAS role",
                    "color": discord.Color.green()
                }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": "Could not give/remove ACAS role",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

def setup(client):
    client.add_cog(class_alert(client))