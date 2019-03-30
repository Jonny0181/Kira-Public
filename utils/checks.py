async def is_owner(ctx):
    if ctx.author.id == ctx.bot.config['ownerid']:
        return True
    else:
        await ctx.send("<:tickred:539495579793883176> Command is locked to developers, sorry.", delete_after=10)
        return False

async def is_nsfw(ctx):
    try:
        if ctx.channel.is_nsfw() == True:
            return True
        else:
            await ctx.send("<:tickred:539495579793883176> Nice try you perv. This isn't a NSFW channel.", delete_after=10)
            return False
    except:
        return True

async def can_embed(ctx):
    try:
        if (ctx.guild.me.permissions_in(ctx.channel).attach_files and ctx.guild.me.permissions_in(ctx.channel).embed_links) is True:
            return True
        else:
            await ctx.send("<:tickred:539495579793883176> I can't embed links or send files. Please fix permissions and try again.", delete_after=10)
            return False
    except:
        return True

async def kick(ctx):
    try:
        if (ctx.author.permissions_in(ctx.channel).kick_members and ctx.guild.me.permissions_in(ctx.channel).kick_members) is True:
            return True
        else:
            await ctx.send("<:tickred:539495579793883176> Either you or me do not have the `kick_members` permission. Please fix permissions and try again.", delete_after=10)
            return False
    except:
        return True

async def ban(ctx):
    try:
        if (ctx.author.permissions_in(ctx.channel).ban_members and ctx.guild.me.permissions_in(ctx.channel).ban_members) is True:
            return True
        else:
            await ctx.send("<:tickred:539495579793883176> Either you or me do not have the `ban_members` permission. Please fix permissions and try again.", delete_after=10)
            return False
    except:
        return True

async def delete(ctx):
    try:
        if (ctx.author.permissions_in(ctx.channel).manage_messages and ctx.guild.me.permissions_in(ctx.channel).manage_messages) is True:
            return True
        else:
            await ctx.send("<:tickred:539495579793883176> Either you or me do not have the `manage_messages` permission. Please fix permissions and try again.", delete_after=10)
            return False
    except:
        return True

async def guild(ctx):
    try:
        if (ctx.author.permissions_in(ctx.channel).manage_guild and ctx.guild.me.permissions_in(ctx.channel).manage_guild) is True:
            return True
        else:
            await ctx.send("<:tickred:539495579793883176> Either you or me do not have the `manage_guild` permission. Please fix permissions and try again.", delete_after=10)
            return False
    except:
        return True

async def role(ctx):
    try:
        if (ctx.author.permissions_in(ctx.channel).manage_roles and ctx.guild.me.permissions_in(ctx.channel).manage_roles) is True:
            return True
        else:
            await ctx.send("<:tickred:539495579793883176> Either you or me do not have the `manage_roles` permission. Please fix permissions and try again.", delete_after=10)
            return False
    except:
        return True

async def in_voice(ctx):
    if ctx.author.voice:
        if ctx.guild.me.voice:
            if ctx.author.voice.channel != ctx.guild.me.voice.channel:
                await ctx.send("<:tickred:539495579793883176> You must be in **my** voice channel to use the command.", delete_after=10)
                return False
            else:
                return True
        else:
            return True
    else:
        await ctx.send("<:tickred:539495579793883176> You must be in a voice channel to use the command.", delete_after=10)
        return False
