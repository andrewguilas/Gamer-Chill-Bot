JOIN_EMOJI = "🟩"
LEFT_EMOJI = "◀️"
RIGHT_EMOJI = "▶️"
OUT_EMOJI = "❌"
ADD_EMOJI = "➕"
NUMBERS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
PLAYER_2_JOIN_TIMEOUT = 30
MOVE_TIMEOUT = 30
SHOW_MOVE_DURATION = 3

import discord
from discord.ext import commands
from discord import Color as discord_color

import asyncio
import pytz
from datetime import datetime

def create_embed(title, color = discord_color.blue(), fields = {}):
    embed = discord.Embed(
        title = title,
        colour = color or discord_color.blue()
    )

    for name, value in fields.items():
        embed.add_field(
            name = name,
            value = value,
            inline = True
        )

    embed.timestamp = datetime.now(tz = pytz.timezone("US/Eastern"))

    return embed

def visualize_hand(hand):
    if not hand:
        return OUT_EMOJI
    return NUMBERS[hand - 1]

def get_number_from_emoji(emoji):
    for index, number_emoji in enumerate(NUMBERS):
        if number_emoji == emoji:
            return index

def check_loser(hands):
    return not hands[0] and not hands[1]

class sticks(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def sticks(self, context):
        # get second player

        player_1 = context.author
        embed = await context.send(embed = create_embed("Sticks", discord_color.gold(), {
            "Status": "Awaiting player 2. React to join. Timeout in 30 seconds.",
            "Player 1": player_1.mention,
            "Player 2": "None"
        }))

        await embed.add_reaction(JOIN_EMOJI)

        def player_2_check(reaction, user):
            return reaction.emoji == JOIN_EMOJI and user != player_1 and reaction.message.channel == context.channel and not user.bot
        
        try:
            reaction, player_2 = await self.client.wait_for("reaction_add", check = player_2_check, timeout = PLAYER_2_JOIN_TIMEOUT)
        except asyncio.TimeoutError:
            await embed.edit(embed = create_embed("Sticks", discord_color.gold(), {
                "Status": "Player 2 did not join in time."
            }))
            return
        else:
            await embed.edit(embed = create_embed("Sticks", discord_color.gold(), {
                "Status": "Setting up game",
                "Player 1": player_1.mention,
                "Player 2": player_2.mention
            }))

        # setup game

        player_1_hand = [1, 1]
        player_2_hand = [1, 1]

        current_player = player_1
        current_player_hand = player_1_hand
        enemy_player = player_2
        enemy_player_hand = player_2_hand

        # start game

        while True:
            # get hand to attack

            chosen_attack_hand = None

            await embed.clear_reactions()

            if current_player_hand[0]:
                await embed.add_reaction(LEFT_EMOJI)

            if current_player_hand[1]:
                await embed.add_reaction(RIGHT_EMOJI)

            await embed.edit(embed = create_embed("Sticks", discord_color.gold(), {
                "Status": f"{current_player.mention}, choose one of your hands to attack. Timeout in 30 seconds.",
                f"{current_player.name}'s hand": visualize_hand(current_player_hand[0]) + visualize_hand(current_player_hand[1]),
                f"{enemy_player.name}'s hand": visualize_hand(enemy_player_hand[0]) + visualize_hand(enemy_player_hand[1])
            }))

            def check_attack_hand_move(reaction, user):
                if user == current_player and reaction.message == embed:
                    return reaction.emoji == LEFT_EMOJI or reaction.emoji == RIGHT_EMOJI
            
            try:
                chosen_attack_hand, user = await self.client.wait_for("reaction_add", check = check_attack_hand_move, timeout = MOVE_TIMEOUT)
            except asyncio.TimeoutError:
                await embed.edit(embed = create_embed("Sticks", discord_color.gold(), {
                    "Status": f"{current_player.mention} did not make their move in time."
                }))
                return
            else:
                chosen_attack_hand = chosen_attack_hand.emoji

            # get enemy hand to attack

            chosen_enemy_hand = None

            await embed.clear_reactions()

            if enemy_player_hand[0]:
                await embed.add_reaction(LEFT_EMOJI)

            if enemy_player_hand[1]:
                await embed.add_reaction(RIGHT_EMOJI)

            await embed.edit(embed = create_embed("Sticks", discord_color.gold(), {
                "Status": f"{current_player.mention}, choose one of the enemy's hands to attack. Timeout in 30 seconds.",
                f"{current_player.name}'s hand": visualize_hand(current_player_hand[0]) + visualize_hand(current_player_hand[1]),
                f"{enemy_player.name}'s hand": visualize_hand(enemy_player_hand[0]) + visualize_hand(enemy_player_hand[1])
            }))

            def check_enemy_hand_move(reaction, user):
                if user == current_player and reaction.message == embed:
                    return reaction.emoji == LEFT_EMOJI or reaction.emoji == RIGHT_EMOJI
            
            try:
                chosen_enemy_hand, user = await self.client.wait_for("reaction_add", check = check_enemy_hand_move, timeout = MOVE_TIMEOUT)
            except asyncio.TimeoutError:
                await embed.edit(embed = create_embed("Sticks", discord_color.gold(), {
                    "Status": f"{current_player.mention} did not make their move in time."
                }))
                return
            else:
                chosen_enemy_hand = chosen_enemy_hand.emoji

            # play move

            hand_to_attack = None
            if chosen_enemy_hand == LEFT_EMOJI:
                hand_to_attack = 0
            else:
                hand_to_attack = 1

            number_to_add = None
            if chosen_attack_hand == LEFT_EMOJI:
                number_to_add = current_player_hand[0]
            else:
                number_to_add = current_player_hand[1]

            print(chosen_enemy_hand == LEFT_EMOJI)
            print(f"Attacking: {chosen_enemy_hand} {hand_to_attack}")
            if enemy_player_hand[hand_to_attack] + number_to_add >= 5:
                enemy_player_hand[hand_to_attack] = None
            else:
                enemy_player_hand[hand_to_attack] += number_to_add

            # check winner

            if check_loser(enemy_player_hand):
                break

            # ready next move

            current_player, enemy_player = enemy_player, current_player
            current_player_hand, enemy_player_hand = enemy_player_hand, current_player_hand

        await embed.clear_reactions()
        await embed.edit(embed = create_embed("Sticks", discord_color.gold(), {
            "Status": f"{current_player.mention} has won!",
            f"Winner: {current_player.name}": visualize_hand(current_player_hand[0]) + visualize_hand(current_player_hand[1]),
            f"Loser: {enemy_player.name}": visualize_hand(enemy_player_hand[0]) + visualize_hand(enemy_player_hand[1])
        }))

def setup(client):
    client.add_cog(sticks(client))