import os
import subprocess
import zipfile
from datetime import datetime
import re

import discord
from discord.ext import commands

from cogs.meta import DOWNLOAD_LINK


def get_prefix(bot, message):
    try:
        return ['ca.'] + (
            [('!', ';')[bot.user.id == 376485072561504257]] if message.guild.id == 357922255553953794 else [])
    except AttributeError:  # if in DMs, message.guild is None and therefore has no attribute 'id'
        return '!'  # TODO: override commands.Bot.get_prefix to allow this to be ''


class Context(commands.Context):
    async def update(self):
        self.message = await self.fetch_message(self.message.id)

    async def upd_rxns(self):
        await self.update()
        return self.message.reactions

    async def thumbsup(self, user=None, text='Success!', ping=False, *, channel=None, override=True):
        try:
            if not override and any(rxn.emoji in '👍👎' for rxn in await self.upd_rxns() if rxn.me):
                return
            await self.message.add_reaction('👍')
            if user is not None and ping:
                await (self if channel is None else channel).send(f'{user.mention}: {text}')
        except discord.NotFound:
            pass

    async def thumbsdown(self, user=None, text='Failure.', ping=False, *, channel=None, override=True):
        try:
            if not override and any(rxn.emoji in '👍👎' for rxn in await self.upd_rxns() if rxn.me):
                return
            await self.message.add_reaction('👎')
            if user is not None and ping:
                await (self if channel is None else channel).send(f'{user.mention}: {text}')
        except discord.NotFound:
            pass

    async def invoke(self, *args, **kwargs):
        return await super().invoke(*args, **kwargs, __invoking=True)


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        self.first_time = True
        self.owner = None
        self.assets_chn = None
        super().__init__(*args, **kwargs)

    async def on_message(self, message):
        await self.invoke(await self.custom_context(message))

    async def custom_context(self, message):
        return await self.get_context(message, cls=Context)


bot = Bot(
    command_prefix=get_prefix,
    description='A cellular automata bot for Conwaylife.com',
    help_command=None
)


@bot.check
def ignore_bots(ctx):
    return not ctx.author.bot

@bot.check
async def ignore_dms(ctx):
    return ctx.guild is not None

@bot.event
async def on_member_join(member):
    if re.match(".+ twitter\\.com/h0nde.*(?i)", member.name):
        await member.ban()

@bot.event
async def on_ready():
    caviewer_path = os.path.dirname(os.path.abspath(__file__)) + "/cogs/resources/bin/CAViewer"

    if not os.path.exists(caviewer_path):  # Checking if CAViewer exists
        print("Downloading CAViewer...")
        p = subprocess.Popen(f"wget {DOWNLOAD_LINK}",
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        p.communicate()

        print("Unzipping...")
        with zipfile.ZipFile("CAViewer-Linux.zip", "r") as z:
            z.extractall(caviewer_path.replace("/bin/CAViewer", ""))

        print("Download complete!")

        os.chmod(caviewer_path, 0o755)
        os.remove("CAViewer-Linux.zip")

    if bot.first_time:
        #### DEV STUFF
        import ssl
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        ####
        bot.assets_chn = bot.get_channel(424383992666783754)
        bot.owner = (await bot.application_info()).owner
        for cog in ('meta', 'wiki', 'ca', 'admin', 'db'):
            try:
                bot.load_extension(f'cogs.{cog}')
            except Exception:
                raise
        bot.help_padding = 1 + max(len(i.name) for i in bot.commands)
        bot.sorted_commands = sorted(bot.commands, key=lambda x: x.name)
        print(f'Logged in as\n{bot.user.name}\n{bot.user.id}')
        print('Guilds:', len(bot.guilds))
        print('------')
        bot.first_time = False


bot.run(os.getenv('DISCORD_TOKEN'))
