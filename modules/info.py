import time
import discord
import humanize
import psutil
import asyncio
import aiohttp
import datetime
import os
import base64
import math
import platform
import speedtest
import subprocess
import struct
import sys
import codecs
import pathlib
from discord.ext import commands
from utils import default, checks
from asyncio.subprocess import PIPE

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_bot_uptime(self, *, brief=False):
        now = datetime.datetime.utcnow()
        delta = now - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        if not brief:
            fmt = 'I\'ve been online for {d} days, {h} hours, {m} minutes, and {s} seconds!'
        else:
            fmt = '{d}d {h}h {m}m {s}s'
        return fmt.format(d=days, h=hours, m=minutes, s=seconds)

    def _get_playing(self):
        return len([p for p in self.bot.lavalink.players._players.values() if p.is_playing])

    @commands.command()
    async def activity(self, ctx, user : discord.Member=None):
        """Information on a user activity."""
        if user is None:
            user = ctx.author
        try:
            act = user.activity
            if act.name == "Visual Studio Code":
                details = act.details
                state = act.state
                e = discord.Embed()
                e.colour = user.colour
                e.set_author(name=f"{user.display_name}'s Activity Status:", icon_url=user.avatar_url)
                e.description = f"__**Currently on {act.name}**__\n\n"
                e.description += f"{details}\n"
                e.description += f"{state}\n"
                e.set_thumbnail(url=act.large_image_url)
                await ctx.send(embed=e)
                return
            if act.name == 'Spotify':
                e = discord.Embed()
                e.colour = act.color
                e.set_author(name=f"{user.display_name}'s Activity Status:", icon_url=user.avatar_url)
                e.description = f"__**Currently on {act}**__\n\n"
                e.description += f"Listening to: {act.title}\n"
                e.description += f"By: {act.artist}\n"
                e.description += f"On: {act.album}\n"
                e.set_thumbnail(url=act.album_cover_url)
                await ctx.send(embed=e)
                return
            if act.name == 'JetBrains IDE':
                try:
                    e = discord.Embed()
                    e.set_author(name=f"{user.display_name}'s Activity Status:", icon_url=user.avatar_url)
                    e.colour = user.colour
                    e.description = f"__**Currently on {act.name}**__\n\n"
                    e.description += f"{act.details}\n"
                    e.description += f"{act.state}\n"
                    e.set_thumbnail(url=act.large_image_url)
                    await ctx.send(embed=e)
                    return
                except Exception as e:
                    await ctx.send(e)
            if act.type == discord.ActivityType.streaming:
                e = discord.Embed()
                e.colour = user.colour
                e.set_author(name=f"{user.display_name}'s Activity Status:", icon_url=user.avatar_url)
                e.description = f"__**Currently Streaming {act.name}**__\n\n"
                e.description += f"Twitch Name: {act.twitch_name}\n"
                e.description += f"Link: {act.url}"
                e.set_thumbnail(url="https://i.imgur.com/4c0OOXY.png")
                await ctx.send(embed=e)
                return
            else:
                e = discord.Embed()
                e.colour = user.colour
                e.set_author(name=f"{user.display_name}'s Activity Status:", icon_url=user.avatar_url)
                e.description = f"__**Currently on:**__\n\n"
                e.description += f" {act.name}\n"
                try:
                    e.description += f"{act.details}\n"
                except:
                    pass
                try:
                    e.description += f"{act.state}\n"
                except:
                    pass
                try:
                    e.set_thumbnail(url=act.large_image_url)
                except:
                    pass
                await ctx.send(embed=e)
                return
        except:
            await ctx.send("Uh oh, looks like there is no information to show.")
            return

    @commands.command()
    async def network(self, ctx, *, args=None):
        """Network"""
        if not args:
            proc = await asyncio.create_subprocess_shell("vnstati -s -i ens3  -o vnstati.png", stdin=None, stderr=None, stdout=PIPE)
            out = await proc.stdout.read()
            await ctx.send(file=discord.File('vnstati.png'))
        elif args == "hourly":
            proc = await asyncio.create_subprocess_shell("vnstati -h -i ens3 -o vnstati.png", stdin=None, stderr=None, stdout=PIPE)
            out = await proc.stdout.read()
            await ctx.send(file=discord.File('vnstati.png'))
        elif args == "monthly":
            proc = await asyncio.create_subprocess_shell("vnstati -m -i ens3 -o vnstati.png", stdin=None, stderr=None, stdout=PIPE)
            out = await proc.stdout.read()
            await ctx.send(file=discord.File('vnstati.png'))

    @commands.command()
    @commands.bot_has_permissions(embed_links=True)
    async def globalui(self, ctx, user_id : int):
        """Shows information on a users id."""
        try:
            a = ctx.bot.get_user(id=user_id)
            if a:
                user = a.id
                seen = len(set([member.guild.name for member in ctx.bot.get_all_members() if member.id== user]))
                sharedservers = str(set([member.guild.name for member in ctx.bot.get_all_members() if member.id == user]))
                for shared in sharedservers:
                    shared = "".strip("'").join(sharedservers).strip("'")
                    shared = shared.strip("{").strip("}")
                data = "{}\n".format(shared)
                e = discord.Embed(colour=ctx.author.colour)
                e.title = "Global Userinfo:"
                e.add_field(name="Username:", value=a.name)
                e.add_field(name="Discriminator:", value=a.discriminator)
                e.add_field(name="Bot:", value=a.bot)
                e.add_field(name="Nitro:", value=a.is_avatar_animated())
                e.add_field(name="Shared Guilds:", value=seen)
                e.add_field(name="Joined Discord:", value=a.created_at)
                e.add_field(name="Shared Guilds List:", value=data)
                e.set_thumbnail(url=a.avatar_url)
                await ctx.send(embed=e)
            else:
                await ctx.send("User was not found.")
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    async def musicstats(self, ctx):
        """Shows how many servers the bot is playing in."""
        server_num = self._get_playing()
        server_ids = self.bot.lavalink.players._players
        server_list = []
        number = 0
        users = 0
        await ctx.trigger_typing()
        for _id, p in server_ids.items():
            try:
                if p.is_playing:
                    number += 1
                    g = self.bot.get_guild(_id)
                    users += len(g.me.voice.channel.members)
                    try:
                        server_list.append(f"**{number})** {g.name}: **{p.current.title}**")
                    except:
                        server_list.append(f"**{number})** {g.name}: **{p.current['info']['title']}**")
            except AttributeError:
                pass
        if server_list == []:
            servers = 'Not connected anywhere.'
        else:
            servers = "\n".join(server_list)
        e = discord.Embed()
        e.colour = 0x36393E
        e.add_field(name="Players:", value=f"Playing in {len(server_list)} servers..")
        e.add_field(name="Users:", value=f"{users-len(server_list)} users listening..")
        e.add_field(name="Guilds:", value=servers, inline=False)
        e.set_footer(text=f"There is currently {len(server_ids)} players created in total.")
        try:
            await ctx.send(embed=e)
            return
        except:
            e = discord.Embed(colour=0x36393E)
            e.description = f"**Well aren't we just popular? I can't display all the servers. But I am currently playing in {server_num} servers.**"
            await ctx.send(embed=e)
            return

    @commands.command()
    async def ping(self, ctx):
        """ Pong! """
        pings = []
        number = 0
        typings = time.monotonic()
        await ctx.trigger_typing()
        typinge = time.monotonic()
        typingms = round((typinge - typings) * 1000)
        pings.append(typingms)
        latencyms = round(self.bot.latency * 1000)
        pings.append(latencyms)
        discords = time.monotonic()
        url = "https://discordapp.com/"
        async with self.bot.session.get(url) as resp:
            if resp.status is 200:
                discorde = time.monotonic()
                discordms = round((discorde-discords)*1000)
                pings.append(discordms)
                discordms = f"{discordms}ms"
            else:
                discordms = "Failed"
        for ms in pings:
            number += ms
        average = round(number / len(pings))
        await ctx.send(f"__**Ping Times:**__\nTyping: `{typingms}ms`  |  Latency: `{latencyms}ms`\nDiscord: `{discordms}`  |  Average: `{average}ms`")

    @commands.command()
    async def invite(self, ctx):
        """Invite Kira."""
        try:
            await ctx.author.send("Here is my invite link:\n<https://discordapp.com/oauth2/authorize?client_id=538344287843123205&scope=bot&permissions=267779137>")
            await ctx.send("I sent my invite link in your dms!", delete_after=5)
        except:
            await ctx.send("Here is my invite link:\n<https://discordapp.com/oauth2/authorize?client_id=538344287843123205&scope=bot&permissions=267779137>", delete_after=10)

    @commands.command()
    async def support(self, ctx):
        """Send support server in dms, unless you have dm's blocked."""
        try:
            await ctx.author.send("Need help? No problem, join here!\nhttps://discord.gg/dbUFDg7")
            await ctx.send("I sent the support server in dms!", delete_after=5)
        except:
            await ctx.author.send("Need help? No problem, join here!\nhttps://discord.gg/dbUFDg7", delete_after=10)

    @commands.command()
    async def commits(self, ctx):
        """Shows last 5 github commits."""
        cmd = r'git show -s HEAD~5..HEAD --format="[{}](https://github.com/JonnyBoy2000/Kira-Miki/commit/%H) %s (%cr)"'
        if os.name == 'posix':
            cmd = cmd.format(r'\`%h\`')
        else:
            cmd = cmd.format(r'`%h`')
        try:
            revision = os.popen(cmd).read().strip()
        except OSError:
            revision = 'Could not fetch due to memory error. Sorry.'
        e = discord.Embed()
        e.colour = 0x36393E
        e.description = revision
        e.set_author(icon_url=self.bot.user.avatar_url, name="Latest Github Changes:")
        e.set_thumbnail(url="https://avatars2.githubusercontent.com/u/22266893?s=400&u=9df85f1c8eb95b889fdd643f04a3144323c38b66&v=4")
        await ctx.send(embed=e)


    @commands.command(aliases=['lls'])
    async def stats(self, ctx):
        """Posts bot stats."""
        oe = "<:wonline:544126607443492895>"
        ie = "<:widle:544126607669854219>"
        de = "<:wdnd:544126607485304843>"
        ge = "<:woffline:544126607711797253>"
        cmd = r'git show -s HEAD~3..HEAD --format="[{}](https://github.com/JonnyBoy2000/Kira-Miki/commit/%H) %s (%cr)"'
        if os.name == 'posix':
            cmd = cmd.format(r'\`%h\`')
        else:
            cmd = cmd.format(r'`%h`')
        try:
            revision = os.popen(cmd).read().strip()
        except OSError:
            revision = 'Could not fetch due to memory error. Sorry.'
        currentOS     = platform.platform()
        cpuUsage      = psutil.cpu_percent(interval=1)
        cpuThred      = os.cpu_count()
        pythonMajor   = sys.version_info.major
        pythonMinor   = sys.version_info.minor
        pythonMicro   = sys.version_info.micro
        pythonRelease = sys.version_info.releaselevel
        pyBit         = struct.calcsize("P") * 8
        threadString = 'thread'
        if not cpuThred == 1:
            threadString += 's'
        memStats      = psutil.virtual_memory()
        memUsed       = memStats.used
        memTotal      = memStats.total
        processor     = platform.processor()
        memUsedGB     = "{0:.1f}".format(((memUsed / 1024) / 1024) / 1024)
        memTotalGB    = "{0:.1f}".format(((memTotal/1024)/1024)/1024)
        memPerc       = str(((memTotal/1024)/1024)/1024 / ((memUsed / 1024) / 1024) / 1024).split('.')[0]
        process       = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'], shell=False, stdout=subprocess.PIPE)
        git_head_hash = process.communicate()[0].strip()
        dev = f"**Name:** {self.bot.get_user(170619078401196032)}\n**ID:** {self.bot.get_user(170619078401196032).id}"
        online = len([e.name for e in self.bot.get_all_members() if e.status == discord.Status.online])
        idle = len([e.name for e in self.bot.get_all_members() if e.status == discord.Status.idle])
        dnd = len([e.name for e in self.bot.get_all_members() if e.status == discord.Status.dnd])
        offline = len([e.name for e in self.bot.get_all_members() if e.status == discord.Status.offline])
        used = humanize.naturalsize(self.bot.lavalink.stats.memory.used)
        free = humanize.naturalsize(self.bot.lavalink.stats.memory.free)
        memory = f"**Used:** {used}\n"
        memory += f"**Free:** {free}\n"
        cpu = f"**Cores:** {self.bot.lavalink.stats.cpu.cores}\n"
        cpu += '**Cpu:** {}% of {} ({} {})\n'.format(cpuUsage, processor, cpuThred, threadString)
        cpu += '**Ram:** {} ({}%) of {}GB used\n'.format(memUsedGB, memPerc, memTotalGB)
        lava = f"**Launched:** {humanize.naturaltime(datetime.datetime.utcnow() - datetime.timedelta(milliseconds=self.bot.lavalink.stats.uptime))}\n"
        lava += f"**Kira Players:** `{len(self.bot.lavalink.players._players)}` players are distributed.\n"
        lava += f"**Lavalink Cpu Load:** {round(self.bot.lavalink.stats.cpu.lavalink_load * 100)}%\n"
        basic = '**OS:** {}\n'.format(currentOS)
        basic += '**Hostname:** {}\n'.format(platform.node())
        basic += '**Language:** Python {}.{}.{} {} ({} bit)\n'.format(pythonMajor, pythonMinor, pythonMicro, pythonRelease, pyBit)
        basic += '**Commit:** {}\n'.format(git_head_hash.decode("utf-8"))
        basic += f"**Bot Uptime:** {self.get_bot_uptime(brief=True)}"
        members = f"{oe} {online}   | "
        members += f"{ie} {idle}\n"
        members += f"{de} {dnd}   | "
        members += f"{ge} {offline}"
        guilds = len(self.bot.guilds)
        e = discord.Embed()
        e.colour = 0x36393E
        e.set_thumbnail(url=self.bot.user.avatar_url)
        e.add_field(name="Basic:", value=basic)
        e.add_field(name="Dev:", value=dev)
        e.add_field(name="Guilds:", value=guilds)
        e.add_field(name="Members:", value=members)
        e.add_field(name="Lavalink:", value=lava)
        e.add_field(name="Memory:", value=memory)
        e.add_field(name="CPU | RAM:", value=cpu)
        e.add_field(name="Latest Changes:", value=revision)
        await ctx.send(embed=e)

    @commands.command()
    async def about(self, ctx):
        """Shows basic info about Kira."""
        total = 0
        file_amount = 0
        pyvi = sys.version_info
        spl = "https://discord.gg/dbUFDg7"
        discordi = f"Discord.py: v{discord.__version__} (Branch rewrite)"
        python = f"Python: v{pyvi.major}.{pyvi.minor}.{pyvi.micro} (Branch {pyvi.releaselevel} v{pyvi.serial})"
        invl = "https://discordapp.com/oauth2/authorize?client_id=538344287843123205&scope=bot&permissions=267779137"
        b = str.encode(self.bot.http.token.split(".")[1] + '==')
        b = base64.b64decode(b)
        b = int(codecs.encode(b, 'hex'), 16)
        cdate = f"{datetime.datetime.fromtimestamp(b + 1293840000)}"
        owner = self.bot.get_user(self.bot.owner_id)
        for path, subdirs, files in os.walk('.'):
            for name in files:
                if name.endswith('.py'):
                    file_amount += 1
                    with codecs.open('./' + str(pathlib.PurePath(path, name)), 'r', 'utf-8') as f:
                        for i, l in enumerate(f):
                            if l.strip().startswith('#') or len(l.strip()) is 0:  # skip commented lines.
                                pass
                            else:
                                total += 1
        code = f'I am made of {total:,} lines of Python, spread across {file_amount:,} files!'
        e = discord.Embed()
        e.colour = 0x36393E
        e.add_field(name="Helpfull Links:", value=f"[Invite]({invl}) | [Support]({spl})")
        e.add_field(name="Developer:", value=owner)
        e.add_field(name="Libraries:", value=f"{discordi}\n{python}")
        e.add_field(name="Date created:", value=cdate)
        e.add_field(name="Code Information:", value=code)
        e.set_thumbnail(url=self.bot.user.avatar_url)
        e.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=e)

    @commands.command()
    async def uptime(self, ctx):
        """How long have I been online?"""
        uptime = self.get_bot_uptime()
        await ctx.send(uptime)

    @commands.command()
    @commands.check(checks.is_owner)
    async def speedtest(self, ctx):
        """Check the bots speed."""
        msg = await ctx.send("Collecting information, one second....")
        #servers = ['10395']
        s = speedtest.Speedtest()
        #s.get_servers(servers)
        s.get_best_server()
        up = s.download()
        down = s.upload()
        await msg.delete()
        await ctx.trigger_typing()
        await ctx.send(f"{ctx.author.mention} Here are my speedtest results:\n**Download:** {humanize.naturalsize(down)}S\n**Upload:** {humanize.naturalsize(up)}S")

    @commands.command()
    @commands.guild_only()
    @commands.check(checks.can_embed)
    async def roleinfo(self, ctx, role : discord.Role):
        """Shows information on a role."""
        tperms = []
        fperms = []
        perms = iter(role.permissions)
        for x in perms:
            if "True" in str(x):
                tperms.append(str(x).split('\'')[1])
            else:
                fperms.append(str(x).split('\'')[1])
        e = discord.Embed(colour=role.colour)
        e.add_field(name="Name:", value=role.name)
        e.add_field(name="Id:", value=role.id)
        e.add_field(name="Created:", value=role.created_at)
        e.add_field(name="Managed:", value=role.managed)
        e.add_field(name="Position:", value=role.position)
        e.add_field(name="Color:", value="#{:06x}".format(role.color.value))
        e.add_field(name="Separately displayed:", value=role.hoist)
        e.add_field(name="Mentionable:", value=role.mentionable)
        e.add_field(name="Permissions:", value=f"**Valid:** {', '.join(tperms)}\n**Invalid:** {', '.join(fperms)}", inline=False)
        await ctx.send(embed=e)

    @commands.command()
    @commands.guild_only()
    @commands.check(checks.can_embed)
    async def serverinfo(self, ctx):
        """Check info about current server """
        members = set(ctx.guild.members)
        offline = filter(lambda m: m.status is discord.Status.offline, members)
        offline = set(offline)
        bots = filter(lambda m: m.bot, members)
        bots = set(bots)
        users = members - bots
        embed = discord.Embed(colour=0x36393E)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(name="Server Name", value=ctx.guild.name, inline=True)
        embed.add_field(name="Server ID", value=ctx.guild.id, inline=True)
        embed.add_field(name="Owner", value=ctx.guild.owner, inline=True)
        embed.add_field(name="Region", value=ctx.guild.region, inline=True)     
        embed.add_field(name="Created on", value=default.date(ctx.guild.created_at), inline=True)
        embed.add_field(name="Users", value=f"**Total Users:** {len(users)}\n**Users Online:** {len(users - offline)}\n**Users Offline:** {len(users & offline)}", inline=True)
        embed.add_field(name="Bots", value=f"**Total Bots:** {len(bots)}\n**Bots Online:** {len(bots - offline)}\n**Bots Offline:** {len(bots & offline)}", inline=True)
        await ctx.send(embed = embed)
		
    @commands.command()
    @commands.guild_only()
    @commands.check(checks.can_embed)
    async def userinfo(self, ctx, user: discord.Member = None):
        """Get user information"""
        if user is None:
            user = ctx.author
        roles = [x.mention for x in user.roles if x.name != "@everyone"]
        roles = ', '.join(roles)
        embed = discord.Embed(colour=0x36393E)
        embed.set_thumbnail(url=user.avatar_url)
        embed.add_field(name="Name", value=user, inline=True)
        if hasattr(user, "nick"):
            embed.add_field(name="Nickname", value=user.nick, inline=True)
        else:
            embed.add_field(name="Nickname", value="No nickname.", inline=True)
        embed.add_field(name="Joined Discord on", value=default.date(user.created_at), inline=True)
        if hasattr(user, "joined_at"):
            embed.add_field(name="Joined this server on", value=default.date(user.joined_at), inline=True)
        if roles != "":
            embed.add_field(name="Roles", value=roles)
        else:
            embed.add_field(name="Roles", value="User has no roles.")
        await ctx.send(embed=embed)

    @commands.command()
    async def patreon(self, ctx):
        """Shows Patreon stats."""
        async with self.bot.session as session:
            async with session.get('http://api.patreon.com/user/8692289') as resp:
                data = await resp.json()
                if len(data["included"]) > 0:
                    patrons = str(data['included'][0]['attributes']['patron_count'])
                    pledge = str(data['included'][0]['attributes']['pledge_sum'])[:-2]
                else:
                    patrons = "N/A"
                    pledge = "N/A"
        await ctx.send(f"There is currently {patrons} patrons, supporting with ${pledge} per month. Want to become a patron? Head on over to the link. <https://www.patreon.com/user?u=8692289>")

    @commands.command()
    @commands.check(checks.can_embed)
    async def avatar(self, ctx, user: discord.Member = None):
        """ Get the avatar of you or someone else """
        if user is None:
            user = ctx.author
        png = user.avatar_url_as(format='png')
        jpg = user.avatar_url_as(format='jpg')
        webp = user.avatar_url_as(format='webp')
        embed = discord.Embed(colour=0x36393E)
        embed.description = "**{}** Avatar:".format(user.name)
        embed.add_field(name="Formats:", value=f"[Png]({png}) | [Jpg]({jpg}) | [Webp]({webp})")
        embed.set_image(url=png)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Info(bot))
