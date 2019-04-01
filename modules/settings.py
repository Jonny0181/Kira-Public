import discord
import random
import asyncio
import os
from io import BytesIO
from PIL import Image, ImageFont, ImageOps, ImageDraw
from utils import checks
from discord.ext import commands

class Settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.guild_only()
    async def settings(self, ctx):
        """Kira settings for your server."""
        guild = ctx.guild
        logs = await self.bot.db.settings.find_one({'guild_id': ctx.guild.id})
        if not logs:
            settings = {
                "guild_id": guild.id,
                "prefix" : None,
                "djrole": None,
                "announce_channel": None,
                "toggle": False,
            }
            await self.bot.db.settings.insert_one(settings)
        if ctx.invoked_subcommand is None:
            e = discord.Embed()
            e.colour = 0x36393E
            e.set_author(name="Help for Kira's command group settings.", icon_url=ctx.guild.me.avatar_url)
            e.description = "**prefix - ** Set a custom prefix for your guild.\n"
            e.description += "**music -** Setup music settings for your guild..\n"
            e.description += "**deleteall -** This will delete all of your guilds settings.\n"
            e.description += "**banlist -** Add or remove users from the banlist.\n"
            e.description += "**welcomer -** Welcomer settings for your guild.\n"
            e.description += "**ignore -** Ignore a user, role, or channel.\n"
            e.description += "**unignore -** Unignore a user, role, or channel.\n"
            e.description += "**config -** Shows all settings for the current guild.\n"
            e.set_thumbnail(url=ctx.guild.me.avatar_url)
            await ctx.send(embed=e)

    @settings.command()
    @commands.check(checks.guild)
    async def prefix(self, ctx, prefix : str=None):
        """Set a custom guild prefix."""
        guild = ctx.guild
        logs = await self.bot.db.settings.find_one({'guild_id': guild.id})
        if not logs:
            welp = {
                "guild_id": guild.id,
                "prefix" : None,
                "djrole": None,
                "mchnl": False,
                "toggle": False,
                "channelid": None
            }
            await self.bot.db.settings.insert_one(welp)
        if prefix == None:
            if logs['prefix'] == None:
                await ctx.send(f'You can set a prefix by using `{ctx.prefix}settings prefix <your_prefix>`.')
                return
            else:
                await ctx.send("Your current prefix is `{}`. You can also still use `[k., k!]`.".format(logs['prefix']))
                return
        if prefix == logs['prefix']:
            await ctx.send("Aye your prefix is already that.")
            return
        else:
            await self.bot.db.settings.update_one({'guild_id': guild.id}, {'$set':{'prefix': prefix}})
            await ctx.send("Done, I have set your custom prefix! Also here is a little tip. If you forget your prefix just use <@!538344287843123205>.")
            return

    @settings.group(name="unignore")
    async def _unignore(self, ctx):
        """Unignore a user, role, or channel."""
        if ctx.invoked_subcommand is None or isinstance(ctx.invoked_subcommand, commands.Group):
            e = discord.Embed(description="""
**user -** Unignore a user.
**role -** Unignore a role.
**channel -** Unignore a channel.""")
            e.colour = 0x36393E
            e.set_author(name="Help for {}'s command group {}.".format(ctx.bot.user.name, ctx.command), icon_url=ctx.guild.me.avatar_url)
            e.set_thumbnail(url=ctx.guild.me.avatar_url)
            await ctx.send(embed=e)

    @_unignore.command(name="user")
    @commands.check(checks.guild)
    async def _user(self, ctx, user: discord.User):
        """Unignores a user in your guild."""
        guild = ctx.guild
        logs = await self.bot.db.ignore.find_one({'guild_id': guild.id})
        if not logs:
            settings = {
                "guild_id": guild.id,
                "channels" : [], 
                "users" : [], 
                "roles" : []
            }
            await self.bot.db.ignore.insert_one(settings)
        if user.id in logs["users"]:
            await self.bot.db.ignore.update_one({'guild_id': guild.id}, {'$pull':{'users': user.id}})
            await ctx.send("{} User removed the ignore list!".format(ctx.author.mention))
        else:
            await ctx.send(":x: {} User is not in the ignore list!".format(ctx.author.mention))

    @_unignore.command(name="channel")
    @commands.check(checks.guild)
    async def _channel(self, ctx, channel: discord.TextChannel):
        """Unignores a channel in your guild."""
        guild = ctx.guild
        logs = await self.bot.db.ignore.find_one({'guild_id': guild.id})
        if not logs:
            settings = {
                "guild_id": guild.id,
                "channels" : [], 
                "users" : [], 
                "roles" : []
            }
            await self.bot.db.ignore.insert_one(settings)
        if channel.id in logs["channels"]:
            await self.bot.db.ignore.update_one({'guild_id': guild.id}, {'$pull':{'channels': channel.id}})
            await ctx.send("{} Channel removed the ignore list!".format(ctx.author.mention))
        else:
            await ctx.send(":x: {} Channel is not in the ignore list!".format(ctx.author.mention))

    @_unignore.command(name="role")
    @commands.check(checks.guild)
    async def _role(self, ctx, role: discord.Role):
        """Unignores a role in your guild."""
        guild = ctx.guild
        logs = await self.bot.db.ignore.find_one({'guild_id': guild.id})
        if not logs:
            settings = {
                "guild_id": guild.id,
                "channels" : [], 
                "users" : [], 
                "roles" : []
            }
            await self.bot.db.ignore.insert_one(settings)
        if role.id in logs["roles"]:
            await self.bot.db.ignore.update_one({'guild_id': guild.id}, {'$pull':{'roles': role.id}})
            await ctx.send("{} Role removed the ignore list!".format(ctx.author.mention))
        else:
            await ctx.send(":x: {} Role is not in the ignore list!".format(ctx.author.mention))

    @settings.group()
    @commands.check(checks.guild)
    async def ignore(self, ctx):
        """Ignore a role, user, or channel."""
        if ctx.invoked_subcommand is None or isinstance(ctx.invoked_subcommand, commands.Group):
            e = discord.Embed(description="""
**user -** Ignore a user.
**role -** Ignore a role.
**channel -** Ignore a channel.""")
            e.colour = 0x36393E
            e.set_author(name="Help for {}'s command group {}.".format(ctx.bot.user.name, ctx.command), icon_url=ctx.guild.me.avatar_url)
            e.set_thumbnail(url=ctx.guild.me.avatar_url)
            await ctx.send(embed=e)

    @ignore.command()
    @commands.check(checks.guild)
    async def user(self, ctx, user: discord.User):
        """Ignores a user in your guild."""
        guild = ctx.guild
        logs = await self.bot.db.ignore.find_one({'guild_id': guild.id})
        if not logs:
            settings = {
                "guild_id": guild.id,
                "channels" : [], 
                "users" : [], 
                "roles" : []
            }
            await self.bot.db.ignore.insert_one(settings)
        if user.id in logs["users"]:
            await ctx.send(":x: {} User is already in the ignore list!".format(ctx.author.mention))
        else:
            await self.bot.db.ignore.update_one({'guild_id': guild.id}, {'$push':{'users': user.id}})
            await ctx.send("{} User added to ignore list!".format(ctx.author.mention))

    @ignore.command()
    @commands.check(checks.guild)
    async def role(self, ctx, role: discord.Role):
        """Ignores a role in your guild."""
        guild = ctx.guild
        logs = await self.bot.db.ignore.find_one({'guild_id': guild.id})
        if not logs:
            settings = {
                "guild_id": guild.id,
                "channels" : [], 
                "users" : [], 
                "roles" : []
            }
            await self.bot.db.ignore.insert_one(settings)
        if role.id in logs["roles"]:
            await ctx.send(":x: {} Role is already in the ignore list!".format(ctx.author.mention))
        else:
            await self.bot.db.ignore.update_one({'guild_id': guild.id}, {'$push':{'roles': role.id}})
            await ctx.send("{} Role added to ignore list!".format(ctx.author.mention))

    @ignore.command()
    @commands.check(checks.guild)
    async def channel(self, ctx, channel: discord.TextChannel):
        """Ignores a channel in your guild."""
        guild = ctx.guild
        logs = await self.bot.db.ignore.find_one({'guild_id': guild.id})
        if not logs:
            settings = {
                "guild_id": guild.id,
                "channels" : [], 
                "users" : [], 
                "roles" : []
            }
            await self.bot.db.ignore.insert_one(settings)
        if channel.id in logs["channels"]:
            await ctx.send(":x: {} Channel is already in the ignore list!".format(ctx.author.mention))
        else:
            await self.bot.db.ignore.update_one({'guild_id': guild.id}, {'$push':{'channels': channel.id}})
            await ctx.send("{} Channel added to ignore list!".format(ctx.author.mention))

    @settings.command()
    @commands.check(checks.guild)
    async def deleteall(self, ctx):
        """This will delete all of your guilds settings."""
        logs = await self.bot.db.settings.find_one({'guild_id': ctx.guild.id})
        logs2 = await self.bot.db.settings.find_one({'guild_id': ctx.guild.id})
        confcode = "{}".format(random.randint(1000,9999))
        msg = "Please type in the confirmation code to confirm, or wait 30 seconds to cancel."
        e = discord.Embed()
        e.colour = 0x36393E
        e.description = msg
        e.title = f"Deleting Guild Settings:"
        e.add_field(name="Settings:", value=logs)
        e.add_field(name="Confirmation Code:", value=confcode)
        m = await ctx.send(embed=e)
        def a(m):
            return m.content == confcode and m.channel == ctx.channel and m.author == ctx.author
        try:
            msg = await self.bot.wait_for("message", check=a, timeout=30)
        except asyncio.TimeoutError:
            await m.delete()
            await ctx.send("Operation cancelled.")
            return
        await m.delete()
        if logs2:
            await self.bot.db.welcomer.find_one_and_delete({'guild_id': ctx.guild.id})
        if logs:
            await self.bot.db.settings.find_one_and_delete({'guild_id': ctx.guild.id})
        await ctx.send("Settings where deleted.")

    @settings.command()
    async def config(self, ctx):
        """Shows settings for the current guild."""
        guild = ctx.guild
        music = ""
        welcomer = ""
        ignore = ""
        logs = await self.bot.db.welcomer.find_one({"guild_id": guild.id})
        logs2 = await self.bot.db.settings.find_one({"guild_id": guild.id})
        logs3 = await self.bot.db.ignore.find_one({"guild_id": guild.id})
        e = discord.Embed()
        e.colour = 0x36393E
        if logs2['prefix'] is not None:
            e.add_field(name="Prefix:", value=logs2['prefix'])
        else:
            e.add_field(name="Prefix:", value="<@538344287843123205>, k., K.")
        if logs:
            try:
                if logs['userrole'] is not None:
                    userrole = discord.utils.get(ctx.guild.roles, id=logs['userrole'])
                else:
                    userrole = "None"
                if logs['botrole'] is not None:
                    botrole = discord.utils.get(ctx.guild.roles, id=logs['botrole'])
                else:
                    botrole = "None"
                if logs['message'] is not None:
                    message = logs['message']
                else:
                    message = "None"
                if logs['destination'] is None:
                    channel = f"Not setup."
                else:
                    channel = guild.get_channel(logs["destination"]).mention
                if logs['images'] == True:
                    images = "Enabled."
                else:
                    images = f"Disabled."
                welcomer += f"**Toggle:** {logs['toggle']}\n"
                welcomer += f"**Roles:** `Users:` {userrole} `Bots:` {botrole}\n"
                welcomer += f"**Message:** {message}\n"
                welcomer += f"**Images:** {images}\n"
                welcomer += f"**Destination:** {channel}"
                e.add_field(name="Welcomer Settings:", value=welcomer, inline=False)
            except:
                pass
        if logs2:
            try:
                if logs2['djrole'] is not None:
                    music += f"**DJ Role:** {logs2['djrole']}\n"
                else:
                    music += "**DJ Role:** None\n"
                e.add_field(name="Music Settings:", value=music, inline=False)
            except:
                pass
        e.set_thumbnail(url=ctx.guild.icon_url)
        e.set_author(icon_url=ctx.author.avatar_url, name=f"Current settings for {ctx.guild.name}:")
        if (music or welcomer) != "":
            await ctx.send(embed=e)
            return
        else:
            await ctx.send("<:tickred:539495579793883176> There are no settings enabled or setup for this guild.")

    @settings.group(name="welcomer")
    async def _welcomer(self, ctx):
        """Welcomer settings."""
        guild = ctx.guild
        logs = await self.bot.db.welcomer.find_one({"guild_id": guild.id})
        settings = {
            "guild_id": guild.id,
            "destination" : None, 
            "toggle" : False,
            "message": None,
            "images": False,
            "background": "data/imgwelcome/transparent.png",
            "botrole": None,
            "userrole": None
        }
        if not logs:
            await self.bot.db.welcomer.insert_one(settings)
        if ctx.invoked_subcommand is None or isinstance(ctx.invoked_subcommand, commands.Group):
            e = discord.Embed()
            e.colour = 0x36393E
            e.set_author(name="Help for Kira's command group settings welcomer.", icon_url=ctx.guild.me.avatar_url)
            e.description = "**destination -** Sets destination.\n"
            e.description += "**message -** Sets message.\n"
            e.description += "**role -** Sets the autoroles.\n"
            e.description += "**bg -** Sets welcome image background for your guild.\n"
            e.description += "**toggle -** Toggles welcomer on or off.\n"
            e.description += "**testmessage -** Sends a test message to make sure you have your settings right."
            e.set_thumbnail(url=ctx.guild.me.avatar_url)
            await ctx.send(embed=e)

    @_welcomer.command(name='bg')
    @commands.check(checks.guild)
    async def _upload(self, ctx):
        """Upload a background through Discord. 500px x 150px.
        This must be an image file and not a url."""
        guild = ctx.guild
        await ctx.send("Please send the image. Must be 500px x 150px.")
        def check(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel
        answer = await self.bot.wait_for("message", timeout=60.0, check=check)
        try:
            bg_url = answer.attachments[0].url
            success = True
        except Exception as e:
            success = False
            print(e)
        if success:
            try:
                async with self.bot.session.get(bg_url) as r:
                    image = await r.content.read()
                    if not os.path.exists('data/imgwelcome/{}'.format(guild.id)):
                        os.makedirs('data/imgwelcome/{}'.format(guild.id))
                guildbg = 'data/imgwelcome/{}/guildbg.png'.format(guild.id)
                with open(guildbg, 'wb') as f:
                    f.write(image)
                    guildimage = Image.open(guildbg).convert('RGBA')
                    success = True
            except Exception as e:
                success = False
                print(e)
            if success:
                if guildimage.size == (500, 150):
                    bg = f"data/imgwelcome/{guild.id}/guildbg.png"
                    await self.bot.db.welcomer.update_one({"guild_id": guild.id}, {"$set":{"background": bg}})
                else:
                    await ctx.send("Image needs to be 500x150.")
                    return
                background_img = ('data/imgwelcome/{}/guildbg.png'.format(guild.id))
                await self.bot.db.welcomer.update_one({"guild_id": guild.id}, {"$set":{"background": background_img}})
                await ctx.send('Welcome image for this guild set to uploaded file.')
            else:
                await ctx.send("Couldn't get the image from Discord.")
        else:
            await ctx.send("Couldn't get the image.")

    @_welcomer.command(name="role")
    @commands.check(checks.guild)
    async def _role(self, ctx, option=None, role: discord.Role=None):
        """Sets the join role for a user when they join the server."""
        guild = ctx.guild
        if option is None:
            await ctx.send(f"Please specify an option, here is an example. `{ctx.prefix}welcomer role users Users`")
            return
        if option is not None:
            if option == "users":
                if role is None:
                    await ctx.send("Please specify a role.")
                    return
                else:
                    apply = await ctx.send("<a:loading:535996854400319489> Applying to your settings....")
                    await self.bot.db.welcomer.update_one({"guild_id": guild.id}, {"$set":{"userrole": role.id}})
                    await asyncio.sleep(2)
                    await apply.edit(content=f" All done, I have applied your settings.")
                    return
            if option == "bots":
                if role is None:
                    await ctx.send("Please specify a role.")
                    return
                else:
                    apply = await ctx.send("<a:loading:535996854400319489> Applying to your settings....")
                    await self.bot.db.welcomer.update_one({"guild_id": guild.id}, {"$set":{"botrole": role.id}})
                    await asyncio.sleep(2)
                    await apply.edit(content=f" All done, I have applied your settings.")
                    return
            else:
                await ctx.send("Option must either be users or bots.")
                return


    @_welcomer.command(name="destination")
    @commands.check(checks.guild)
    async def _destination(self, ctx, channel: discord.TextChannel=None):
        """Set welcomer destination."""
        guild = ctx.guild
        logs = await self.bot.db.welcomer.find_one({"guild_id": guild.id})
        if channel is None:
            await ctx.send("<:tickNo:315009174163685377> Hey Bud! You need to specify a channel.")
            return
        if logs:
            apply = await ctx.send("<a:loading:535996854400319489> Applying log channel to your settings....")
            print(channel)
            await self.bot.db.welcomer.update_one({"guild_id": guild.id}, {"$set":{"destination": channel.id}})
            await asyncio.sleep(2)
            await apply.edit(content=f" All done, I have set the channel in your settings.")
            return
        if not logs:
            await ctx.send(f"<:uncheck:433159805117399050> Looks like we ran into an error. I have failed to make your guild settings.")
            return

    @_welcomer.command(name="toggle")
    @commands.check(checks.guild)
    async def _toggle(self, ctx, toggle=None):
        """Toggle setting for welcomer."""
        guild = ctx.guild
        logs = await self.bot.db.welcomer.find_one({"guild_id": guild.id})
        if logs:
            if toggle == "images":
                if logs['images'] is False:
                    apply = await ctx.send("<a:loading:535996854400319489> Applying to your settings....")
                    await self.bot.db.welcomer.update_one({"guild_id": guild.id}, {"$set":{"images": True}})
                    await asyncio.sleep(2)
                    await apply.edit(content=f" All done, I have set the toggle in your settings to True.")
                if logs['images'] is True:
                    apply = await ctx.send("<a:loading:535996854400319489> Applying to your settings....")
                    await self.bot.db.welcomer.update_one({"guild_id": guild.id}, {"$set":{"images": False}})
                    await asyncio.sleep(2)
                    await apply.edit(content=f" All done, I have set the toggle in your settings to False.")
            if toggle == "on":
                apply = await ctx.send("<a:loading:535996854400319489> Applying to your settings....")
                await self.bot.db.welcomer.update_one({"guild_id": guild.id}, {"$set":{"toggle": True}})
                await asyncio.sleep(2)
                await apply.edit(content=f" All done, I have set the toggle in your settings to True.")
                return
            if toggle == "off":
                apply = await ctx.send("<a:loading:535996854400319489> Applying to your settings....")
                await self.bot.db.welcomer.update_one({"guild_id": guild.id}, {"$set":{"toggle": False}})
                await asyncio.sleep(2)
                await apply.edit(content=f" All done, I have set the toggle in your settings to False.")
                return
            if toggle is None:
                await ctx.send(f"<:uncheck:433159805117399050> Please specify either on, off, or images.")
                return
        if not logs:
            await ctx.send(f"<:uncheck:433159805117399050> Looks like we ran into an error. I have failed to make your guild settings.")
            return

    @_welcomer.command()
    @commands.check(checks.guild)
    async def message(self, ctx, *, msg: str=None):
        """Sets welcome message."""
        guild = ctx.guild
        logs = await self.bot.db.welcomer.find_one({"guild_id": guild.id})
        if msg is not None:
            if logs:
                apply = await ctx.send("<a:loading:395760990689558539> Applying message to your settings....")
                await self.bot.db.welcomer.update_one({"guild_id": guild.id}, {"$set":{"message": msg}})
                await asyncio.sleep(2)
                await apply.edit(content=f"<:check:433159782287802369> All done, I have set the welcome message in your settings.")
                return
            if not logs:
                await ctx.send(f"<:uncheck:433159805117399050> Looks like we ran into an error. I have failed to make your guild settings.")
                return
        if msg is None:
            await ctx.send(f"<:uncheck:433159805117399050> {ctx.author.mention} Hey Bud! You need to specify for me to set.")
            await ctx.send("""
__**Here are some examples:**__
{0.mention} Welcome to {1.name} I hope you have a good time here!
{0.name} has now entered {1.name} there are now {1.member_count} users in the guild.

__**Tips:**__
`0` is the user/member that joined. So to get their name use `{0.name}`. If you would like to mention them use `{0.mention}`
`1` is the guild. So to get the guild name use `{1.guild}` and to get the guild member count use `{1.member_count}`.""")
            return

    @_welcomer.command(name="testmessage")
    async def _testmessage(self, ctx):
        """Sends a test message to make sure your welcomer settings a right."""
        guild = ctx.guild
        author = ctx.author
        logs = await self.bot.db.welcomer.find_one({"guild_id": guild.id})
        if logs:
            destination = logs["destination"]
            wmessage = logs["message"]
            images = logs['images']
            if wmessage is None:
                await ctx.send("<:uncheck:433159805117399050> Hey Bud! How are you going to test your message when you don't even have one?")
                return
            e = discord.Embed()
            e.colour = author.colour
            e.description = "__**Here is a preview of your message for when a user joins your server:**__\n\n"
            e.description += wmessage.format(author, guild)
            try:
                lchannel = guild.get_channel(destination)
                e.set_author(name=f"\nWelcome messages will be sent to {lchannel} channel.", icon_url="https://cdn.discordapp.com/emojis/433159782287802369.png?v=1")
            except:
                pass
            if images is True:
                e.description += "\n\n__**And here is a preview of the welcome image that will be attached to your message.**__"
                member = ctx.author
                image_object = await self._create_welcome(member, url=member.avatar_url)
                image = discord.File(image_object, filename="welcome.png")
                e.set_image(url="attachment://welcome.png")
                await ctx.send(file=image, embed=e)
                return
            else:
                await ctx.send(embed=e)
        else:
            await ctx.send("<:uncheck:433159805117399050> Hey Bud! Setup welcomer first.")
            return

    @settings.group()
    async def banlist(self, ctx):
        """Dev settings for Kira."""
        guild = ctx.guild
        logs = await self.bot.db.banlist.find_one({'kira_id': guild.me.id})
        if not logs:
            settings = {
                "kira_id": guild.me.id
            }
            await self.bot.db.banlist.insert_one(settings)
        if ctx.invoked_subcommand is None or isinstance(ctx.invoked_subcommand, commands.Group):
            e = discord.Embed()
            e.colour = 0x36393E
            e.set_author(name="Help for Kira's command group settings banlist.", icon_url=ctx.guild.me.avatar_url)
            e.description = "**commit -** Adds a discord user to Kira's banlist.\n"
            e.description += "**uncommit -** Removes a discord user from Kira's banlist.\n"
            e.description += "**users -** Shows the current users in Kira's banlist.\n"
            e.set_thumbnail(url=ctx.guild.me.avatar_url)
            await ctx.send(embed=e)

    @banlist.command()
    async def users(self, ctx):
        """Shows the current users in Kira's banlist."""
        guild = ctx.guild
        logs = await self.bot.db.banlist.find_one({'kira_id': guild.me.id})
        if not logs:
            await ctx.send("<:tickred:539495579793883176> Seems like I can't find the banlist database.")
        else:
            msg = ""
            number = 0
            for key, val in logs.items():
                if "_id" in key:
                    continue
                number += 1
                user = await self.bot.http.get_user_info(key)
                name = user['username']
                discrim = user['discriminator']
                uid = user['id']
                msg += f"`{number})` {name}#{discrim}({uid})\n**Reason:** {val['reason']}\n\n"
            e = discord.Embed()
            e.colour = 0x36393E
            e.title = "Users in Kira's Banlist:"
            if msg == "":
                e.description = "There are no users currently banned."
            else:
                e.description = msg
            await ctx.send(embed=e)
            return

    @banlist.command()
    @commands.check(checks.is_owner)
    async def commit(self, ctx, uid, *, reason: str):
        """Adds a discord user to Kira's banlist."""
        guild = ctx.guild
        logs = await self.bot.db.banlist.find_one({'kira_id': guild.me.id})
        if logs:
            if uid in logs:
                await ctx.send("<:tickred:539495579793883176> Seems like that user is already banned.")
                return
            else:
                hm = {uid:{"reason": reason}}
                await self.bot.db.banlist.update_one({"kira_id": guild.me.id}, {"$set": hm})
                await ctx.send("Added the user the banlist.")
                return
        else:
            await ctx.send("<:tickred:539495579793883176> Seems like I can't find the banlist database.")

    @banlist.command()
    @commands.check(checks.is_owner)
    async def uncommit(self, ctx, *, uid):
        """Removes a discord user to Kira's banlist."""
        guild = ctx.guild
        logs = await self.bot.db.banlist.find_one({'kira_id': guild.me.id})
        if logs:
            if uid in logs:
                hm = logs[uid]
                await self.bot.db.banlist.update_one({"kira_id": guild.me.id}, {"$unset": {uid: hm}})
                await ctx.send("Removed the user from the banlist.")
                return
            else:
                await ctx.send("<:tickred:539495579793883176> Seems like that user is not banned.")
                return
        else:
            await ctx.send("<:tickred:539495579793883176> Seems like I can't find the banlist database.")            

    @settings.group()
    async def music(self, ctx):
        """Setup music settings for your guild."""
        guild = ctx.guild
        logs = await self.bot.db.settings.find_one({'guild_id': guild.id})
        if not logs:
            welp = {
                "guild_id": guild.id,
                "prefix" : None,
                "djrole": None,
                "announce_channel": None,
                "mchnl": False,
                "toggle": False,
                "channelid": None
            }
            await self.bot.db.settings.insert_one(welp)
        if ctx.invoked_subcommand is None or isinstance(ctx.invoked_subcommand, commands.Group):
            e = discord.Embed()
            e.colour = 0x36393E
            e.set_author(name="Help for Kira's command group settings music.", icon_url=ctx.guild.me.avatar_url)
            e.description = "**djrole -** Setup a DJ role for your guild.\n"
            e.description += "**channel -** Setup a music channel for your guild."
            await ctx.send(embed=e)

    @music.command()
    @commands.check(checks.guild)
    async def djrole(self, ctx, role: discord.Role):
        """Setup a DJ role for your guild."""
        guild = ctx.guild
        logs = await self.bot.db.settings.find_one({'guild_id': guild.id})
        if not logs:
            welp = {
                "guild_id": guild.id,
                "prefix" : None,
                "djrole": None,
                "mchnl": False,
                "toggle": False,
                "channelid": None
            }
            await self.bot.db.settings.insert_one(welp)
        await self.bot.db.settings.update_one({'guild_id': guild.id}, {'$set':{'djrole': role.id}})
        await ctx.send("Done, I have set your custom DJ Role!")
        return

    @music.command(name="channel")
    @commands.check(checks.guild)
    async def _channel(self, ctx, toggle=None):
        """Enables musicchannel."""
        guild = ctx.guild
        logs = await self.bot.db.settings.find_one({'guild_id': guild.id})
        if not logs:
            welp = {
                "guild_id": guild.id,
                "prefix" : None,
                "djrole": None,
                "mchnl": False,
                "toggle": False,
                "channelid": None
            }
            await self.bot.db.settings.insert_one(welp)
        if toggle is None:
            await ctx.send("Please use this format. `..settings musicchannel on/off/info`")
            return
        if toggle == "info":
            msg = """
Here is some information on Music Channel before I enable it.
Music channel is a new function on Kira that allows more user friendly functionality.
Anyways, this allows you to just type messages like `skip`, `np`, and `queue`.
Another thing you can do is send a link like `https://www.youtube.com/watch?v=0m3kt5kLKkM`  without having to type `..play` and Kira will play a song."""
            await ctx.send(msg)
            await self.bot.db.settings.update_one({'guild_id': guild.id}, {'$set':{'mchnl': False}})
            return
        if toggle == "on":
            msg = await ctx.send("<a:loading:535996854400319489> Creating channel....")
            musicchannel = await ctx.guild.create_text_channel(name="music_channel")
            await msg.edit(content="<a:loading:535996854400319489> Applying music channel to enabled in guild settings...")
            await self.bot.db.settings.update_one({'guild_id': guild.id}, {'$set':{'toggle': True}})
            await msg.edit(content="<a:loading:535996854400319489> Applying channel id to guild settings....")
            await self.bot.db.settings.update_one({'guild_id': guild.id}, {'$set':{"channelid": musicchannel.id}})
            await msg.edit(content="<:check:534931851660230666> All done, everything is set, now all you need to do is move the channel to the correct catagory you want it in. Also you can rename the channel if you want.")
            return
        if toggle == "off":
            msg = await ctx.send("<a:loading:535996854400319489> Deleting channel....")
            await ctx.guild.get_channel(logs['channelid']).delete()
            await msg.edit(content="<a:loading:535996854400319489> Applying music channel to disabled in guild settings...")
            await self.bot.db.settings.update_one({'guild_id': guild.id}, {'$set':{'toggle': False}})
            await msg.edit(content="<:check:534931851660230666> All set, all done. Gg mate. I have disabled `musicchannel`.")
            return

    async def _create_welcome(self, member, url):
        guild = member.guild
        logs = await self.bot.db.welcomer.find_one({'guild_id': guild.id})
        members = sorted(guild.members, key=lambda m: m.joined_at).index(member) + 1
        if logs:
            wfont = "data/imgwelcome/fonts/UniSansHeavy.otf"
            welcome_font = ImageFont.truetype(wfont, 20)
            guild_font = ImageFont.truetype(wfont, 20)
            name_font = ImageFont.truetype(wfont, 20)
            background = Image.open(logs['background']).convert('RGBA')
            no_profile_picture = Image.open("data/imgwelcome/noimage.png")
            global welcome_picture
            welcome_picture = Image.new("RGBA", (500, 150))
            welcome_picture = ImageOps.fit(background, (500, 150), centering=(0.5, 0.5))
            welcome_picture.paste(background)
            welcome_picture = welcome_picture.resize((500, 150), Image.NEAREST)
            profile_area = Image.new("L", (512, 512), 0)
            draw = ImageDraw.Draw(profile_area)
            draw.ellipse(((0, 0), (512, 512)), fill=255)
            circle_img_size = tuple([111, 111])
            profile_area = profile_area.resize((circle_img_size), Image.ANTIALIAS)
            try:
                url = url.replace('webp?size=1024', 'png')
                url = url.replace('gif?size=1024', 'png')
                await self._get_profile(url)
                profile_picture = Image.open('data/imgwelcome/profilepic.png')
            except:
                profile_picture = no_profile_picture
            profile_area_output = ImageOps.fit(profile_picture, (circle_img_size), centering=(0, 0))
            profile_area_output.putalpha(profile_area)
            bordercolor = tuple([255, 255, 255, 230])
            fontcolor = tuple([255, 255, 255, 230])
            guildcolor = tuple([255, 255, 255, 230])
            textoutline = tuple([0, 0, 0, 255])
            mask = Image.new('L', (512, 512), 0)
            draw_thumb = ImageDraw.Draw(mask)
            draw_thumb.ellipse((0, 0) + (512, 512), fill=255, outline=0)
            circle = Image.new("RGBA", (512, 512))
            draw_circle = ImageDraw.Draw(circle)
            draw_circle.ellipse([0, 0, 512, 512], fill=(bordercolor[0], bordercolor[1], bordercolor[2], 180), outline=(255, 255, 255, 250))
            circle_border_size = await self._circle_border(circle_img_size)
            circle = circle.resize((circle_border_size), Image.ANTIALIAS)
            circle_mask = mask.resize((circle_border_size), Image.ANTIALIAS)
            circle_pos = (7 + int((136 - circle_border_size[0]) / 2))
            border_pos = (11 + int((136 - circle_border_size[0]) / 2))
            drawtwo = ImageDraw.Draw(welcome_picture)
            welcome_picture.paste(circle, (circle_pos, circle_pos), circle_mask)
            welcome_picture.paste(profile_area_output, (border_pos, border_pos), profile_area_output)
            uname = (str(member.name) + "#" + str(member.discriminator))
            def _outline(original_position: tuple, text: str, pixel_displacement: int, font, textoutline):
                op = original_position
                pd = pixel_displacement
                left = (op[0] - pd, op[1])
                right = (op[0] + pd, op[1])
                up = (op[0], op[1] - pd)
                down = (op[0], op[1] + pd)
                drawtwo.text(left, text, font=font, fill=(textoutline))
                drawtwo.text(right, text, font=font, fill=(textoutline))
                drawtwo.text(up, text, font=font, fill=(textoutline))
                drawtwo.text(down, text, font=font, fill=(textoutline))
                drawtwo.text(op, text, font=font, fill=(textoutline))
            _outline((150, 16), "Welcome", 1, welcome_font, (textoutline))
            drawtwo.text((150, 16), "Welcome", font=welcome_font, fill=(fontcolor))
            if len(uname) <= 17:
                _outline((152, 63), uname, 1, name_font, (textoutline))
                drawtwo.text((152, 63), uname, font=name_font, fill=(fontcolor))
            if len(uname) > 17:
                if len(uname) <= 23:
                    _outline((152, 66), uname, 1,  name_font, (textoutline))
                    drawtwo.text((152, 66), uname, font=name_font, fill=(fontcolor))
            if len(uname) >= 24:
                if len(uname) <= 32:
                    _outline((152, 70), uname, 1,  name_font, (textoutline))
                    drawtwo.text((152, 70), uname, font=name_font, fill=(fontcolor))
            if len(uname) >= 33:
                _outline((152, 73), uname, 1,  name_font, (textoutline))
                drawtwo.text((152, 73), uname, font=name_font, fill=(fontcolor))
            member_number = str(members) + self._get_suffix(members)
            sname = str(member.guild.name) + '!' if len(str(member.guild.name)) <= 28 else str(member.guild.name)[:23] + '...'
            _outline((152, 96), "You are the " + str(member_number) + " member", 1, guild_font, (textoutline))
            drawtwo.text((152, 96), "You are the " + str(member_number) + " member", font=guild_font, fill=(guildcolor))
            _outline((152, 116), 'of ' + sname, 1, guild_font, (textoutline))
            drawtwo.text((152, 116), 'of ' + sname, font=guild_font, fill=(guildcolor))
            image_object = BytesIO()
            print(image_object)
            welcome_picture.save(image_object, format="PNG")
            image_object.seek(0)
            return image_object

    def _get_suffix(self, num):
        suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
        if 10 <= num % 100 <= 20:
            suffix = 'th'
        else:
            suffix = suffixes.get(num % 10, 'th')
        return suffix

    async def _get_profile(self, url):
        async with self.bot.session.get(url) as r:
            image = await r.content.read()
        with open('data/imgwelcome/profilepic.png', 'wb') as f:
            f.write(image)

    async def _circle_border(self, circle_img_size: tuple):
        border_size = []
        for i in range(len(circle_img_size)):
            border_size.append(circle_img_size[0] + 8)
        return tuple(border_size)

    @commands.Cog.listener()
    async def on_member_join(self, member : discord.Member):
        """Join message funtion."""
        guild = member.guild
        logs = await self.bot.db.welcomer.find_one({"guild_id": guild.id})
        if logs:
            toggle = logs["toggle"]
            destination = logs["destination"]
            message = logs["message"]
            botrole = logs['botrole']
            userrole = logs['userrole']
            if toggle is True:
                if userrole is not None:
                    try:
                        role = discord.utils.get(guild.roles, id=userrole)
                        await member.add_roles(role)
                    except:
                        pass
                if member.bot:
                    if botrole is not None:
                        try:
                            role = discord.utils.get(guild.roles, id=botrole)
                            await member.add_roles(role)
                        except:
                            pass
                if destination is not None:
                    channel = guild.get_channel(destination)
                    if logs['images'] is True:
                        image_object = await self._create_welcome(member, url=member.avatar_url)
                        await channel.send(content=message.format(member, guild), file=discord.File(image_object, filename="welcome.png"))
                    else:
                        await channel.send(message.format(member, guild))
                print("Toggle True: {0.name} Joined guild {1.name}".format(member, guild))
                return
            if toggle is not True:
                print("Toggle False: {0.name} Joined guild {1.name}".format(member, guild))
                return

def setup(bot):
    bot.add_cog(Settings(bot))
