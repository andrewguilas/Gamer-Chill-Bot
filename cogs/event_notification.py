API_KEY = "kF1RfYWUHZetCMihCy6hx66dC"
API_SECRET_KEY = "IYDTzgiFWOIr0cb5ATRVUjstggA1AIJbw7weJB7MqMOuZ1sXvx"
ACCESS_TOKEN = "1166546759583248386-ikWfGAu9EyMTTppMJPDEjQWylt1c7s"
ACCESS_TOKEN_SECRET = "6NE87Hm1dFgbJ6QEg22AOt70vFtmROCRDXLUuCI3lzpMs"
UPDATE_TIME = 10
TIME_ZONE_DIFFERENCE = 4
DEFAULT_EVENTS_DATA = {
    "id": None,
    "twitter": [],
    "instagram": [],
    "youtube": [],
    "acas": False,
}

# discord
import discord
from discord import Color as discord_color
from discord.ext import commands, tasks

# embed
import pytz
from datetime import datetime

# other
import tweepy
import json
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://admin:QZnOT86qe3TQ@cluster0.meksl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
events_data_store = cluster.discord.events

auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

def convert_string_to_date(string):
    chunks = string.split(" ")

    time = chunks[3]
    day = chunks[2]
    month = chunks[1]
    year = chunks[5]

    string = f"{day} {month} {year} {time}"
    return datetime.strptime(string, "%d %b %Y %H:%M:%S")

def pretty_print(content):
    return json.dumps(content, sort_keys = True, indent = 4)

def create_embed(title, fields: {} = {}, info: {} = {}):
    embed = discord.Embed(
        title = title,
        colour = info.get("color") or discord_color.blue(),
        timestamp = datetime.now(tz = pytz.timezone("US/Eastern"))
    )

    for name, value in fields.items():
        embed.add_field(
            name = name,
            value = value,
            inline = True
        )

    if info.get("member"):
        embed.set_author(name = info["member"], icon_url = info["member"].avatar_url)
    if info.get("author_name"):
        embed.set_author(name = info["author_name"], icon_url = info.get("author_icon"))
    if info.get("thumbnail"):
        embed.set_thumbnail(url = info["thumbnail"])
    if info.get("url"):
        embed.url = info["url"]

    return embed

def save_events_data(data):
    events_data_store.update_one({"id": data["id"]}, {"$set": data})

def insert_events_data(data):
    events_data_store.insert_one(data)

def get_events_data(user_id):
    data = events_data_store.find_one({"id": user_id})
    if not data:
        data = DEFAULT_EVENTS_DATA
        data["id"] = user_id
        insert_events_data(data)
    return data 

