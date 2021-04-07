STATUS_URL = "http://api.roblox.com/users/USER_ID/onlinestatus/"
USERNAME_URL = "http://api.roblox.com/users/USER_ID"
UPDATE_DELAY = 30

OFFLINE_EMOJI = "🔴"
ONLINE_EMOJI = "🟢"

import discord
from discord.ext import commands, tasks
import pytz
import requests
import time
from datetime import datetime
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://admin:QZnOT86qe3TQ@cluster0.meksl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
subscriptions_data_store = cluster.discord_revamp.subscriptions

def save_subscriptions(data):
    subscriptions_data_store.update_one({"user_id": data["user_id"]}, {"$set": data})
    
def get_subscriptions(user_id: int):
    data = subscriptions_data_store.find_one({"user_id": user_id}) 
    if not data:
        data = {"user_id": user_id}
        subscriptions_data_store.insert_one(data)
    return data

def create_embed(info: {} = {}, fields: {} = {}):
    embed = discord.Embed(
        title = info.get("title") or "",
        description = info.get("description") or "",
        colour = info.get("color") or discord.Color.blue(),
        url = info.get("url") or "",
    )

    for name, value in fields.items():
        embed.add_field(name = name, value = value, inline = info.get("inline") or False)

    if info.get("author"):
        embed.set_author(name = info.author.name, url = info.author.mention, icon_url = info.author.avatar_url)
    if info.get("footer"):
        embed.set_footer(text = info.footer)
    if info.get("image"):
        embed.set_image(url = info.url)
    if info.get("thumbnail"):
        embed.set_thumbnail(url = info.thumbnail)
    
    return embed

class subscriptions(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.roblox_user_status = {}
        self.roblox_loop.start()

    def cog_unload(self):
        self.roblox_loop.cancel()

    def cog_load(self):
        self.roblox_loop.start()

    @tasks.loop(seconds = UPDATE_DELAY)
    async def roblox_loop(self):
        # get all the roblox players that were subscribed to
        roblox_players = {}
        all_subscriptions = list(subscriptions_data_store.find({}))
        for user_data in all_subscriptions:
            for roblox_player_id in user_data["roblox"]:
                if not roblox_players.get(roblox_player_id):
                    roblox_players[roblox_player_id] = [user_data["user_id"]]
                else:
                    roblox_players[roblox_player_id].append(user_data["user_id"])

                if not self.roblox_user_status.get(roblox_player_id):
                    self.roblox_user_status[roblox_player_id] = "offline"

        for roblox_player_id, users_to_notify in roblox_players.items():
            try:
                # get player status
                user_data = requests.get(USERNAME_URL.replace("USER_ID", str(roblox_player_id))).json()
                if not user_data:
                    print(f"ERROR: Could not get roblox user {roblox_player_id}")
                    continue

                status_data = requests.get(STATUS_URL.replace("USER_ID", str(roblox_player_id))).json()
                if not status_data:
                    print(f"ERROR: Could not get roblox user {roblox_player_id}'s status")
                    continue

                # notify subscribed users
                status = status_data["LastLocation"].lower()
                status = status == "playing" and "online" or status == "online" and "online" or "offline"

                if self.roblox_user_status[roblox_player_id] != status:
                    self.roblox_user_status[roblox_player_id] = status

                    for user_to_notify in users_to_notify:
                        user = await self.client.fetch_user(user_to_notify)
                        if status == "online":
                            await user.send("```yaml\n{username} is online ({current_time})\n```".format(
                                username = user_data["Username"],
                                current_time = datetime.now(tz = pytz.timezone("US/Eastern")).strftime("%m/%d/%y at %I:%M %p")
                            ))
                        else:
                            await user.send("```fix\n{username} is offline ({current_time})\n```".format(
                                username = user_data["Username"],
                                current_time = datetime.now(tz = pytz.timezone("US/Eastern")).strftime("%m/%d/%y at %I:%M %p")
                            ))
            except Exception as error_message:
                print(f"ERROR: Something went wrong when checking the roblox user {roblox_player_id}'s status")
                print(error_message)

    @commands.command(description = "Get notified when a certain event occurs.")
    async def subscribe(self, context, event, *, value):
        response = await context.send(embed = create_embed({
            "title": f"Subscribing/unsubscribing to {event}...",
            "color": discord.Color.gold()
        }, {
            "Value": value
        }))

        try:
            if event == "roblox":
                value = int(value)
                if value:
                    # check if roblox user exists
                    user_data = requests.get(USERNAME_URL.replace("USER_ID", str(value))).json()
                    if not user_data:
                        await response.edit(embed = create_embed({
                            "title": f"Could not find the roblox user {value}",
                            "color": discord.Color.red()
                        }))
                        return

                    # save data
                    action = None
                    subscriptions = get_subscriptions(context.author.id)
                    if not subscriptions.get("roblox"):
                        subscriptions["roblox"] = [value]
                        action = "Subscribed"
                    else:
                        if value in subscriptions["roblox"]:
                            subscriptions["roblox"].remove(value)
                            action = "Unsubscribed"
                        else:
                            subscriptions["roblox"].append(value)
                            action = "Subscribed"
                    save_subscriptions(subscriptions)

                    await response.edit(embed = create_embed({
                        "title": f"{action} to {event}",
                        "color": discord.Color.green()
                    }, {
                        "Value": value
                    }))
                else:
                    await response.edit(embed = create_embed({
                        "title": f"{value} is not a valid integer",
                        "color": discord.Color.red()
                    }))
                    return
            else:
                await response.edit(embed = create_embed({
                    "title": f"{event} is not a valid subscription",
                    "color": discord.Color.red()
                }, {
                    "Value": value
                }))
                return
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not subscribe/unsubscribe to {event}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message,
                "Value": value
            }))

    @commands.command(description = "Retrieves a list of subscriptions by the user.")
    async def subscriptions(self, context):
        response = await context.send(embed = create_embed({
            "title": "Loading subscriptions...",
            "color": discord.Color.gold()
        }))

        try:
            subscriptions = get_subscriptions(context.author.id)
            await response.edit(embed = create_embed({
                "title": f"{context.author}'s subscriptions"
            }, subscriptions))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not get {context.author}'s subscriptions",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

def setup(client):
    client.add_cog(subscriptions(client))