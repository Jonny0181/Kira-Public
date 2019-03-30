import discord
import asyncio
from discord.ext import commands
from random import choice as rndchoice

class RndStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.set_status())

    async def set_status(self):
        await self.bot.wait_until_ready()
        while True:
            pnbr = len([p for p in self.bot.lavalink.players._players.values() if p.is_playing])
            if pnbr > 1:
                npstatus = "music in {} servers.."
            elif pnbr == 0:
                npstatus = "No servers playing music at this time.."
            else:
                npstatus = "music in {} server.."
            statuses = [
                npstatus,
                "k.help | k.invite",
                "k.help | k.support",
                "{} guilds..",
                "{} members.."
            ]
            new = rndchoice(statuses)
            if new == "{} guilds..":
                await self.bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=new.format(len(self.bot.guilds))))
            elif new == "{} members..":
                await self.bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=new.format(len([e.name for e in self.bot.get_all_members()]))))
            elif new == "music in {} server..":
                await self.bot.change_presence(activity=discord.Streaming(name=new.format(pnbr), url="https://www.twitch.tv/snpmv"))
            elif new == "music in {} servers..":
                await self.bot.change_presence(activity=discord.Streaming(name=new.format(pnbr), url="https://www.twitch.tv/snpmv"))
            else:
                await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(name=new))
            await asyncio.sleep(25)

def setup(bot):
    n = RndStatus(bot)
    bot.add_cog(n)
