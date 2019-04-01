import discord
from discord.ext import commands
import datetime

class GuildLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        msg = f"<:check:534931851660230666> Joined guild {guild.name} with {guild.member_count} users. Now in {len(self.bot.guilds)} guilds."
        print(msg)
        self.bot.logger.info(f"[GUILD JOIN] Joined guild {guild.name} with {guild.member_count} users. Now in {len(self.bot.guilds)} guilds.")

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        msg = f"<:tickred:539495579793883176> Left guild {guild.name} with {guild.member_count} users. Now in {len(self.bot.guilds)} guilds."
        print(msg)
        self.bot.logger.info(f"[GUILD LEAVE]  Left guild {guild.name} with {guild.member_count} users. Now in {len(self.bot.guilds)} guilds.")
        
def setup(bot):
    bot.add_cog(GuildLogs(bot))
