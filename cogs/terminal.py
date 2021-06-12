WEBHOOK_CHANNEL_ID = 853323932551872542

from discord.ext import commands
import shlex

async def say(client, channel_id, message):
    channel = client.get_channel(int(channel_id))
    await channel.send(message)

class terminal(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.commands = [say]

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
