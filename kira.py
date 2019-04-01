import os
import sys
import yaml
import datetime
import discord
import logging
import aiohttp
import asyncio
import logging.handlers
from utils import checks
from discord.ext import commands
from discord.ext.commands import AutoShardedBot
import motor.motor_asyncio
CCYAN = '\33[36m'
CYELLOW = '\33[33m'
CPURPLE = '\33[35m'
CBLUE = '\33[34m'
CRED = '\33[31m'
CGREEN = '\33[32m'
CEND = '\33[0m'
win = os.name == "nt"
try:
    client = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017)
    print(CGREEN + 'Loaded main database!' + CEND)
except Exception as e:
    print(f'{CRED}Error in loading database!\n{e}{CEND}')

with open('config.yml') as data:
    config = yaml.load(data, Loader=yaml.FullLoader)
    if not config.get('token'):
        print('TOKEN IS MISSING FROM CONFIG FILE!')
        sys.exit(1)
    if not config.get('prefix'):
        print('PREFIX IS MISSING FROM CONFIG FILE!')
        sys.exit(1)

async def _prefix(bot, msg):
    if not msg.guild:
        return ['k.', 'K.']
    base = [f'<@!{bot.config['botid']}> ', f'<@{bot.config['botid']}> ', bot.config['prefix']]
    try:
        settings = await bot.db.settings.find_one({'guild_id': msg.guild.id})
        if settings['prefix'] is not None:
            base = [f'<@!{bot.config['botid']}> ', f'<@{bot.config['botid']}> ', settings['prefix']]
    except:
        welp = {
            "guild_id": msg.guild.id,
            "prefix" : None,
            "djrole": None,
            "mchnl": False,
            "toggle": False,
            "channelid": None
            }
        await bot.db.settings.insert_one(welp)
    return base

load_modules = (
    'modules.dev',
    'modules.fun',
    'modules.help',
    'modules.info',
    'modules.mod',
    'modules.music',
    'modules.repl',
    'modules.settings',
    'modules.sounds',
    'modules.rndstatus',
    'modules.logs',
    'modules.errorhandler')

starttime = datetime.datetime.now()

logger = logging.getLogger("bot")
logger.setLevel(logging.INFO)
handler = logging.handlers.TimedRotatingFileHandler(filename=f"data/logs/kira.log", encoding="utf-8", when="D",
            interval=1, utc=True, backupCount=10)
handler.setFormatter(logging.Formatter("[%(asctime)s:%(levelname)s:%(name)s] %(message)s"))
logger.addHandler(handler)

