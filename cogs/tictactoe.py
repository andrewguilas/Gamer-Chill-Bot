NUMBERS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
PLAYER_1_EMOJI = "❎"
PLAYER_2_EMOJI = "🅾️"
JOIN_EMOJI = "➡️"

import discord
from discord.ext import commands
from discord import Color as discord_color

import sys
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
            inline = False
        )

    embed.timestamp = datetime.now(tz = pytz.timezone("US/Eastern"))

    return embed

def create_board(board):
    text = ""
    for index, slot in enumerate(board):
        text = text + slot
        if index == 2 or index == 5:
            text = text + "\n"
    return text

def find_emoji(emoji, list):
    for index, emoji_in_list in enumerate(list):
        if str(emoji) == str(emoji_in_list):
            return index

def get_winner(board):
    """
    0 1 2
    3 4 5️
    6 7 8
    """

    winning_emoji = None

    # rows
    if board[0] == board[1] and board[1] == board[2]:
        winning_emoji = board[0]
    elif board[3] == board[4] and board[4] == board[5]:
        winning_emoji = board[3]
    elif board[6] == board[7] and board[7] == board[8]:
        winning_emoji = board[6]
    # columns
    elif board[0] == board[3] and board[3] == board[6]:
        winning_emoji = board[0]
    elif board[1] == board[4] and board[4] == board[7]:
        winning_emoji = board[1]
    elif board[2] == board[5] and board[5] == board[8]:
        winning_emoji = board[2]
    # diagonal
    elif board[0] == board[4] and board[4] == board[8]:
        winning_emoji = board[0]
    elif board[2] == board[4] and board[4] == board[6]:
        winning_emoji = board[0]

    empty_slots_remaining = 0
    for emoji in board:
        if emoji != PLAYER_1_EMOJI and emoji != PLAYER_2_EMOJI:
            empty_slots_remaining += 1

    if empty_slots_remaining == 0:
        winning_emoji = 3

    return PLAYER_1_EMOJI == winning_emoji and 1 or PLAYER_2_EMOJI == winning_emoji and 2 or winning_emoji

class tictactoe(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def tictactoe(self, context_1):
        player_1 = context_1.author

        # create embed to get player 2

        embed = create_embed("Awaiting for Player 2 to react to join. Times out in 30 seconds.")
        embed.set_footer(text = f"#{context_1.channel}")
        embed.set_author(name = context_1.author, icon_url = context_1.author.avatar_url)
        message_sent = await context_1.send(embed = embed)
        
        # await join reaction for player 2

        player_2 = None
        await message_sent.add_reaction(JOIN_EMOJI)

        def check_join_reaction(reaction, user):
            return not user.bot and user != player_1 and str(reaction.emoji) == JOIN_EMOJI and reaction.message.channel == context_1.channel

        try:
            reaction, player_2 = await self.client.wait_for("reaction_add", check = check_join_reaction, timeout = 30)
        except asyncio.TimeoutError:
            await message_sent.edit(embed = create_embed("Timeout: Another player did not join the game in time", discord_color.orange()))
            return
        
        # start game

        embed = create_embed(f"Starting tic tac toe game with {player_1} and {player_2}", None, {
            "Player 1": player_1.mention,
            "Player 2": player_2.mention
        })
        embed.set_footer(text = f"#{context_1.channel}")
        embed.set_author(name = context_1.author, icon_url = context_1.author.avatar_url)
        await message_sent.edit(embed = embed)

        # create reactions

        current_player = None
        board = NUMBERS.copy()
        winner = None

        await message_sent.clear_reactions()
        for index, slot in enumerate(board):
            await message_sent.add_reaction(NUMBERS[index])

        # make players make move

        while not winner:
            # edit embed

            current_player = current_player == player_1 and player_2 or player_1
            await message_sent.edit(embed = create_embed(f"{current_player}, make your move. Timeout in 30 seconds.\n{create_board(board)}", None, {
                "Player 1": player_1.mention,
                "Player 2": player_2.mention
            }))
            
            # wait for reaction

            chosen_slot = None

            def check_board_reaction(reaction, user):
                return user == current_player and str(reaction.emoji) in board and reaction.message.channel == context_1.channel

            try:
                chosen_slot, user = await self.client.wait_for("reaction_add", check = check_board_reaction, timeout = 30)
            except asyncio.TimeoutError:
                await message_sent.edit(embed = create_embed(f"Timeout: {current_player} did not play a move in time", discord_color.orange()))
                return
                
            # do move

            await message_sent.clear_reaction(chosen_slot.emoji)
            board[find_emoji(chosen_slot, board)] = current_player == player_1 and PLAYER_1_EMOJI or PLAYER_2_EMOJI
            
            # check of winner

            winner = get_winner(board)
            if winner == 1:
                winner = player_1
            elif winner == 2:
                winner = player_2
            elif winner == 3:
                winner = "TIE"

        # update embed

        await message_sent.clear_reactions()
        if winner == "TIE":
            await message_sent.edit(embed = create_embed(f"Tie! You are both trash.\n{create_board(board)}", None, {
                "Player 1": player_1.mention,
                "Player 2": player_2.mention
            }))
        else:
            await message_sent.edit(embed = create_embed(f"{winner} has won!\n{create_board(board)}", None, {
                "Player 1": player_1.mention,
                "Player 2": player_2.mention
            }))

def setup(client):
    client.add_cog(tictactoe(client))