PREFIX = "?"
DEFAULT_GUILD_SETTINGS = {"guild_id": None}
DEFAULT_USER_DATA = {"user_id": None}
EXTENSIONS = [
    "events",
    "bot",
    "default",
    "fun",
    "moderation",
    "server",
    "vc",
    "subscriptions",
    "leveling",
    "economy",
    "stocks"
]

ACAS_BLACKLISTED_DAYS = [4, 5, 6]
ACAS_REMINDER_BLOCK_TIMES = ["09:20:00", "10:50:00", "12:35:00", "14:35:00"]
ACAS_BLOCK_TIMES = ["09:25:00", "10:55:00", "12:40:00", "14:40:00"]
ACAS_UPDATE_DELAY = 1

ECONOMY_MAX_FIELDS_FOR_LEADERBOARD_EMBED = 10
ECONOMY_STARTING_MONEY = 1000

VC_LANGUAGE = "en"
VC_ACCENT = "com"
VC_VOICE_IS_SLOW = False

SUBSCRIPTIONS_STATUS_URL = "http://api.roblox.com/users/USER_ID/onlinestatus/"
SUBSCRIPTIONS_USERNAME_URL = "http://api.roblox.com/users/USER_ID"
SUBSCRIPTIONS_UPDATE_DELAY = 60

LEVELING_UPDATE_DELAY = 60
LEVELING_MESSAGE_COOLDOWN = 30
LEVELING_MESSAGE_EXP = 5
LEVELING_VOICE_EXP = 1
LEVELING_LEVEL_DIFFICULTY = 20
LEVELING_MAX_BOXES_FOR_RANK_EMBED = 10
LEVELING_MAX_FIELDS_FOR_LEADERBOARD_EMBED = 10
LEVELING_DEFAULT_EXPERIENCE = 0
LEVELING_MONEY_PER_LEVEL = 50

LEVELING_FILL_EMOJI = "🟦"
LEVELING_UNFILL_EMOJI = "⬜"

STOCKS_PERIOD = "2h"
STOCKS_INTERVAL = "1m"

VERSION_LOGS = {
    "1.0.9": "Made ?forbes list net-worth instead of bank balance.",
    "1.0.8": "Created specific permissions for changing certain settings.",
    "1.0.7": "Merged ACAS with subscriptions. Do `?subscribe acas` to subscribe/unsubscribe from acas. Fixed acas not announcing block 1.",
    "1.0.6": "Added net-worth to ?bal",
    "1.0.5": "Removed minecraft subscription and status because it caused the bot to randomly disconnect and slow down.",
    "1.0.4": "Added money reward for leveling up.",
    "1.0.3": "Fixed ACAS not making announcements.",
    "1.0.2": "Added ?updatelog.",
    "1.0.1": "Added ?status and minecraft server subscriptions.",
    "1.0.0": "Added settings, more portfolio info, and increased performance.",
}