class event_notification(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.events = {
            "twitter": {},
        }
        self.check_events.start()

    def cog_unload(self):
        self.check_events.cancel()

    def cog_load(self):
        self.check_events.start()

    @tasks.loop(seconds = UPDATE_TIME)
    async def check_events(self):
        await self.client.wait_until_ready()
        guild = self.client.guilds[0]
        
        subscribed_events = events_data_store.find({})
        # subscribe to all of the members' subscriptions
        for data in subscribed_events:
            for twitter_user_id in data["twitter"]:
                if not self.events["twitter"].get(twitter_user_id):
                    self.events["twitter"][twitter_user_id] = None

        # compare cached tweets to most recent tweets
        for twitter_user_id, recent_tweet_id in self.events["twitter"].items():
            # get most recent tweet
            most_recent_tweet = None
            user_tweets = api.user_timeline(id = id, count = 1, include_rts = False)
            if not user_tweets or not user_tweets[0]:
                most_recent_tweet = None
            else:
                most_recent_tweet = user_tweets[0]._json

            if most_recent_tweet["id"] != recent_tweet_id:
                # check if tweet is old
                created_at_datetime_object = convert_string_to_date(most_recent_tweet["created_at"])
                if created_at_datetime_object.timestamp() - TIME_ZONE_DIFFERENCE * 60 * 60 + UPDATE_TIME < datetime.now(tz = pytz.timezone("GMT")).timestamp():
                    return

                self.events["twitter"][twitter_user_id] = most_recent_tweet["id"]
                # notify all members who subscribed
                subscribed_events = events_data_store.find({})
                for data in subscribed_events:
                    member = guild.get_member(data["id"])
                    if twitter_user_id in data["twitter"]:
                        url = "https://twitter.com/{name}/status/{id}".format(
                            name = most_recent_tweet["user"]["screen_name"],
                            id = most_recent_tweet["id"]
                        )

                        await member.send(embed = create_embed("{}".format(most_recent_tweet["text"]), {
                            "Date": datetime.fromtimestamp(created_at_datetime_object.timestamp() - TIME_ZONE_DIFFERENCE * 60 * 60 + UPDATE_TIME),
                        }, {
                            "author_name": most_recent_tweet["user"]["screen_name"],
                            "author_icon": most_recent_tweet["user"]["profile_image_url_https"],
                            "url": url
                        }))

    @commands.command()
    async def gettweet(self, context, username: str):
        username = username.lower()
        recent_tweet = None
        embed = await context.send(embed = create_embed(f"Retrieving the most recent tweet of {username}", {}, {
            "color": discord_color.gold(),
            "member": context.author,
        }))

        try:
            user_tweets = api.user_timeline(screen_name = username, count = 1, include_rts = False)
            if not user_tweets or not user_tweets[0]:
                return None
            recent_tweet = user_tweets[0]._json
        except Exception as error_message:
            await embed.edit(embed = create_embed(f"ERROR: Could not get {username}'s most recent tweet", {
                "Error Message": error_message,
            }, {
                "color": discord_color.red(),
                "member": context.author,
            }))
        else:
            if not recent_tweet:
                embed = await context.send(embed = create_embed(f"{username} does not have any tweets", {}, {
                    "member": context.author,
                }))
            else:
                created_at_datetime_object = convert_string_to_date(recent_tweet["created_at"])

                url = "https://twitter.com/{name}/status/{id}".format(
                    name = recent_tweet["user"]["screen_name"],
                    id = recent_tweet["id"]
                )
                await embed.edit(embed = create_embed(recent_tweet["text"], {
                    "Date": datetime.fromtimestamp(created_at_datetime_object.timestamp() - TIME_ZONE_DIFFERENCE * 60 * 60),
                }, {
                    "author_name": recent_tweet["user"]["screen_name"],
                    "author_icon": recent_tweet["user"]["profile_image_url_https"],
                    "url": url,
                }))

    @commands.command()
    async def subscribe(self, context, platform: str = "", identifier: str = ""):
        platform = platform.lower()
        identifier = identifier.lower()

        embed = await context.send(embed = create_embed(f"Subscribing to {platform}-{identifier}", {}, {
            "color": discord_color.gold(),
            "member": context.author,
        }))

        if platform == "twitter":
            # get user
            try:
                user = api.get_user(screen_name = identifier)
            except Exception as error_message:
                await embed.edit(embed = create_embed(f"ERROR: Something went wrong when finding @{identifier} on Twitter", {
                    "Error Message": error_message,
                }, {
                    "color": discord_color.red(),
                    "member": context.author,
                }))
                return

            if not user:
                await embed.edit(embed = create_embed(f"ERROR: Could not locate @{identifier} on Twitter", {}, {
                    "color": discord_color.red(),
                    "member": context.author,
                }))
                return
            
            # get data
            subscribed_events = get_events_data(context.author.id)
            was_subscribed = user._json["id"] in subscribed_events["twitter"]

            # save data
            if was_subscribed:
                subscribed_events["twitter"].remove(user._json["id"])
            else:
                subscribed_events["twitter"].append(user._json["id"])
            save_events_data(subscribed_events)

            # send response
            if was_subscribed:
                await embed.edit(embed = create_embed(f"SUCCESS: Unsubscribed from @{identifier} on twitter", {
                    "Description": f"You will NOT be notified when @{identifier} creates a new tweet"
                }, {
                    "color": discord_color.green(),
                    "member": context.author,
                }))
            else:
                await embed.edit(embed = create_embed(f"SUCCESS: Subscribed to @{identifier} on twitter", {
                    "Description": f"You will now be notified when @{identifier} creates a new tweet"
                }, {
                    "color": discord_color.green(),
                    "member": context.author,
                }))
        elif platform == "instagram":
            pass
        elif platform == "youtube":
            pass
        elif platform == "reddit":
            pass
        elif platform == "acas":
            pass
        elif platform == "present_school":
            pass
        elif platform == "preset_stocks":
            pass
        else:
            await embed.edit(embed = create_embed(f"ERROR: The platform `{platform}` is not a valid plaform", {}, {
                "color": discord_color.red(),
                "member": context.author,
            }))

    @commands.command()
    async def subscriptions(self, context):
        subscriptions = {
            "twitter": [],
            "instagram": [],
            "youtube": [],
            "acas": False,
        }

        embed = await context.send(embed = create_embed(f"Getting {context.author}'s subscriptions", {}, {
            "color": discord_color.gold(),
            "member": context.author,
        }))

        subscribed_events = get_events_data(context.author.id)

        # twitter
        for user_id in subscribed_events["twitter"]:
            try:
                user = api.get_user(id = user_id)
                if user:
                    subscriptions["twitter"].append(user.screen_name)
            except:
                continue

        # instagram
        
        # youtube
        
        # reddit
        
        # acas
        
        # present_school
        
        # preset_stocks
        
        await embed.edit(embed = create_embed(f"{context.author}'s subscriptions", subscriptions, {
            "color": discord_color.green(),
            "member": context.author,
        }))

def setup(client):
    client.add_cog(event_notification(client))