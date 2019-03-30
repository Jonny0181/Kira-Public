import discord
import traceback
from discord.ext import commands

CCYAN = '\33[36m'
CYELLOW = '\33[33m'
CPURPLE = '\33[35m'
CBLUE = '\33[34m'
CRED = '\33[31m'
CGREEN = '\33[32m'
CEND = '\33[0m'

class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot  = bot
        
    @commands.Cog.listener()
    async def check_commands(self, ctx):
        if not ctx.guild:
            return True
        author = ctx.author
        guild = ctx.guild
        channel = ctx.channel
        logs = await idb.find_one({'guild_id': guild.id})
        ban = client['kira_banlist']
        ban = ban.banlistdb
        ban = await ban.find_one({'kira_id': self.user.id})
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
                await idb.insert_one(settings)
                return True
        except Exception as e:
            print(f"Error in ignore function: {e}")
            return True

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            a = discord.Embed(colour=0x36393E)
            a.set_author(name=f"{ctx.command.name} {ctx.command.signature}", icon_url=self.bot.user.avatar_url)
            a.description = f"{ctx.command.help}"
            await ctx.send(embed=a)
        elif isinstance(error, commands.BadArgument):
            a = discord.Embed(colour=0x36393E)
            a.set_author(name=f"{ctx.command.name} {ctx.command.signature}", icon_url=self.bot.user.avatar_url)
            a.description = f"{ctx.command.help}"
            await ctx.send(embed=a)
        elif isinstance(error, commands.CommandOnCooldown):
            seconds = error.retry_after
            seconds = round(seconds, 2)
            await ctx.send(f'<:tickred:539495579793883176> Mate slow the fuck down. {seconds}s remaining.', delete_after=10)
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send('<:tickred:539495579793883176> Mate you can\'t use that command in DMS, please invite me to a server or go to one I\'m in.', delete_after=10)
        elif isinstance(error, discord.Forbidden):
            await ctx.send("I dont have permissions to execute this command.")
        else:
            if ctx.command:
                e = discord.Embed(title="Command threw an error! Join the support server with k.support", description="An error has been thrown with this command!", colour=0x36393E)
                e.add_field(name="Command Name:", value=ctx.command.name, inline=False)
                e.add_field(name="Error:", value="".join(traceback.format_exception(type(error.original), error.original, error.original.__traceback__)), inline=False)
                e.add_field(name="Command Help:", value=ctx.command.help, inline=False)
                await ctx.send(embed=e)
                channel = self.bot.get_channel(558595605014773761)
                a = discord.Embed()
                a.colour = 0x36393E
                a.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                a.add_field(name="Invoking message:", value=ctx.message.content)
                a.add_field(name="Error:", value="".join(traceback.format_exception(type(error.original), error.original, error.original.__traceback__)), inline=False)
                await channel.send(embed=a)
            print('{}Ignoring exception in command {}:\n{}{}'.format(CRED, ctx.command, "".join(traceback.format_exception(type(error.original), error.original, error.original.__traceback__)), CEND))

def setup(bot):
    bot.add_cog(ErrorHandler(bot))
