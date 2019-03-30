import discord
from discord.ext import commands
import datetime
from utils import checks

class GuildLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        e = discord.Embed(colour=0x36393E)
        e.description = f"<:check:534931851660230666> Joined guild {guild.name} with {guild.member_count} users. Now in {len(self.bot.guilds)} guilds."
        e.set_footer(text=f"Joined guild on {datetime.datetime.utcnow().strftime('%A %d %B %Y at %H:%M:%S')}")
        await self.bot.get_channel(550121953462059008).send(embed=e)
        self.bot.logger.info(f"[GUILD JOIN] Joined guild {guild.name} with {guild.member_count} users. Now in {len(self.bot.guilds)} guilds.")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        e = discord.Embed(colour=0x36393E)
        e.description = f"<:tickred:539495579793883176> Left guild {guild.name} with {guild.member_count} users. Now in {len(self.bot.guilds)} guilds."
        e.set_footer(text=f"Left guild on {datetime.datetime.utcnow().strftime('%A %d %B %Y at %H:%M:%S')}")
        await self.bot.get_channel(550121953462059008).send(embed=e)
        self.bot.logger.info(f"[GUILD LEAVE]  Left guild {guild.name} with {guild.member_count} users. Now in {len(self.bot.guilds)} guilds.")
        
def setup(bot):
    bot.add_cog(GuildLogs(bot))
