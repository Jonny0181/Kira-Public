import re
import jishaku
from utils import checks
from discord.ext import commands
from collections import namedtuple

Codeblock = namedtuple('Codeblock', 'language content')
CODEBLOCK_REGEX = re.compile("^(?:```([A-Za-z0-9\\-\\.]*)\n)?(.+?)(?:```)?$", re.S)

class REPL(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sessions = set()

    @commands.command()
    @commands.check(checks.is_owner)
    async def repl(self, ctx):
        """Start a JSK session."""
        if ctx.channel.id in self.sessions:
            await ctx.send('Already running a JSK session in this channel. Exit it with `quit`.')
            return
        self.sessions.add(ctx.channel.id)
        await ctx.send('Enter code to execute or evaluate. `exit` or `quit` to exit.')
        self.bot.get_cog('Jishaku').retain = True
        self.bot.get_cog('Jishaku')._scope = jishaku.repl.Scope()
        while True:
            response = await self.bot.wait_for(
                "message",
                check=lambda m: (m.author == ctx.author and
                                 m.channel == ctx.channel))
            content = response.content
            oof = await self.bot.get_context(response)
            if content in ('quit', 'exit', 'exit'):
                await ctx.send('Quiting JSK session.')
                self.bot.get_cog('Jishaku').retain = False
                self.sessions.remove(ctx.channel.id)
                return
            elif content.startswith('```py\n') and content.endswith('```'):
                result = await self.convert(ctx, argument=content)
                await oof.invoke(self.bot.get_command('jsk py'), argument=result)
            elif content.startswith('`'):
                hm = content[1:]
                result = await self.convert(ctx, argument=hm)
                await oof.invoke(self.bot.get_command('jsk py'), argument=result)

    async def convert(self, ctx, argument):
        match = CODEBLOCK_REGEX.search(argument)
        if not match:
            return Codeblock(None, argument)
        return Codeblock(match.group(1), match.group(2))

def setup(bot):
    bot.add_cog(REPL(bot))
