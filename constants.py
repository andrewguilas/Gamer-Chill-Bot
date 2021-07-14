EXTENSIONS = [
    'events',
    'bot',
    'default',
    'fun',
    'vc',
    'security',
    'economy',
    'stocks',
]

DEFAULT_GUILD_DATA = {
    'guild_id': None,
    'join_channel': None,
}

DEFAULT_USER_DATA = {
    'user_id': None,
    'balance': 1000,
    'stocks': {},
}

EIGHTBALL_RESPONSES = [
    'It is certain.',
    'It is decidedly so.',
    'Without a doubt.',
    'Yes - definitely.',
    'You may rely on it.',
    'As I see it, yes.',
    'Most likely.',
    'Outlook good.',
    'Yes.',
    'Signs point to yes.',
    'Reply hazy, try again.',
    'Ask again later.',
    'Better not tell you now.',
    'Cannot predict now.',
    'Concentrate and ask again.',
    'Don\'t count on it.',
    'My reply is no.',
    'My sources say no.',
    'Outlook not so good.',
    'Very doubtful.',
    'No.',
    'Your question isn\'t important, but btc to the moon is.',
    'Ask better questions next time.',
]

COMMANDS = {
    'Default': {
        'help': 'Retrieves bot commands.',
        'userinfo <user>': 'Retrieves info of the user.',
        'serverinfo': 'Retrieves server info. Server command only.',
        'messageleaderboard': 'Retrieves the users with the most messages in the server.',
    },
    'Fun': {
        '8ball': 'Retrieves a random response to a question.',
        'roll <number>': 'Retrieves a die of number.',
        'impersonate': 'Impersonates sending a message as a user.',
        'randomperson': 'Retrieves a random user in the server.',
        'm': 'Retrieves a random meme from r/meme. DM command only.',
        'join': 'Makes the bot join your VC.',
        'leave': 'Makes the bot leave your VC.',
        'say <message>': 'Makes the bot say the message. Server command only.',
    },
    'Bot': {
        'load <extension>': 'Loads an extension.',
        'unload <extension>': 'Unloads an extension.',
        'reload <extension>': 'Reloads an extension.',
        'update': 'Reloads all extensions.',
        'run <code>': 'Runs code through the bot.',
        'cls': 'Clears the terminal.',
        'restart': 'Restarts the bot.',
        'info': 'Retrieves the bot\'s ping, invite link, uptime, connected servers, members watching, and users watching.'
    },
    'Economy & Stocks': {
        'bal': 'Retrieves the user\'s balance.',
        'forbes': 'Retrieves the richest members of a server.',
        'buyshares <ticker> <amount>': 'Buys shares of a stock/crypto.',
        'sellshares <ticker> <amount>': 'Sells shares of a stock/crypto',
        'portfolio <user>': 'Retrieves the user\'s portfolio',
    }
}

IS_TESTING = True
MAX_LEADERBOARD_FIELDS = 10
DELETE_RESPONSE_DELAY = 3
MAX_MEMES = 10
MEME_SUBREDDIT = 'memes'
PREFIX = '?'

CHECK_EMOJI = '✅'
NEXT_EMOJI = '▶️'
BACK_EMOJI = '◀️'

TEMP_PATH = '__temp__'
TTS_PATH = '__temp__/tts.mp3'
TEST_DATASTORE = 'datastore6'
PRODUCTION_DATASTORE = 'datastore7'