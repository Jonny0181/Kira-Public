import discord
from utils import checks
from discord.ext import commands

class Sounds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.music = self.bot.get_cog('Music')


    @commands.group()
    @commands.guild_only()
    @commands.check(checks.can_embed)
    async def sounds(self, ctx):
        """Soundboard sounds."""
        if ctx.invoked_subcommand is None:
            e = discord.Embed()
            e.colour = 0x36393E
            e.set_author(name="Help for Wakk's command group sounds.", icon_url=ctx.guild.me.avatar_url)
            e.description = "**add - ** Add a sound to your soundboard sounds..\n"
            e.description += "**delete -** Delete a sound from your soundboard sounds.\n"
            e.description += "**start -** Start a sound from your soundboard sounds.\n"
            e.description += "**show -** Show your soundboard sounds.\n"
            e.set_thumbnail(url=ctx.guild.me.avatar_url)
            await ctx.send(embed=e)

    @sounds.command(name="show")
    async def _show(self, ctx):
        """Show your soundboard sounds."""
        logs = await self.bot.db.sounds.find_one({"user_id": ctx.author.id})
        settings = {
            "user_id": ctx.author.id,
        }
        if not logs:
            await ctx.send("Database not found for you, create one by adding a sound.")
            return
        if logs:
            if logs == settings:
                await ctx.send("You have a database, but you don't have any sounds, use the command `..sounds` to add some, use this as an example `..sounds add <sound_name>`")
                return
        number = 0
        data = discord.Embed()
        data.set_author(name="Here are those lit soundboard sounds.", icon_url=ctx.author.avatar_url)
        data.colour = 0x36393E
        description = "\n**Available Sounds:**\n"
        for key, val in logs.items():
            if "_id" in key:
                continue
            number += 1
            description += f"`{number})` {key}\n"
        if description == "\n**Available Sounds:**\n":
            description += "Oh you don't have any sounds? Here is how to add some."
            data.description = description.replace('\n**Available Sounds:**\n', '')
            data.set_image(url="http://the-best.thicc-ho.es/34e04ecb36.gif")
        data.description = description
        await ctx.send(embed=data)

    @sounds.command(name="add")
    async def _add(self, ctx, sound_name: str):
        """Add a sound to your soundboard sounds."""
        logs = await self.bot.db.sounds.find_one({"user_id": ctx.author.id})
        msg = ctx.message
        if not msg.attachments:
            await ctx.send("Please attach a sound file to the command message.")
            return
        if ("png" or "jpg" or "gif" or "webp") in msg.attachments[0].url:
            await ctx.send("Please only use audio files.")
            return
        if msg.attachments[0].size > 1000000:
            await ctx.send("I'm sorry but you can only add sounds that are 1mb.")
            return
        if not logs:
            settings = {
                "user_id": ctx.author.id,
            }
            await self.bot.db.sounds.insert_one(settings)
        try:
            await self.bot.db.sounds.update_one({"user_id": ctx.author.id}, {'$set': {sound_name: msg.attachments[0].url}})
            await ctx.send("Done, I have added your file to your database. DO NOT DELETE THE FILE FROM DISCORD IT WILL BREAK. Unless you don't want to be able to play this sound anymore.")
        except Exception as e:
            await ctx.send(e)

    @sounds.command(name="delete")
    async def _delete(self, ctx, sound_name: str):
        """Delete a sound from your soundboard sounds."""
        logs = await self.bot.db.sounds.find_one({"user_id": ctx.author.id})
        if logs:
            if logs[sound_name]:
                await self.bot.db.sounds.update_one({"user_id": ctx.author.id}, {'$unset': {sound_name: logs[sound_name]}})
                await ctx.send("Done, deleted.")
                return
            else:
                await ctx.send("Sorry, but I couldn't find that sound in your databse.")
                return
        else:
            await ctx.send("Why are you trying to delete something when you don't have a databse?")

    @sounds.command(name="start")
    @commands.check(checks.in_voice)
    async def _start(self, ctx, sound_name: str):
        """Start a sound from your soundboard sounds."""
        logs = await self.bot.db.sounds.find_one({"user_id": ctx.author.id})
        if logs:
            try:
                if logs[sound_name]:
                    msg = await ctx.send("Playing...")
                    await self.music.play(ctx, ctx.guild, ctx.message, ctx.author, ctx.channel, msg, False, True, logs[sound_name])
                else:
                    await ctx.send("Sorry, but I couldn't find that sound in your databse.")
                    return
            except:
                await ctx.send("Sorry, but I couldn't find that sound in your databse.")
        else:
            await ctx.send("Why are you trying to play something when you don't have a databse?")

def setup(bot):
    n = Sounds(bot)
    bot.add_cog(n)
