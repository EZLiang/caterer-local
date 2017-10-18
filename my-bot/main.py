import discord
from discord.ext import commands
import json
import asyncio
import re
import requests
from html import unescape
from collections import namedtuple

def get_prefix(bot, message):
    in_lounge = message.guild.id == 357922255553953794
    return '!' if in_lounge else 'ca.'

bot = commands.Bot(command_prefix=get_prefix, description="A 'caterer' bot for the cellular automata community's Discord server")
bot.remove_command('help')

cogs = ['extensions.utils', 'extensions.wiki', 'extensions.ca']

@bot.event
async def on_ready():
    if __name__ == '__main__':
        for cog in cogs:
            bot.load_extension(cog)
    print(f'Discord: {discord.__version__}')
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

bot.run('MzU5MDY3NjM4MjE2Nzg1OTIw.DKBnUw.MJm4R_Zz6hCI3TPLT05wsdn6Mgs')
