import discord
from discord.ext import commands, tasks
import pytz
import requests
import time
from datetime import datetime
import minestat

from helper import create_embed, get_user_data, save_user_data, get_all_user_data
from constants import SUBSCRIPTIONS_STATUS_URL, SUBSCRIPTIONS_USERNAME_URL, SUBSCRIPTIONS_UPDATE_DELAY

class subscriptions(commands.Cog, description = "Subscribe to different events."):
    def __init__(self, client):
        self.client = client
        self.roblox_user_status = {}
        self.roblox_loop.start()

    def cog_unload(self):
        self.roblox_loop.cancel()

    def cog_load(self):
        self.roblox_loop.start()

    @tasks.loop(seconds = SUBSCRIPTIONS_UPDATE_DELAY)
    async def roblox_loop(self):
        await self.client.wait_until_ready()

        # get all the roblox players that were subscribed to
        roblox_players = {}

        all_user_data = get_all_user_data()
        for user_data in all_user_data:
            for roblox_player_id in user_data["subscriptions"]["roblox"]:
                if not roblox_players.get(roblox_player_id):
                    roblox_players[roblox_player_id] = [user_data["user_id"]]
                else:
                    roblox_players[roblox_player_id].append(user_data["user_id"])

                if not self.roblox_user_status.get(roblox_player_id):
                    self.roblox_user_status[roblox_player_id] = "offline"

        for roblox_player_id, users_to_notify in roblox_players.items():
            try:
                # get player status
                user_data = requests.get(SUBSCRIPTIONS_USERNAME_URL.replace("USER_ID", str(roblox_player_id))).json()
                if not user_data:
                    print(f"ERROR: Could not get roblox user {roblox_player_id}")
                    continue

                status_data = requests.get(SUBSCRIPTIONS_STATUS_URL.replace("USER_ID", str(roblox_player_id))).json()
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
                    user_data = requests.get(SUBSCRIPTIONS_USERNAME_URL.replace("USER_ID", str(value))).json()
                    if not user_data:
                        await response.edit(embed = create_embed({
                            "title": f"Could not find the roblox user {value}",
                            "color": discord.Color.red()
                        }))
                        return

                    # save data
                    action = None

                    user_data = get_user_data(context.author.id)
                    if not user_data["subscriptions"].get("roblox"):
                        user_data["subscriptions"]["roblox"] = [value]
                        action = "Subscribed"
                    else:
                        if value in user_data["subscriptions"]["roblox"]:
                            user_data["subscriptions"]["roblox"].remove(value)
                            action = "Unsubscribed"
                        else:
                            user_data["subscriptions"]["roblox"].append(value)
                            action = "Subscribed"
                    save_user_data(user_data)

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
            user_data = get_user_data(context.author.id)
            await response.edit(embed = create_embed({
                "title": f"{context.author}'s subscriptions"
            }, user_data["subscriptions"]))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not get {context.author}'s subscriptions",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

    @commands.command(description = "Gets the status of a subscription.")
    async def status(self, context, name, *, value):
        response = await context.send(embed = create_embed({
            "title": f"Loading status of {name} - {value}",
            "color": discord.Color.gold()
        }))

        try:
            if name == "roblox":
                value = int(value)
                if not value:
                    await response.edit(embed = create_embed({
                        "title": f"`{value}` could not be converted to an integer",
                        "color": discord.Color.red()
                    }))

                user_data = requests.get(SUBSCRIPTIONS_USERNAME_URL.replace("USER_ID", str(value))).json()
                if not user_data:
                    print(f"ERROR: Could not get roblox user {value}")
                    return

                status_data = requests.get(SUBSCRIPTIONS_STATUS_URL.replace("USER_ID", str(value))).json()
                if not status_data:
                    print(f"ERROR: Could not get roblox user {value}'s status")
                    return

                status = status_data["LastLocation"].lower()
                status = status == "playing" and "online" or status == "online" and "online" or "offline"
                username = user_data["Username"]

                await response.edit(embed = create_embed({
                    "title": f"{username} is {status}",
                    "color": discord.Color.gold()
                }))
            else:
                await response.edit(embed = create_embed({
                    "title": f"{name} is not a valid subscription",
                    "color": discord.Color.red()
                }))
        except Exception as error_message:
            await response.edit(embed = create_embed({
                "title": f"Could not load status of {name} - {value}",
                "color": discord.Color.red()
            }, {
                "Error Message": error_message
            }))

def setup(client):
    client.add_cog(subscriptions(client))