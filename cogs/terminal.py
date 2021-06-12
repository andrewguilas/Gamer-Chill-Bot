WEBHOOK_CHANNEL_ID = 853323932551872542

from discord.ext import commands
import shlex

async def say(client, channel_id, message):
    channel = client.get_channel(int(channel_id))
    await channel.send(message)

async def dm(client, user_id, message):
    user = client.get_user(int(user_id))
    await user.send(message)

async def getdm(client, user_id):
    user = client.get_user(int(user_id))
    async for message in user.history(limit=None):
        print(message.content)

class terminal(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.commands = [say, dm, getdm]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != WEBHOOK_CHANNEL_ID:
            return

        arguments = shlex.split(message.content, posix = True)
        for method in self.commands:
            if method.__name__ == arguments[0]:
                await method(self.client, *arguments[1:])
                return

def setup(client):
    client.add_cog(terminal(client))
