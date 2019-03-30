import discord
import os
import time
import random
import datetime
import string
import asyncio
import json
import textwrap
import async_timeout
from utils import checks
from lxml.html import fromstring
from discord.ext import commands
from random import choice as randchoice
from PIL import Image, ImageDraw, ImageFont

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def chuck_noris(self, ctx):
        catagories = ["explicit","dev","movie","food","celebrity","science","sport","political","religion","animal","history","music","travel","career","money","fashion"]
        url = f'https://api.chucknorris.io/jokes/random?category={random.choice(catagories)}'
        async with self.bot.session.get(url) as resp:
            if resp.status is not 200:
                await ctx.send('Error: cannot fetch api.chucknorris.io data.')
                return
            else:
                return await resp.json()

    @commands.group()
    async def random(self, ctx):
        """Random response commands."""
        if ctx.invoked_subcommand is None:
            e = discord.Embed()
            e.colour = 0x36393E
            e.set_author(name="Help for Kira's command group random.", icon_url=self.bot.user.avatar_url)
            e.description = "**message - ** Sends a random message.\n"
            e.description += "**dinner -** Get a random recipie for dinner.\n"
            e.set_thumbnail(url=self.bot.user.avatar_url)
            await ctx.send(embed=e)
        
    @random.command()
    async def dinner(self, ctx):
        """Get a random recipie for dinner."""
        async with self.bot.session.get('http://whatthefuckshouldimakefordinner.com/') as resp:
            e = fromstring(await resp.text())
            dl = e.cssselect('dl')
            a, b = [(t.text_content()).strip() for t in dl[:2]]
            link = dl[1].xpath('dt/a')[0].attrib['href']
        return await ctx.send(f'{a} {b}.\n**Link to recipe:** <{link}>')

    @random.command()
    @commands.guild_only()
    async def message(self, ctx, channel: discord.TextChannel=None):
        """Send a random message."""
        if channel is None:
            channel = ctx.channel
        if channel.is_nsfw() is True and ctx.channel.is_nsfw() is False:
            await ctx.send("<:tickred:539495579793883176> Yeet, you fucking thought.")
            return
        try:
            def strTimeProp(start, end, format, prop):
                stime = time.mktime(time.strptime(start, format))
                etime = time.mktime(time.strptime(end, format))
                ptime = stime + prop * (etime - stime)
                return time.strftime(format, time.localtime(ptime))
            def randomDate(start, end, prop):
                return strTimeProp(start, end, '%Y-%m-%d %H:%M:%S', prop)
            cnl = channel.created_at.strftime('%Y-%m-%d %H:%M:%S')
            msg = ctx.message.created_at.strftime('%Y-%m-%d %H:%M:%S')
            date = randomDate(cnl, msg, random.random())
            newdate = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
            msg = random.choice(await channel.history(limit=1, before=newdate).flatten())
            e = discord.Embed()
            e.colour = 0x36393E
            e.set_author(name=f"{msg.author} said:", url=msg.jump_url, icon_url=msg.author.avatar_url)
            e.set_footer(text=f"Message created at: {msg.created_at.strftime('%m/%d/%Y %I:%M %p')}")
            if msg.embeds:
                urls = []
                author = ""
                e.description = f"Yeet, it was an embed.\n"
                if msg.content:
                    e.add_field(name="Content:", value=msg.content)
                l = msg.embeds[0]
                if l.author:
                    if l.author.name:
                        author += f"**Name:** {l.author.name}\n"
                    if l.author.icon_url:
                        e.set_thumbnail(url=l.author.icon_url)
                        author += "(Thumbnail is the authors avatar.)"
                if author != "":
                    e.add_field(name="Author:", value=author)
                if l.image:
                    urls.append(l.image.url)
                if l.thumbnail:
                    urls.append(l.thumbnail.url)
                if l.colour:
                    e.add_field(name="Colour", value=l.colour.value)
                if l.url:
                    e.set_image(url=l.url)
                if l.title:
                    e.add_field(name="Title:", value=l.title)
                if l.description:
                    e.add_field(name="Description:", value=l.description)
                if l.fields != []:
                    oof = ""
                    for field in l.fields:
                        oof += f"**{field.name}:** {field.value}\n"
                    e.add_field(name="Fields:", value=oof)
                if l.footer:
                    e.add_field(name="Footer:", value=l.footer.text)
                if urls != []:
                    e.add_field(name="Image Urls:", value="\n".join(urls))
            else:
                if msg.attachments:
                    if msg.content == "":
                        e.description = f"Yeet, it was an image.\n"
                        e.set_image(url=msg.attachments[0].url)
                    else:
                        e.description = f"{msg.content}\n"
                        e.set_image(url=msg.attachments[0].url)
                else:
                    e.description = f"{msg.content}\n"
            await ctx.send(embed=e)
        except:
            await ctx.send("Sorry but I was unable to retrieve the message.")

    @commands.check(checks.delete)
    @commands.command()
    @commands.guild_only()
    async def say(self, ctx, *, content: str):
        """Make Kira say something."""
        content = content.replace('@everyone', 'everyone')
        content = content.replace('@here', 'here')
        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.send(content)
        
    @commands.command()
    @commands.guild_only()
    @commands.check(checks.in_voice)
    async def videochannel(self, ctx):
        """Makes the bot create a link to your voice channel for video call or screenshare."""
        guild = ctx.guild
        author = ctx.author
        link = "https://discordapp.com/channels/"
        await ctx.send(f'Here is your link:\n<{link}{guild.id}/{author.voice.channel.id}>')

    @commands.command()
    async def billy(self, ctx):
        """Random Billy meme."""
        url = "https://belikebill.ga/billgen-API.php?default=1"
        url = url + "&" + "".join(random.sample(string.ascii_lowercase,10)) + "=" + "".join(random.sample(string.ascii_lowercase,10)) 
        e = discord.Embed()
        e.colour = 0x36393E
        e.set_image(url=url)
        await ctx.send(embed=e)

    @commands.command(aliases=['cn'])
    async def chucknorris(self, ctx):
        """Posts a random Chuck Norris joke."""
        await ctx.trigger_typing()
        data = await self.chuck_noris(ctx)
        if data:
            e = discord.Embed()
            e.colour = 0x36393E
            e.set_author(name="Chuck Norris Joke", icon_url=data['icon_url'])
            e.description = data['value']
            await ctx.send(embed=e)
        else:
            await ctx.send('Error: cannot fetch api.chucknorris.io data.')

    @commands.command(aliases=['suggestion'])
    async def suggest(self, ctx, *, suggestion: str):
        """Send a command or feature suggestion to the developer."""
        owner = self.bot.get_user(170619078401196032)
        e = discord.Embed()
        e.colour = 0x36393E
        e.set_author(name=f"{ctx.author} has made a suggestion!", icon_url=ctx.author.avatar_url)
        e.description = suggestion
        e.set_footer(text=f"Suggestion created at: {ctx.message.created_at.strftime('%m/%d/%Y %I:%M %p')}")
        await owner.send(embed=e)
        await ctx.send("Suggestion send!", delete_after=5)

    @commands.command(aliases=['cp'])
    async def copypasta(self, ctx):
        """Copy pastas."""
        await ctx.trigger_typing()
        with open('data/jsons/cps.json') as fp:
            data = json.load(fp)
        cp = randchoice(data)
        await ctx.send(cp)

    @commands.guild_only()
    @commands.command()
    async def insult(self, ctx, user : discord.Member=None):
        """Insult a user."""
        await ctx.trigger_typing()
        with open('data/jsons/insults.json') as fp:
            data = json.load(fp)
        insult = randchoice(data)
        msg = ' '
        if user != None:
            if user.id == self.bot.user.id:
                user = ctx.message.author
                msg = "<:tickred:539495579793883176> Yeet, you fokin thoughtttt."
                await ctx.send(user.mention + msg)

            else:
                await ctx.send(user.mention + msg + insult)
        else:
            await ctx.send(ctx.message.author.mention + msg + insult)

    @commands.command()
    @commands.guild_only()
    @commands.check(checks.is_nsfw)
    @commands.check(checks.can_embed)
    async def ricardo(self, ctx):
        """Post's a random ricardo meme or video."""
        await ctx.trigger_typing()
        try:
            path = "data/ricardo/"
            files = os.listdir(path)
            index = random.randrange(0, len(files))
            file = path+files[index]
            await ctx.trigger_typing()
            await ctx.send(file=discord.File(file))
        except:
            await ctx.send("Uh oh! And error. Check to make sure I have permissions to send files.")
     
    @commands.guild_only()
    @commands.command()
    async def rr(self, ctx, rounds: int=1):
        """Russian roulette.
        
        - Rounds is how many rounds you want to have in the chamber.
        Example: k.rr 2
        - This will put two rounds in the chamber. And make the stakes higher."""
        filled = []
        count = 0
        death = [
            f"{ctx.author.mention} **SPLAT!** 🔫💥 Your brains where splattered all over the wall.",
            f"{ctx.author.mention} **SPLAT!** 🔫💥 Your brains are now all over the floor.",
            f"{ctx.author.mention} **BANG!** 🔫💥 You have shot yourself in the head. Your life is now flashing before your eyes.",
            f"{ctx.author.mention} **KAPOW!** 🔫💥 You have shot yourself in foot, looks like you got lucky.",
            f"{ctx.author.mention} **BANG!** 🔫💥 You have shot yourself in the leg. You may think you got lucky. But you didn't make it. You where loosing so much blood on the way to the hospital you died in the ambulance."
            ]
        live = [
            f"{ctx.author.mention} Welp, looks like you live to see another day",
            f"{ctx.author.mention} Huh, looks like you got lucky.",
            f"{ctx.author.mention} Wow, is someone watching over you? 🤔",
            f"{ctx.author.mention} Tsk tsk tsk, you got lucky this time. I'll get you next time. 😪",
            f"{ctx.author.mention} C-can you just not be so lucky for once? 😫"
            ]
        if rounds > 6:
            await ctx.send("You cannot have more than 6 rounds! There is only 6 slots in a revolver cylinder!")
            return
        if rounds < 1:
            await ctx.send("You have to at least put 1 round in the revolver cylinder...")
            return
        async with ctx.typing():
            if rounds == 1:
                msg = await ctx.send(f"Loading **{rounds}** round into the cylinder...")
            else:
                msg = await ctx.send(f"Loading **{rounds}** rounds into the cylinder...")
            while not count == rounds:
                slot = random.randint(1, 6)
                if not slot in filled:
                    filled.append(slot)
                    count += 1
            await asyncio.sleep(2)
            await msg.edit(content="Spinning the cylinder...")
            await asyncio.sleep(2)
            await msg.edit(content="Pulling the trigger...")
            await asyncio.sleep(2)
            landed = random.randrange(1, 6)
            if landed in filled:
                await msg.delete()
                await ctx.send(random.choice(death))
            else:
                await msg.delete()
                await ctx.send(random.choice(live))
                     
def setup(bot):
    n = Fun(bot)
    bot.add_cog(n)
