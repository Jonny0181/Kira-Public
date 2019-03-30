import discord
import asyncio
from dhooks import Webhook
from discord.ext import commands

class Test(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hook = Webhook('https://discordapp.com/api/webhooks/541451681490272256/xR2ev6hNS_zdBX7bfT8vESQ0AlIti6vIpajKD_UoKVpKbysQZuV8khBdP_aEL4z9Hp5u')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        guildid = 538770375266533408
        roleid = 561076933920817162
        channelid = 541560087848681475
        msgid = 561079911557890048
        if payload.guild_id == 336642139381301249:
            channel = 381963689470984203
            schannel = self.bot.get_channel(channel)
            if payload.channel_id == channel:
                print(dir(payload))
                if payload.user_id == 170619078401196032:
                    if payload.emoji.name == "✔":
                        await schannel.send('Now get the guild object.', delete_after=5)
                        guild = self.bot.get_guild(guildid)
                        await schannel.send('got the guild, now just get the user.', delete_after=5)
                        user = guild.get_member(payload.user_id)
                        await schannel.send('Got the user, now just get the role.', delete_after=5)
                        role = guild.get_role(roleid)
                        await schannel.send('Got the role, now just add it to the user.', delete_after=5)
                        await user.add_roles(role)
                        await schannel.send('Added the role!', delete_after=5)
                        return
                return
        else:
            return
        
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if not payload.guild_id:
            return
        if payload.guild_id == 336642139381301249:
            channel = 381963689470984203
            schannel = self.bot.get_channel(channel)
            if payload.channel_id == channel:
                print(payload.emoji)
                print(payload.emoji.name)
                print(payload.user_id)
                print(dir(payload.emoji))
                if payload.user_id == 170619078401196032:
                    if payload.emoji.name == "💩":
                        await schannel.send('Meep2', delete_after=5)
                        return
                return
        else:
            return
        
    @commands.command()
    async def webhooktest(self, ctx):
        """Test command."""
        server = ctx.guild
        embed = discord.Embed()
        embed.colour = ctx.author.colour
        embed = discord.Embed(title="Server Info for {}".format(server.name), colour=0xffa500)
        embed.set_footer(text=("Server created at: " + server.created_at.strftime("%d %B, %Y at %H:%M:%S%P")))
        embed.add_field(name="ID", value=server.id)
        def Roles(server):
            counter = 0
            for role in server.roles:
                if role.name == "@everyone":
                    continue
                counter += 1
            return str(counter)
        def Bots(server):
            count = 0
            for member in server.members:
                if member.bot:
                    count += 1
                else:
                    continue
            return str(count)
        embed.add_field(name="Role Count", value=Roles(server))
        embed.add_field(name="Owner", value="{} {}".format(str(server.owner), server.owner.id))
        embed.add_field(name="Region", value=server.region)
        embed.add_field(name="Member Count", value=server.member_count)
        embed.add_field(name="Bot Count", value=Bots(server))
        embed.add_field(name="Text Channel Count", value=str(len(server.text_channels)))
        embed.add_field(name="Voice Channel Count", value=str(len(server.voice_channels)))
        embed.add_field(name="Total Channel Count", value=str(len(server.channels)))
        if server.icon_url:
            embed.set_thumbnail(url=server.icon_url)
            embed.add_field(name="Avatar URL", value=server.icon_url)
        self.hook.send(embed=embed)

def setup(bot):
    n = Test(bot)
    bot.add_cog(n)