class KiraMiki(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(command_prefix=_prefix, description='',
                        pm_help=None, case_insensitive=True)
        self.stats = {}
        self.sniped = []
        self.config = config
        self.db = client['kira']
        self.guild_prefixes = _prefix
        self.logger = logging.getLogger("bot")
        self.add_check(self.check_commands)
        self.session = aiohttp.ClientSession()
        self.uptime = datetime.datetime.utcnow()
        try:
            self.load_extension("jishaku")
            self.logger.info(f"[MODULE LOAD] Loaded Jishaku!")
            print(CGREEN + "Loaded JSK on first try!" + CEND)
        except Exception as e:
            print(CRED + "Failed to load JSK!" + CEND)
            self.logger.info(f"[JSK LOAD ERROR] {e}")
        for module in load_modules:
            try:
                self.load_extension(module)
                self.logger.info(f"[MODULE LOAD] Loaded {module}!")
            except Exception as e:
                print('{}Failed to load extension {}\n{}: {}{}'.format(CRED, module, type(e).__name__, e, CEND))
                self.logger.info('[MODULE LOAD ERROR] {}Failed to load extension {}\n{}: {}{}'.format(CRED, module, type(e).__name__, e, CEND))

    async def clear_screen(self):
        if win:
            os.system("cls")
        else:
            os.system("clear")

    async def on_ready(self):
        await self.clear_screen()
        guilds = len(self.guilds)
        channels = len([c for c in self.get_all_channels()])
        login_time = datetime.datetime.now() - starttime
        login_time = login_time.seconds + login_time.microseconds/1E6
        print(CBLUE + "-----------------------------------------------------------------" + CEND)
        print("{}Login time         :{} {}{} milliseconds{}".format(CCYAN, CEND, CPURPLE, login_time, CEND))
        x = "{}Logged in as       :{} {}{} ({}){}"
        y = x.format(CCYAN, CEND, CPURPLE, str(self.user).encode("ascii", "backslashreplace").decode(), self.user.id, CEND)
        print(y)
        del x, y
        print("{}Connected to       :{} {}{} guilds and {} channels{}".format(CCYAN, CEND, CPURPLE, guilds, channels, CEND))
        self.logger.info("[START UP] Connected to: {} guilds and {} channels".format(guilds, channels))
        print("{}Python version     :{} {}{}.{}.{}{}".format(CCYAN, CEND, CPURPLE, *os.sys.version_info[:3], CEND))
        print("{}Discord.py version :{} {}{}{}".format(CCYAN, CEND, CPURPLE, discord.__version__, CEND))
        print(CBLUE + "-----------------------------------------------------------------" + CEND)

    async def on_resumed(self):
        print('Resumed session...')
        self.logger.info('Resumed session..')

    async def check_commands(self, ctx):
        if not ctx.guild:
            return True
        author = ctx.author
        guild = ctx.guild
        channel = ctx.channel
        logs = await self.db.ignore.find_one({'guild_id': guild.id})
        ban = client['kira_banlist']
        ban = ban.ban_list
        ban = await self.db.banlist.find_one({'kira_id': self.user.id})
        settings = {"guild_id": guild.id, "channels": [], "users": [], "roles": []}
        try:
            if f"{author.id}" in ban:
                await ctx.send("<:tickred:539495579793883176> Seems like you’ve been personally banned by the owner.")
                return False
            if logs:
                if channel.id in logs['channels']:
                    await ctx.send("<:tickred:539495579793883176> This channel is in the ignore list, please use a different channel.", delete_after=10)
                    return False
                elif author.id in logs['users']:
                    await ctx.send("<:tickred:539495579793883176> Your id is in this servers ignore list, please use a different server.", delete_after=10)
                    return False
                elif set(r.id for r in author.roles) & set(logs["roles"]):
                    await ctx.send("<:tickred:539495579793883176> One of your roles is in the ignore list, please use a different server.", delete_after=10)
                    return False
                else:
                    return True
            else:
                await self.db.ignore.insert_one(settings)
                return True
        except Exception as e:
            return True
    
    async def on_command(self, ctx):
        module = ctx.command.cog_name
        cmd_name = ctx.command.name
        if module not in self.stats:
            self.stats[module] = {cmd_name: 1}
        elif cmd_name not in self.stats[module]:
            self.stats[module][cmd_name] = 1
        else:
            self.stats[module][cmd_name] += 1
        self.logger.info(f'[COMMAND] {ctx.author.name}({ctx.author.id}) | {ctx.guild.name}@{ctx.channel.name} | {ctx.message.content}')

    async def is_on_cd(self, ctx):
        """Assign a default CD if the command was defined without one. Raise CommandOnCooldown error if it is on CD."""
        if await self.is_owner(ctx.author) is True:
            return True
        await self.handle_command_cooldown(ctx)
        return True

    async def raise_if_on_cd(self, buckets):
        """Raise a CommandOnCooldown error, only if a command is on cooldown."""
        retry_after = buckets._cooldown.update_rate_limit()
        if retry_after:
            raise commands.errors.CommandOnCooldown(buckets._cooldown, retry_after)

    async def handle_command_cooldown(self, ctx):
        """Assign a default CD if needed. Raise error if the specific command is on CD."""
        buckets = getattr(ctx.command, '_buckets')
        await self.assign_default_cooldown(buckets)
        if ctx.command.is_on_cooldown(ctx):
            await self.raise_if_on_cd(buckets)

    async def assign_default_cooldown(self, buckets):
        """Assigns a default cooldown to a command which was defined without one."""
        if buckets._cooldown is None:
            buckets._cooldown = commands.Cooldown(5, 30.0, commands.BucketType.user)

    async def shutdown(self):
        self.logger.info("[SHUTDOWN] Starting shutdown sequence!")
        for module in load_modules:
            self.unload_extension(module)
            self.logger.info(f"[MODULE UNLOAD] Unloaded {module}!")
        await self.session.close()
        await self.logout()

    def run(self):
        try:
            super().run(self.config['token'], reconnect=True)
        except Exception as e:
            print('{}Failed to login:\n{}{}'.format(CRED, e, CEND))

KiraMiki().run()
