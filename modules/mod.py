import discord
import random
import asyncio
import datetime
from datetime import timedelta
from discord.ext import commands
from utils import checks
from utils.mod import mass_purge, slow_deletion

class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def format_mod_embed(self, ctx, user, success, method):
        '''Helper function to format an embed to prevent extra code'''
        em = discord.Embed()
        em.colour = 0x36393E
        em.set_author(name=method.title(), icon_url=user.avatar_url)
        em.set_footer(text='User ID: {}'.format(user.id))
        if success:
            if method == 'ban' or method == 'unban':
                em.description = '{} was just {}ned.'.format(user, method)
            else:
                em.description = '{} was just {}d.'.format(user, method)
        else:
            em.description = 'You do not have the permissions to {} users.'.format(method)

        return em

    def _role_from_string(self, guild, rolename, roles=None):
        if roles is None:
            roles = guild.roles
        role = discord.utils.find(lambda r: r.name.lower() == rolename.lower(),
                                  roles)
        return role

    @commands.command()
    @commands.guild_only()
    async def clean(self, ctx):
        """Clean bot messages and command messages."""
        logs = await self.bot.db.settings.find_one({"guild_id": ctx.guild.id})
        can_mass_purge = ctx.channel.permissions_for(ctx.guild.me).manage_messages
        await ctx.channel.purge(limit=100, check=lambda m: m.author == ctx.bot.user, before=ctx.message, after=datetime.datetime.now() - timedelta(days=14), bulk=can_mass_purge)
        try:
            await ctx.channel.purge(limit=100, check=lambda m: (m.content.startswith("k.") or m.content.startswith("k!") or m.content.startswith(str(logs['prefix']))), before=ctx.message, after=datetime.datetime.now() - timedelta(days=14), bulk=can_mass_purge)
        except:
            pass
        await ctx.message.add_reaction('\u2705')

    @commands.command()
    @commands.guild_only()
    @commands.check(checks.guild)
    @commands.check(checks.kick)
    async def voicekick(self, ctx, member: discord.Member):
        """Kick a member from voice chat"""
        if member.voice is not None:
            kick_channel = await ctx.guild.create_voice_channel(name=self.bot.user.name)
            await member.move_to(kick_channel)
            await kick_channel.delete()
            await ctx.send("{0.name} has been kicked from voice".format(member))
        else:
            await ctx.send("{0.name} is not in a voice channel".format(member))

    @commands.command()
    @commands.guild_only()
    @commands.check(checks.role)
    async def addrole(self, ctx, role: discord.Role, user : discord.Member=None):
        """Adds a role to a user."""
        if user is None:
            user = ctx.author
        try:
            await user.add_roles(role)
            await ctx.send('<:check:534931851660230666> Added role {} to {}'.format(role.name, user.name))
        except discord.errors.Forbidden:
            await ctx.send("<:notdone:334852376034803714> I don't have `manage_roles` permissions!")

    @commands.command(aliases=['bc'])
    @commands.check(checks.delete)
    @commands.guild_only()
    async def botclean(self, ctx, amount: int=100):
        """Deletes messages from bots in a channel"""
        def is_bot(m):
            return m.author.bot
        try:
            await ctx.channel.purge(limit=amount, check=is_bot)
        except discord.HTTPException:
            await ctx.send("The bot is missing permissions to delete messages.")

    @commands.command()
    @commands.guild_only()
    @commands.check(checks.kick)
    async def kick(self, ctx, member : discord.Member, *, reason : str = "[No reason specified]"):
        """Kick a user from your guild."""
        reason = "[{}] {}".format(str(ctx.author), reason)
        if member.top_role.position >= ctx.author.top_role.position:
            await ctx.send("I can't do this.")
            return
        if member == ctx.guild.owner:
            await ctx.send("I can't do this.")
            return
        if member == ctx.me:
            await ctx.send("I can't do this.")
            return
        confcode = "{}".format(random.randint(1000,9999))
        msg = "Please type in the confirmation code to confirm and kick this user, or wait 30 seconds to cancel."
        e = discord.Embed()
        e.colour = 0x36393E
        e.description = msg
        e.title = f"Kicking user {str(member)}:"
        e.add_field(name="Reason:", value=reason)
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
        try:
            await ctx.guild.kick(member, reason=reason)
            await ctx.send("User {} was successfully kicked.".format(str(member)))
        except (discord.HTTPException, discord.Forbidden) as e:
            await ctx.send("I couldn't kick the user. Have you checked I have the proper permissions and that my role is higher than the user you want to kick?")

    @commands.command()
    @commands.guild_only()
    @commands.check(checks.ban)
    async def ban(self, ctx, member : discord.Member, *, reason : str = "[No reason specified]"):
        """Ban a user from your guild."""
        reason = "[{}] {}".format(str(ctx.author), reason)
        if member.top_role.position >= ctx.author.top_role.position:
            await ctx.send("I can't do this.")
            return
        if member == ctx.guild.owner:
            await ctx.send("I can't do this.")
            return
        if member == ctx.me:
            await ctx.send("I can't do this.")
            return
        confcode = "{}".format(random.randint(1000,9999))
        msg = "Please type in the confirmation code to confirm and ban this user, or wait 30 seconds to cancel."
        e = discord.Embed()
        e.colour = 0x36393E
        e.description = msg
        e.title = f"Banning user {str(member)}:"
        e.add_field(name="Reason:", value=reason)
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
        try:
            await ctx.guild.ban(member, reason=reason, delete_message_days=7)
            await ctx.send("User {} was successfully banned.".format(str(member)))
        except (discord.HTTPException, discord.Forbidden) as e:
            await ctx.send("I couldn't ban the user. Have you checked I have the proper permissions and that my role is higher than the user you want to ban?")

    @commands.command()
    @commands.guild_only()
    @commands.check(checks.ban)
    async def hackban(self, ctx, userid, *, reason : str = "[No reason specified]"):
        """Hackban a user from your guild."""
        reason = "[{}] {}".format(str(ctx.author), reason)
        user = discord.Object(id=userid)
        try:
            name = await self.bot.http.get_user_info(userid)
        except:
            await ctx.send("User not found.")
            return
        confcode = "{}".format(random.randint(1000,9999))
        msg = "Please type in the confirmation code to confirm and ban this user, or wait 30 seconds to cancel."
        e = discord.Embed()
        e.colour = 0x36393E
        e.description = msg
        e.title = f"Banning user {str(user)}:"
        e.add_field(name="Reason:", value=reason)
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
        try:
            await ctx.guild.ban(user)
            await ctx.send(f"User {name['username']} was successfully banned.")
        except (discord.HTTPException, discord.Forbidden) as e:
            await ctx.send("I couldn't ban the user. Have you checked I have the proper permissions and that my role is higher than the user you want to ban?")

    @commands.command()
    @commands.guild_only()
    @commands.check(checks.ban)
    async def softban(self, ctx, member : discord.Member, *, reason : str = "[No reason specified]"):
        """Softban a user from your guild."""
        reason = "[{}] {}".format(str(ctx.author), reason)
        if member.top_role.position >= ctx.author.top_role.position:
            await ctx.send("I can't do this.")
            return
        if member == ctx.guild.owner:
            await ctx.send("I can't do this.")
            return
        if member == ctx.me:
            await ctx.send("I can't do this.")
            return
        confcode = "{}".format(random.randint(1000,9999))
        msg = "Please type in the confirmation code to confirm and softban this user, or wait 30 seconds to cancel."
        e = discord.Embed()
        e.colour = 0x36393E
        e.description = msg
        e.title = f"Soft Banning user {str(member)}:"
        e.add_field(name="Reason:", value=reason)
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
        try:
            await ctx.guild.ban(member, reason=reason, delete_message_days=7)
            await ctx.guild.unban(member, reason=reason)
            await ctx.send("User {} was successfully softbanned.".format(str(member)))
        except (discord.HTTPException, discord.Forbidden) as e:
            await ctx.send("I couldn't softban the user. Have you checked I have the proper permissions and that my role is higher than the user you want to softban?")

    @commands.command()
    @commands.guild_only()
    @commands.check(checks.guild)
    async def mute(self, ctx, user: discord.Member):
        """Mute someone from the channel"""
        try:
            await ctx.channel.set_permissions(user, send_messages=False)
        except:
            success=False
        else:
            success=True

        em=self.format_mod_embed(ctx, user, success, 'mute')
        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @commands.check(checks.delete)
    async def prune(self, ctx: commands.Context, number: int):
        """Prunes messages from the channel."""
        channel = ctx.channel
        author = ctx.author

        is_bot = self.bot.user.bot

        to_delete = []
        tmp = ctx.message

        done = False

        while len(to_delete) - 1 < number and not done:
            async for message in channel.history(limit=1000, before=tmp):
                if len(to_delete) - 1 < number and \
                        (ctx.message.created_at - message.created_at).days < 14:
                    to_delete.append(message)
                elif (ctx.message.created_at - message.created_at).days >= 14:
                    done = True
                    break
                tmp = message
        if is_bot:
            await mass_purge(to_delete, channel)
        else:
            await slow_deletion(to_delete)

    @commands.command()
    @commands.guild_only()
    @commands.check(checks.guild)
    async def unmute(self, ctx, user: discord.Member):
        """Unmute someone from the channel"""
        try:
            await ctx.channel.set_permissions(user, send_messages=True)
        except:
            success=False
        else:
            success=True

        em= self.format_mod_embed(ctx, user, success, 'unmute')
        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Mod(bot))
