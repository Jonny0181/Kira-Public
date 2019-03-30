import os
import glob
import discord
import asyncio
import aiohttp
import async_timeout
from utils import checks
from discord.ext import commands
from subprocess import check_output, CalledProcessError

wrap = "```py\n{}```"

class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.check(checks.is_owner)
    @commands.command()
    async def botavatar(self, ctx):
        """Change the bot's profile pic"""
        if ctx.message.attachments:
            attachment_url = ctx.message.attachments[0].url
            try:
                with async_timeout.timeout(5):
                    async with self.bot.session.get(attachment_url) as req:
                        await self.bot.user.edit(avatar=(await req.read()))
            except asyncio.TimeoutError:
                await ctx.send(':x: The picture is too large!')
            await ctx.message.add_reaction('✅')
        else:
            await ctx.send(':x: You have to attach one **PNG** file!')

    @commands.command()
    async def modules(self, ctx):
        """Shows Kira's modules."""
        loaded = [c.__module__.split(".")[1] for c in self.bot.cogs.values()]
        unloaded = [c.split(".")[1] for c in self._list_modules() if c.split(".")[1] not in loaded]
        if not unloaded:
            unloaded = ['All modules are loaded']
        e = discord.Embed()
        e.colour = 0x36393E
        e.set_author(name="Kira's modules.", icon_url=self.bot.user.avatar_url)
        e.set_thumbnail(url=self.bot.user.avatar_url)
        e.add_field(name="<:check:433159782287802369> Loaded Modules:", value=", ".join(sorted(loaded)))
        e.add_field(name="<:tickred:539495579793883176> Unloaded Modules:", value=", ".join(sorted(unloaded)))
        await ctx.send(embed=e)

    @commands.check(checks.is_owner)
    @commands.command()
    async def restart(self, ctx):
        """Restarts Kira."""
        await ctx.send('Restarting..')
        await self.bot.shutdown()

    @commands.group()
    @commands.check(checks.is_owner)
    @commands.check(checks.can_embed)
    async def pip(self, ctx):
        """Pip tools."""
        if ctx.invoked_subcommand is None:
            e = discord.Embed()
            e.colour = 0x36393E
            e.description = "**upgrade -** Upgrade pip programs for Python 3.5\n"
            e.description += "**uninstall -** Uninstall pip programs for Python 3.5\n"
            e.description += "**install -** Install pip programs for Python 3.5"
            e.set_author(name="Help for {}'s command group {}.".format(self.bot.user.name, ctx.command), icon_url=self.bot.user.avatar_url)
            e.set_thumbnail(url=self.bot.user.avatar_url)
            await ctx.send(embed=e)

    @pip.command()
    async def install(self, ctx, packagename):
        """Install pip programs for Python 3.5"""
        try:
            output = check_output("pip3 install {}".format(packagename), shell=True)
            await ctx.send("Package `{}` installed succesfully!".format(packagename))
        except Exception as e:
            await ctx.send(e)

    @pip.command()
    async def uninstall(self, ctx, packagename):
        """Uninstall pip programs for Python 3.5"""
        try:
            output = check_output("pip3 uninstall {}".format(packagename), shell=True)
            await ctx.send("Package `{}` uninstalled succesfully!".format(packagename))
        except Exception as e:
            await ctx.send(e)

    @pip.command()
    async def upgrade(self, ctx, packagename):
        """Upgrade pip programs for Python 3.5"""
        try:
            output = check_output("pip3 install {} --upgrade".format(packagename), shell=True)
            await ctx.send("Package `{}` upgraded succesfully!".format(packagename))
        except Exception as e:
            await ctx.send(e)
            
    def _list_modules(self):
        modules = [os.path.basename(f) for f in glob.glob("modules/*.py")]
        return ["modules." + os.path.splitext(f)[0] for f in modules]

def setup(bot):
   bot.add_cog(Dev(bot))
