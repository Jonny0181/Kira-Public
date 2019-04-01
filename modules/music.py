import asyncio
import heapq
import math
import re
import time
import discord
import lavalink
from discord.ext import commands
from datetime import datetime
from utils import checks

CCYAN = '\33[36m'
CGREEN = '\33[32m'
CYELLOW = '\33[33m'
CRED = '\33[31m'
CEND = '\33[0m'

time_rx = re.compile('[0-9]+')
url_rx = re.compile(r'https?:\/\/(?:www\.)?.+')

__version__ = "2.0.2.9.a"

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = {"spotify_client_id": "51f8615447044a8bb0068c0c61d16ec1", "spotify_client_secret": "922bbdd2eafb4cd5a4631935f7d0c2a8"}
        self.spotify_token = None
        self.play_lock = []
        self.disconnect_timer = []
        if not hasattr(bot, 'lavalink'):
            lavalink.Client(bot=bot, password='youshallnotpass', ws_port=2333, loop=self.bot.loop)
            self.bot.lavalink.register_hook(self.track_hook)

    def cog_unload(self):
        ids = []
        for guild_id, player in self.bot.lavalink.players:
            self.bot.loop.create_task(player.disconnect())
            player.cleanup()
            ids.append(guild_id)
        print(f"{CYELLOW}Disconnected from {len(ids)} voice clients..{CEND}")
        # Clear the players from Lavalink's internal cache
        self.play_lock.clear()

    async def cog_check(self, ctx):
        guild = ctx.guild
        author = ctx.author
        data = await self.bot.db.settings.find_one({'guild_id': guild.id})
        try:
            if data:
                if data['djrole'] is not None:
                    roles = [e.id for e in author.roles]
                    role = data['djrole']
                    if role in roles:
                        return True
                    else:
                        await ctx.send("<:tickred:539495579793883176> I'm sorry but it seem like you don't have the DJ role. I cannot allow you to do this.", delete_after=5)
                        return False
                else:
                    return True
            else:
                return True
        except:
            return True

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        player = self.bot.lavalink.players.get(member.guild.id)
        c = player.fetch('channel')
        m = player.fetch('disconnect_message')
        if c:
            c = self.bot.get_channel(c)
        else:
            return
        if player.is_connected == True:
            channel = player.connected_channel
            if channel is before.channel or after.channel:
                members = len(member.guild.me.voice.channel.members)
                if members > 1:
                    if m:
                        try:
                            await m.delete()
                        except:
                            pass
                        hmok = await c.send('Users are back in the voice channel, looks like I\'m not disconnecting. <a:miyano_trippin:532417746248531968>')
                        if member.guild.id in self.disconnect_timer:
                            self.disconnect_timer.remove(member.guild.id)
                        await asyncio.sleep(5)
                        await hmok.delete()
                        player.delete('disconnect_message')
                        return
                    else:
                        if member.guild.id in self.disconnect_timer:
                            self.disconnect_timer.remove(member.guild.id)
                        return
                if members == 1:
                    msg = await c.send('I will be leaving the voice channel in 1 minute unless someone joins back... <a:pepesip:535774588588654592>')
                    self.disconnect_timer.append(member.guild.id)
                    player.store('disconnect_message', msg)
                    await asyncio.sleep(7)
                    try:
                        await msg.delete()
                    except:
                        return
                    await asyncio.sleep(53)
                    if member.guild.id in self.disconnect_timer:
                        members = len(member.guild.me.voice.channel.members)
                        if members > 1:
                            self.disconnect_timer.remove(member.guild.id)
                            return
                        else:
                            await player.disconnect()
                            player.queue.clear()
                            self.bot.lavalink.players.remove(member.guild.id)
                            msg = await c.send("Disconnect from voice. I was the only one there! I don't want to be alone so I left! <a:Crying_Weeb:532417760441925642>")
                            return

    async def track_hook(self, event):
        if not hasattr(event, 'player'):
            return
        guild = self.bot.get_channel(event.player.fetch('channel')).guild
        player = self.bot.lavalink.players.get(guild.id)
        if isinstance(event, lavalink.Events.TrackStartEvent):
            c = event.player.fetch('channel')
            if c:
                c = self.bot.get_channel(c)
                if c:
                    try:
                        m = event.player.fetch('npmsg')
                        if m:
                            try:
                                hm = await c.fetch_message(m)
                                await hm.delete()
                                event.player.delete('npmsg')
                            except:
                                pass
                        try:
                            user = guild.get_member(player.current.requester)
                            if player.current.stream:
                                dur = 'LIVE'
                            else:
                                dur = lavalink.Utils.format_time(event.track.duration)
                            time = f"`[{dur}]`"
                            e = discord.Embed()
                            e.colour = 0x36393E
                            e.title = "Now Playing:"
                            e.description = f"<a:audiovs:483974404259446798> {event.track.title} {time}, requested by `{user.name}#{user.discriminator}`\n<{event.track.uri}>"
                            e.set_thumbnail(url=event.track.thumbnail)
                            msg = await c.send(embed=e, delete_after=15)
                            event.player.store('npmsg', msg.id)
                        except:
                            if player.current['info']['isStream']:
                                dur = 'LIVE'
                            else:
                                dur = lavalink.Utils.format_time(event.track['info']['length'])
                            dur = f"`[{dur}]`"
                            e = discord.Embed()
                            e.colour = 0x36393E
                            e.title = "Now Playing:"
                            e.description = f"<a:audiovs:483974404259446798> {event.track['info']['title']} {dur}\n<{event.track['info']['uri']}>"
                            e.set_thumbnail(url=f"https://img.youtube.com/vi/{event.track['info']['identifier']}/default.jpg")
                            msg = await c.send(embed=e, delete_after=15)
                            event.player.store('npmsg', msg.id)
                    except Exception as e:
                        print(e)
        elif isinstance(event, lavalink.Events.QueueEndEvent):
            try:
                c = event.player.fetch('channel')
                if c:
                    c = self.bot.get_channel(c)
                    if c:
                        await c.send('Queue ended! Why not queue more songs?\nWant to help support Kira? Head on over here: <https://www.patreon.com/user?u=8692289>')
                        await player.disconnect()
                        self.bot.lavalink.players.delete(guild.id)
            except:
                pass


    @commands.group(aliases=["pl"])
    @commands.guild_only()
    async def playlists(self, ctx):
        """Shows you commands for your playlists... remove the ..help at the beginning
        want to add a playlist?
        try.
        k.myplaylists add hours https://www.youtube.com/playlist?list=PLByvRxAlykqMXqz3-akzuMG4IocsqOYUn"""
        if ctx.invoked_subcommand is None:
            e = discord.Embed()
            e.colour = 0x36393E
            e.set_author(name="Help for Kira's command group myplaylists.", icon_url=ctx.guild.me.avatar_url)
            e.description = "**show - ** Lets you see your saved playlists..\n"
            e.description += "**start -** Start one of those lit playlists.\n"
            e.description += "**add -** Will add a playlist to your database.\n"
            e.description += "**del -** Will delete a playlist from your database.\n"
            e.description += "**push -** Add links to a existing playlists.\n"
            e.description += "**pull -** Remove links to a existing playlists.\n"
            e.description += "**saveq -** Saves the current player queue to a new playlist.\n"
            e.set_thumbnail(url=ctx.guild.me.avatar_url)
            await ctx.send(embed=e)

    @playlists.command()
    async def saveq(self, ctx, *, name: str):
        """Saves the queue to a new playlist in your database."""
        author = ctx.author
        settings = {
            "user_id": author.id,
        }
        data = await self.bot.db.playlists.find_one({"user_id": ctx.author.id})
        player = self.bot.lavalink.players.get(ctx.guild.id)
        links = []
        if data:
            if player.queue:
                await self.bot.db.playlists.update_one({"user_id": author.id}, {'$set': {name: []}})
                try:
                    await self.bot.db.playlists.update_one({"user_id": author.id}, {'$push': {name: player.current.uri}})
                except:
                    await self.bot.db.playlists.update_one({"user_id": author.id}, {'$push': {name: player.current['info']['uri']}})
                msg = await ctx.send(f"Saving queue to playlist **{name}**..")
                for track in player.queue:
                    try:
                        url = track.uri
                        await self.bot.db.playlists.update_one({"user_id": author.id}, {'$push': {name: url}})
                    except:
                        results = await self.bot.lavalink.get_tracks(track.replace('spotify', 'ytsearch'))
                        url = results['tracks'][0]['info']['uri']
                        await self.bot.db.playlists.update_one({"user_id": author.id}, {'$push': {name: url}})
                        await asyncio.sleep(3)
                    links.append(url)
                await msg.delete()
                await ctx.send(f"{ctx.author.mention} Done, I have created **{name}** playlist and added **{len(links)+1}** songs to the playlist.", delete_after=10)
                return
            else:
                await ctx.send("There is nothing queued to save.",delete_after=10)
                return
        else:
            if player.queue:
                msg = await ctx.send("This is your first playlist, so I'm creating your database..")
                await self.bot.db.playlists.insert_one(settings)
                await self.bot.db.playlists.update_one({"user_id": author.id}, {'$set': {name: []}})
                try:
                    await self.bot.db.playlists.update_one({"user_id": author.id}, {'$push': {name: player.current.uri}})
                except:
                    await self.bot.db.playlists.update_one({"user_id": author.id}, {'$push': {name: player.current['info']['uri']}})
                await msg.edit(content=f"Created your database, now I'm adding the queue to **{name}** playlist..")
                for track in player.queue:
                    try:
                        url = track.uri
                        await self.bot.db.playlists.update_one({"user_id": author.id}, {'$push': {name: url}})
                    except:
                        results = await self.bot.lavalink.get_tracks(track.replace('spotify', 'ytsearch'))
                        url = results['tracks'][0]['info']['uri']
                        await self.bot.db.playlists.update_one({"user_id": author.id}, {'$push': {name: url}})
                        await asyncio.sleep(3)
                    links.append(url)
                await msg.delete()
                await ctx.send(f"{ctx.author.mention} Done, I have created **{name}** playlist and added **{len(links)+1}** songs to the playlist.", delete_after=10)
                return
            else:
                await ctx.send("There is nothing queued to save.", delete_after=10)
                return

    @playlists.command()
    async def show(self, ctx, *, playlist: str=None):
        """Shows your saved playlists."""
        author = ctx.author
        settings = {
            "user_id": author.id,
        }
        data = await self.bot.db.playlists.find_one({"user_id": ctx.author.id})
        if not data:
            e = discord.Embed()
            e.colour = 0x36393E
            e.description = "Oh you don't have any playlists. You should really add some.\n\nTo add playlists use the command `k.playlists`, use this as an example `k.playlists add <name> <link>`"
            e.set_image(url="https://media.discordapp.net/attachments/381963689470984203/558170059718262799/AtEjixqNFvUVDeNSfACXACnAAn0B0EuCLsDqq8TU6AEAEOIEzhgBXhGfMUHFBOQFOgBPgBLqDAFeE3UGVt8kJcAKcACdwxhDgivC.png?width=400&height=105")
            await ctx.send(embed=e)
            return
        keys = {k:v for k,v in data.items() if not k.endswith('_id')}
        if data:
            if data == settings:
                await ctx.send("You have a database, but you don't have any playlists, use the command `k.playlists` to add some, use this as an example `k.playlists add <name> <link>")
                return
        if playlist is None:
            number = 0
            e = discord.Embed()
            e.set_author(name="Here are your playlists:", icon_url=ctx.author.avatar_url)
            e.colour = 0x36393E
            e.description = f"For more info on a playlist try {ctx.prefix}playlists show  <playlist>\n\n**Available Playlists:**\n"
            for key, val in data.items():
                if "_id" in key:
                    continue
                number += 1
                e.description += f"`{number})` {key}\n"
            if e.description == "":
                e.description = "Oh you don't have any playlists. You should really add some.\n\nTo add playlists use the command `k.playlists`, use this as an example `k.playlists add <link> <name>`"
                e.set_image(url="https://i.imgur.com/8FfFpVB.png")
            await ctx.send(embed=e)
            return
        if playlist is not None:
            if playlist not in keys:
                await ctx.send("Playlist not found in database.")
                return
            e = discord.Embed()
            e.set_author(name=f"More info on playlist {playlist}:", icon_url=ctx.author.avatar_url)
            e.add_field(name="Playlist name:", value=playlist)
            e.add_field(name="# of links:", value=len(data[playlist]))
            e.colour = 0x36393E
            if len(data[playlist]) < 10:
                e.add_field(name="Playlist links:", value="\n".join(link for link in data[playlist]), inline=False)
            elif len(data[playlist]) == 10:
                e.add_field(name="Playlist links:", value=f"I cannot show all the links.", inline=False)
            elif len(data[playlist]) > 10:
                e.add_field(name="Playlist links:", value=f"I cannot show all the links.", inline=False)
            await ctx.send(embed=e)
            return

    @playlists.command(name="start")
    @commands.check(checks.in_voice)
    async def start_(self, ctx, *, name: str=None):
        """Starts one of your custom playlists."""
        author = ctx.author
        guild = ctx.guild
        channel = ctx.channel
        data = await self.bot.db.playlists.find_one({"user_id": author.id})
        if guild.id in self.play_lock:
            await ctx.send("Please wait, you are already queueing a playlist in this server...")
            return
        if data:
            player = self.bot.lavalink.players.get(guild.id)
            if not player.is_connected:
                await player.connect(author.voice.channel.id)
                await ctx.send(f'<:check:534931851660230666> Joined {author.voice.channel.name}', delete_after=5)
            keys = {k:v for k,v in data.items() if not k.endswith('_id')}
            if name is None:
                emoji = {'cancel': '❌', 'back': '◀', 'forward': '▶', 'start': '🎵'}
                expected = ['❌', '◀', '▶', '🎵']
                pnumber = 1
                number = 0
                dta = {}
                for key, val in data.items():
                    if "_id" in key:
                        continue
                    number += 1
                    dta.update({number: {"name": key, "links": val}})
                pl = dta[pnumber]
                e = discord.Embed()
                e.colour = 0x36393E
                e.title = "Please choose a playlist:"
                e.add_field(name="Playlist name:", value=pl['name'])
                e.add_field(name="# of links:", value=len(pl['links']))
                if len(pl['links']) > 10:
                    e.add_field(name="Playlist links:", value=f"I cannot show all the links.", inline=False)
                else:
                    e.add_field(name="Playlist links:", value="\n".join(link for link in pl['links']), inline=False)
                msg = await ctx.send(embed=e)
                def check(r, u):
                    return r.message.id == msg.id and u == author
                for i in range(4):
                    await msg.add_reaction(expected[i])
                while True:
                    try:
                        (r, u) = await self.bot.wait_for('reaction_add', check=check, timeout=60.0)
                    except asyncio.TimeoutError:
                        await msg.delete()
                        await ctx.send('Timed out.', delete_after=5)
                        return
                    reacts = {v: k for k, v in emoji.items()}
                    react = reacts[r.emoji]
                    if react == "cancel":
                        await msg.delete()
                        return
                    elif react == "back":
                        pnumber = pnumber-1
                        if pnumber < 1:
                            pnumber = 1
                        pl = dta[pnumber]
                        e = discord.Embed()
                        e.colour = 0x36393E
                        e.title = "Please choose a playlist:"
                        e.add_field(name="Playlist name:", value=pl['name'])
                        e.add_field(name="# of links:", value=len(pl['links']))
                        if len(pl['links']) > 10:
                            e.add_field(name="Playlist links:", value=f"I cannot show all the links.", inline=False)
                        else:
                            e.add_field(name="Playlist links:", value="\n".join(link for link in pl['links']), inline=False)
                        await msg.edit(embed=e)
                    elif react == "forward":
                        pnumber += 1
                        if pnumber > number:
                            pnumber = number
                        if pnumber < 1:
                            number = 1
                        pl = dta[pnumber]
                        e = discord.Embed()
                        e.colour = 0x36393E
                        e.title = "Please choose a playlist:"
                        e.add_field(name="Playlist name:", value=pl['name'])
                        e.add_field(name="# of links:", value=len(pl['links']))
                        if len(pl['links']) > 10:
                            e.add_field(name="Playlist links:", value=f"I cannot show all the links.", inline=False)
                        else:
                            e.add_field(name="Playlist links:", value="\n".join(link for link in pl['links']), inline=False)
                        await msg.edit(embed=e)
                    elif react == 'start':
                        await msg.delete()
                        await ctx.invoke(self.bot.get_command('pl start'), name=pl['name'])
                        return
            if name in keys:
                self.play_lock.append(guild.id)
                await ctx.send("<a:loading:532575409506746369> Loading your playlist...", delete_after=2)
                links = []
                for link in keys[name]:
                    links.append(link)
                    if len(links) > 4:
                        if not player.is_playing:
                            await player.play()
                    if "open.spotify.com" in link:
                        link = "spotify:{}".format(re.sub(r"(http[s]?:\/\/)?(open.spotify.com)\/", "", link).replace("/", ":"))
                    if link.startswith("spotify:"):
                        parts = link.split(":")
                        if "track" in parts:
                            res = await self._make_spotify_req("https://api.spotify.com/v1/tracks/{0}".format(parts[-1]))
                            track = "spotify:{} {}".format(res["artists"][0]["name"], res["name"])
                            player.add(requester=author.id, track=track)
                            player.store('channel', channel.id)
                        elif "album" in parts:
                            link = parts[-1]
                            r = await self._make_spotify_req("https://api.spotify.com/v1/albums/{0}".format(link))
                            spotify_info = []
                            while True:
                                try:
                                    spotify_info.extend(r["tracks"]["items"])
                                except KeyError:
                                    spotify_info.extend(r["items"])
                                try:
                                    if r["next"] is not None:
                                        r = await self._make_spotify_req(r["next"])
                                        continue
                                    else:
                                        break
                                except KeyError:
                                    if r["tracks"]["next"] is not None:
                                        r = await self._make_spotify_req(r["tracks"]["next"])
                                        continue
                                    else:
                                        break
                            for i in spotify_info:
                                track = "spotify:{} {}".format(i["name"], i["artists"][0]["name"])
                                player.add(requester=author.id, track=track)
                            player.store('channel', channel.id)
                        elif "playlist" in parts:
                            link = parts[-1]
                            r = await self._make_spotify_req("https://api.spotify.com/v1/playlists/{0}/tracks".format(link))
                            spotify_info = []
                            numberoftracks = 0
                            while True:
                                try:
                                    spotify_info.extend(r["tracks"]["items"])
                                except KeyError:
                                    spotify_info.extend(r["items"])
                                try:
                                    if r["next"] is not None:
                                        r = await self._make_spotify_req(r["next"])
                                        continue
                                    else:
                                        break
                                except KeyError:
                                    if r["tracks"]["next"] is not None:
                                        r = await self._make_spotify_req(r["tracks"]["next"])
                                        continue
                                    else:
                                        break
                            for i in spotify_info:
                                numberoftracks += 1
                                link = "spotify:{} {}".format(i["track"]["name"], i["track"]["artists"][0]["name"])
                                player.add(requester=author.id, track=link)
                            player.store('channel', channel.id)
                    elif "youtube.com/playlist?list=" in link:
                        results = await self.bot.lavalink.get_tracks(link)
                        if results['loadType'] == 'PLAYLIST_LOADED':
                            tracks = results['tracks']
                            for track in tracks:
                                player.add(requester=author.id, track=track)
                            player.store('channel', channel.id)
                    else:
                        if not url_rx.match(link):
                            link = f'ytsearch:{link}'
                        results = await self.bot.lavalink.get_tracks(link)
                        if results['loadType'] == 'PLAYLIST_LOADED':
                            tracks = results['tracks']
                            for track in tracks:
                                player.add(requester=author.id, track=track)
                        else:
                            track = results['tracks'][0]
                            player.add(requester=author.id, track=track)
                            player.store('channel', channel.id)
                    await asyncio.sleep(3)
                await ctx.send("<:check:433159782287802369> Done! I have loaded your playlist!", delete_after=5)
                if not player.is_playing:
                    await player.play()
                self.play_lock.remove(guild.id)
                return
            else:
                await ctx.send("Playlist not found.", delete_after=15)
                return
        else:
            await ctx.send("You don't have a database. Why don't you make one?", delete_after=15)
            return

    @playlists.command(name="add")
    async def _add(self, ctx, link, *, name: str):
        """Add a playlists to you database.

        Try.
        k.pl add https://www.youtube.com/watch?v=ly9zUw2jVcc&list=PLQh6qjoTV_I-6SVu_gW13_4fiG3B0YhxQ Suicide Boys"""
        author = ctx.author
        settings = {
            "user_id": author.id,
        }
        data = await self.bot.db.playlists.find_one({"user_id": ctx.author.id})
        if name == "":
            await ctx.send("Playlist name cannot be empty.")
            return
        if not data:
            creating = await ctx.send("<a:loading:532575409506746369> Creating your database...")
            await self.bot.db.playlists.insert_one(settings)
            await asyncio.sleep(4)
            await creating.edit(content="<a:loading:532575409506746369> Created your database....now it's time to add your playlists to it.")
            await self.bot.db.playlists.update_one({"user_id": author.id}, {'$set': {name: []}})
            await self.bot.db.playlists.update_one({"user_id": author.id}, {'$push': {name: link}})
            await asyncio.sleep(4)
            await creating.edit(content="<:check:433159782287802369> Done! I have created your database, and added your first playlist to it! You're all set to go!")
            return
        else:
            await self.bot.db.playlists.update_one({"user_id": author.id}, {'$set': {name: []}})
            await self.bot.db.playlists.update_one({"user_id": author.id}, {'$push': {name: link}})
            await ctx.send("Added the playlist to your database!")
            return

    @playlists.command(name="push")
    async def _push(self, ctx, link, *, name: str):
        """Add links to a existing playlists."""
        author = ctx.author
        data = await self.bot.db.playlists.find_one({"user_id": ctx.author.id})
        keys = {k:v for k,v in data.items() if not k.endswith('_id')}
        if name not in keys:
            await ctx.send("Playlist not found in database.")
            return
        if data:
            await self.bot.db.playlists.update_one({"user_id": author.id}, {'$push': {name: link}})
            await ctx.send('Done, added the link to the playlist.')
            return
        else:
            await ctx.send("I'm sorry, but you don't have a playlist database.")

    @playlists.command(name="pull")
    async def _pull(self, ctx, link, *, name: str):
        """Remove links from a existing playlists."""
        author = ctx.author
        data = await self.bot.db.playlists.find_one({"user_id": ctx.author.id})
        keys = {k:v for k,v in data.items() if not k.endswith('_id')}
        if name not in keys:
            await ctx.send("Playlist not found in database.")
            return
        if data:
            await self.bot.db.playlists.update_one({"user_id": author.id}, {'$pull': {name: link}})
            await ctx.send('Done, removed the link from the playlist.')
            return
        else:
            await ctx.send("I'm sorry, but you don't have a playlist database.")

    @playlists.command(name="del")
    async def _del(self, ctx, *, name: str):
        """Deletes a playlist from your database."""
        author = ctx.author
        data = await self.bot.db.playlists.find_one({"user_id": ctx.author.id})
        keys = {k:v for k,v in data.items() if not k.endswith('_id')}
        if name not in keys:
            await ctx.send("Playlist not found in database.")
            return
        if not data:
            await ctx.send("You don't have any playlists, make one.")
        else:
            await self.bot.db.playlists.update_one({"user_id": author.id}, {"$unset":{name: keys[name]}})
            await ctx.send("Removed the playlist from your database.")

    @commands.command(name="jump")
    @commands.guild_only()
    @commands.check(checks.in_voice)
    async def _jump(self, ctx, number: int, post=True):
        """Moves song number specifed to the top of the queue."""
        guild = ctx.guild
        channel = ctx.channel
        player = self.bot.lavalink.players.get(guild.id)
        if not player.queue:
            await channel.send('Nothing queued.')
        if number > len(player.queue) or number < 1:
            await channel.send('Song number must be greater than 1 and within the queue limit.')
        bump_index = number - 1
        bump_song = self.bot.lavalink.players.get(guild.id).queue[bump_index]
        player.queue.insert(0, bump_song)
        player.queue.pop(number)
        if post is not False:
            await channel.send('<:check:433159782287802369> Moved to the top of the queue.')

    @commands.command(aliases=['dc'], name="disconnect")
    @commands.guild_only()
    @commands.check(checks.in_voice)
    async def _disconnect(self, ctx):
        """Disconnects Kira from current voice channel."""
        guild = ctx.guild
        author = ctx.author
        """Disconnect from the voice channel."""
        player = self.bot.lavalink.players.get(guild.id)
        if player.is_connected:
            if player.queue:
                try:
                    results = await self.bot.lavalink.get_tracks(player.current.uri)
                except:
                    results = await self.bot.lavalink.get_tracks(player.current['info']['uri'])
                player.add(requester=author.id, track=results['tracks'][0])
                await ctx.invoke(self.bot.get_command('jump'), number=len(player.queue), post=False)
                await player.disconnect()
                await ctx.send(f'Disconnected, queue is saved. You may use `resume` to resume queue. Use `clear` before `disconnect` next time if you don\'t want the queue to save.', delete_after=15)
            else:
                await player.disconnect()
                await ctx.send("Disconnected...", delete_after=5)
                self.bot.lavalink.players.remove(guild.id)
        else:
            await ctx.send('Not connected in this server.', delete_after=5)
            return

    @commands.check(checks.in_voice)
    @commands.guild_only()
    @commands.command(aliases=['prev'])
    async def previous(self, ctx):
        """Plays the previous song."""
        """Goes back to the previous song."""
        player = self.bot.lavalink.players.get(ctx.guild.id)
        if player.current is None:
            await ctx.send("<:tickred:539495579793883176> Nothing playing, use `play <song_name>`.")
        if player.previous:
            embed = discord.Embed(colour=0x36393E, title="Replaying Track")
            try:
                title = player.previous.title
                uri = player.previous.uri
                thumbnail = player.previous.thumbnail
                embed.add_field(name="Requested By", value=f"<@{player.previous.requester}>")
                embed.add_field(name="Stream", value=player.previous.stream)
            except:
                title = player.previous['info']['title']
                uri = player.previous['info']['uri']
                thumbnail = f"https://img.youtube.com/vi/{player.previous['info']['identifier']}/default.jpg"
            embed.description = f"{title}\n{uri}"
            embed.set_thumbnail(url=thumbnail)
            await player.play_previous()
            await ctx.send(embed=embed, delete_after=10)
        else:
            await ctx.send("There is no previous song.")
            return

    @commands.check(checks.in_voice)
    @commands.guild_only()
    @commands.command(aliases=['np', 'n', 'song'], name="now")
    async def _now(self, ctx):
        """Shows you the song currently playing."""
        emoji = {'queue': '📝', 'pause': '⏯', 'skip': '⏩', 'disconnect': '📤', 'cancel': '❌'}
        expected = ['📝', '⏯', '⏩', '📤', '❌']
        guild = ctx.guild
        player = self.bot.lavalink.players.get(guild.id)
        if player.current:
            arrow = await self._draw_time(ctx, guild)
            pos = lavalink.Utils.format_time(player.position)
            try:
                if player.current.stream:
                    dur = 'LIVE'
                else:
                    dur = lavalink.Utils.format_time(player.current.duration)
                title = player.current.title
                url = player.current.uri
                idd = player.current.identifier
            except:
                if player.current['info']['isStream']:
                    dur = 'LIVE'
                else:
                    dur = lavalink.Utils.format_time(player.current['info']['length'])
                title = player.current['info']['title']
                url = player.current['info']['uri']
                idd = player.current['info']['identifier']
        try:
            e = discord.Embed(colour=0x36393E)
            e.title = "Now Playing:"
            e.description = f"{title}\n"
            e.description += f"{arrow} `[{pos}/{dur}]`\n"
            e.description += f"{url}\n"
            e.set_thumbnail(url=f'https://img.youtube.com/vi/{idd}/hqdefault.jpg')
            message = await ctx.send(embed=e)
            def check(r, u):
                return r.message.id == message.id and u == ctx.author
            for i in range(5):
                await message.add_reaction(expected[i])
            while True:
                try:
                    (r, u) = await ctx.bot.wait_for('reaction_add', check=check, timeout=60.0)
                except asyncio.TimeoutError:
                    await message.delete()
                    return
                reacts = {v: k for k, v in emoji.items()}
                react = reacts[r.emoji]
                if react == 'queue':
                    await message.delete()
                    await ctx.invoke(self.bot.get_command('queue'))
                    return
                if react == 'pause':
                    await message.delete()
                    await ctx.invoke(self.bot.get_command('pause'))
                    return
                if react == 'skip':
                    await message.delete()
                    await ctx.invoke(self.bot.get_command('skip'))
                    return
                if react == 'disconnect':
                    await message.delete()
                    await ctx.invoke(self.bot.get_command('disconnect'))
                    return
                if react == 'cancel':
                    await message.delete()
                    return
        except Exception as e:
            print(e)
            msg = "<:tickred:539495579793883176> Nothing playing, use `play <song_name>`."
            await ctx.send(msg)

    @commands.command(aliases=['resume'], name="pause")
    @commands.guild_only()
    @commands.check(checks.in_voice)
    async def _pause(self, ctx):
        """Pauses or resumes music playback."""
        guild = ctx.guild
        author = ctx.author
        """Pause and resume."""
        player = self.bot.lavalink.players.get(guild.id)
        if not player.is_connected:
            if player.queue:
                await player.connect(author.voice.channel.id)
                await ctx.send(f'<:check:534931851660230666> Joined {author.voice.channel.name}', delete_after=5)
                if not player.is_playing:
                    await player.play()
                await ctx.send('Resumed queue.')
                return
            else:
                pass
        if not player.is_playing:
            msg = "<:tickred:539495579793883176> Nothing playing, use `play <song_name>`."
            await ctx.send(msg)
            return
        if player.paused:
            await player.set_pause(False)
            await ctx.send('Track resumed..')
        else:
            await player.set_pause(True)
            await ctx.send('Track paused..')

    @commands.check(checks.in_voice)
    @commands.guild_only()
    @commands.command(name="percent")
    async def _percent(self, ctx):
        """Shows you the percentage of the queue."""
        guild = ctx.guild
        queue_tracks = self.bot.lavalink.players.get(guild.id).queue
        queue_len = len(queue_tracks)
        requesters = {'total': 0, 'users': {}}

        async def _usercount(req_username):
            if req_username in requesters['users']:
                requesters['users'][req_username]['songcount'] += 1
                requesters['total'] += 1
            else:
                requesters['users'][req_username] = {}
                requesters['users'][req_username]['songcount'] = 1
                requesters['total'] += 1

        for i in range(queue_len):
            req_username = self.bot.get_user(queue_tracks[i].requester).name
            await _usercount(req_username)
        try:
            req_username = self.bot.get_user(self.bot.lavalink.players.get(guild.id).current.requester).name
            await _usercount(req_username)
        except AttributeError:
            await ctx.send('Nothing in the queue.')
            return

        for req_username in requesters['users']:
            percentage = float(requesters['users'][req_username]['songcount']) / float(requesters['total'])
            requesters['users'][req_username]['percent'] = round(percentage * 100, 1)

        top_queue_users = heapq.nlargest(20, [(x, requesters['users'][x][y]) for x in requesters['users'] for y in requesters['users'][x] if y == 'percent'], key=lambda x: x[1])
        queue_user = ["{}: {:g}%".format(x[0], x[1]) for x in top_queue_users]
        queue_user_list = '\n'.join(queue_user)
        await ctx.send(queue_user_list)

    @commands.check(checks.in_voice)
    @commands.guild_only()
    @commands.command(name="play", aliases=['p'])
    async def _play(self, ctx, *, query: str):
        """Plays a song from youtube, soundcloud or search."""
        guild = ctx.guild
        author = ctx.author
        channel = ctx.channel
        player = self.bot.lavalink.players.get(guild.id)
        player.store('channel', channel.id)
        player.store('guild', guild.id)
        if guild.id in self.play_lock:
            await ctx.send("Please wait, you are already queueing a playlist in this server...")
            return
        if not player.is_connected:
            await player.connect(author.voice.channel.id)
            await ctx.send(f'<:check:534931851660230666> Joined {author.voice.channel.name}', delete_after=5)
        query = query.strip('<>')
        if "open.spotify.com" in query:
            query = "spotify:{}".format(re.sub(r"(http[s]?:\/\/)?(open.spotify.com)\/", "", query).replace("/", ":"))
        if query.startswith("spotify:"):
            parts = query.split(":")
            if "track" in parts:
                res = await self._make_spotify_req("https://api.spotify.com/v1/tracks/{0}".format(parts[-1]))
                track = "spotify:{} {}".format(res["artists"][0]["name"], res["name"])
                player.add(requester=author.id, track=track)
                await ctx.send(f"<:check:534931851660230666> Added track to the queue.", delete_after=15)
                if not player.is_playing:
                    await player.play()
                return
            elif "album" in parts:
                query = parts[-1]
                r = await self._make_spotify_req("https://api.spotify.com/v1/albums/{0}".format(query))
                spotify_info = []
                while True:
                    try:
                        spotify_info.extend(r["tracks"]["items"])
                    except KeyError:
                        spotify_info.extend(r["items"])
                    try:
                        if r["next"] is not None:
                            r = await self._make_spotify_req(r["next"])
                            continue
                        else:
                            break
                    except KeyError:
                        if r["tracks"]["next"] is not None:
                            r = await self._make_spotify_req(r["tracks"]["next"])
                            continue
                        else:
                            break
                for i in spotify_info:
                    track = "spotify:{} {}".format(i["name"], i["artists"][0]["name"])
                    player.add(requester=author.id, track=track)
                player.store('channel', channel.id)
                await ctx.send(f"<:check:534931851660230666> Added spotify album to queue.", delete_after=15)
                if not player.is_playing:
                    await player.play()
                return
            elif "playlist" in parts:
                query = parts[-1]
                r = await self._make_spotify_req("https://api.spotify.com/v1/playlists/{0}/tracks".format(query))
                spotify_info = []
                numberoftracks = 0
                while True:
                    try:
                        spotify_info.extend(r["tracks"]["items"])
                    except KeyError:
                        spotify_info.extend(r["items"])
                    try:
                        if r["next"] is not None:
                            r = await self._make_spotify_req(r["next"])
                            continue
                        else:
                            break
                    except KeyError:
                        if r["tracks"]["next"] is not None:
                            r = await self._make_spotify_req(r["tracks"]["next"])
                            continue
                        else:
                            break
                for i in spotify_info:
                    query = "spotify:{} {}".format(i["track"]["name"], i["track"]["artists"][0]["name"])
                    player.add(requester=author.id, track=query)
                await ctx.send(f"<:check:534931851660230666> Added spotify playlist tracks to queue.", delete_after=15)
                player.store('channel', channel.id)
                if not player.is_playing:
                    await player.play()
                return
            else:
                return await ctx.send("This doesn't seem to be a valid Spotify URL or code.", delete_after=15)
        if not url_rx.match(query):
            query = f'ytsearch:{query}'
        results = await self.bot.lavalink.get_tracks(query)
        if not results or not results['tracks']:
            return await ctx.send('Nothing found!', delete_after=15)
        if results['loadType'] == 'PLAYLIST_LOADED':
            tracks = results['tracks']
            for track in tracks:
                player.add(requester=author.id, track=track)
                player.store('channel', channel.id)
            await ctx.send(f"<:check:534931851660230666> Added Youtube playlist to the queue.", delete_after=15)
        else:
            track = results['tracks'][0]
            await ctx.send(f"<:check:534931851660230666> Added track to the queue.", delete_after=15)
            player.add(requester=author.id, track=track)
            player.store('channel', channel.id)
        if not player.is_playing:
            await player.play()

    @commands.command(aliases=['q'], name="queue")
    @commands.guild_only()
    async def queue(self, ctx, page: int=1):
        """Shows you all the songs in queue."""
        emoji = {'cancel': '❌', 'back': '◀', 'forward': '▶', 'page': '🔢'}
        expected = ['❌', '◀', '▶', '🔢']
        guild = ctx.guild
        author = ctx.author
        items_per_page = 10
        player = self.bot.lavalink.players.get(guild.id)
        if not player.queue:
            await ctx.send('Nothing queued.')
            return
        if player.current is None:
            await ctx.send('The player is stopped.')
            return
        arrow = await self._draw_time(ctx, guild)
        pos = lavalink.Utils.format_time(player.position)
        try:
            if player.current.stream:
                dur = 'LIVE'
            else:
                dur = lavalink.Utils.format_time(player.current.duration)
            ntitle = player.current.title
            uri = player.current.uri
        except:
            if player.current['info']['isStream']:
                dur = 'LIVE'
            else:
                dur = lavalink.Utils.format_time(player.current['info']['length'])
            ntitle = player.current['info']['title']
            uri = player.current['info']['uri']
        embed = discord.Embed(colour=0x36393E)
        q = await self._queue(ctx, page)
        embed.add_field(name="Currently Playing:", value=f"{ntitle}\n{uri}\n{arrow} `[{pos}/{dur}]`")
        embed.add_field(name="Up Next:", value=f"{q}", inline=False)
        pages = math.ceil(len(player.queue) / items_per_page)
        text = 'Page {}/{} | {} tracks'.format(page, pages, len(player.queue))
        embed.set_footer(text=text)
        msg = await ctx.send(embed=embed)
        def check(r, u):
            return r.message.id == msg.id and u == author
        for i in range(4):
            await msg.add_reaction(expected[i])
        while True:
            try:
                (r, u) = await self.bot.wait_for('reaction_add', check=check, timeout=60.0)
            except asyncio.TimeoutError:
                return
            reacts = {v: k for k, v in emoji.items()}
            react = reacts[r.emoji]
            if react == "cancel":
                await msg.delete()
            elif react == "back":
                page = page-1
                pages = math.ceil(len(player.queue) / items_per_page)
                if page < 1:
                    page = pages
                q = await self._queue(ctx, page)
                arrow = await self._draw_time(ctx, guild)
                pos = lavalink.Utils.format_time(player.position)
                try:
                    if player.current.stream:
                        dur = 'LIVE'
                    else:
                        dur = lavalink.Utils.format_time(player.current.duration)
                    ntitle = player.current.title
                    uri = player.current.uri
                except:
                    if player.current['info']['isStream']:
                        dur = 'LIVE'
                    else:
                        dur = lavalink.Utils.format_time(player.current['info']['length'])
                    ntitle = player.current['info']['title']
                    uri = player.current['info']['uri']
                e = discord.Embed(colour=0x36393E)
                e.add_field(name="Currently Playing:", value=f"{ntitle}\n{uri}\n{arrow} `[{pos}/{dur}]`")
                e.add_field(name="Up Next:", value=f"{q}", inline=False)
                pages = math.ceil(len(player.queue) / items_per_page)
                text = 'Page {}/{} | {} tracks'.format(page, pages, len(player.queue))
                e.set_footer(text=text)
                await msg.edit(embed=e)
            elif react == "forward":
                page = page+1
                pages = math.ceil(len(player.queue) / items_per_page)
                if page > pages:
                    page = 1
                q = await self._queue(ctx, page)
                arrow = await self._draw_time(ctx, guild)
                pos = lavalink.Utils.format_time(player.position)
                try:
                    if player.current.stream:
                        dur = 'LIVE'
                    else:
                        dur = lavalink.Utils.format_time(player.current.duration)
                    ntitle = player.current.title
                    uri = player.current.uri
                except:
                    if player.current['info']['isStream']:
                        dur = 'LIVE'
                    else:
                        dur = lavalink.Utils.format_time(player.current['info']['length'])
                    ntitle = player.current['info']['title']
                    uri = player.current['info']['uri']
                e = discord.Embed(colour=0x36393E)
                e.add_field(name="Currently Playing:", value=f"{ntitle}\n{uri}\n{arrow} `[{pos}/{dur}]`")
                e.add_field(name="Up Next:", value=f"{q}", inline=False)
                text = 'Page {}/{} | {} tracks'.format(page, pages, len(player.queue))
                e.set_footer(text=text)
                await msg.edit(embed=e)
            elif react == "page":
                m = await ctx.send('What page would you like to go to?')
                def a(m):
                    return m.channel == ctx.channel and m.author == author
                while True:
                    try:
                        e = await ctx.bot.wait_for('message', check=a, timeout=60.0)
                    except asyncio.TimeoutError:
                        await m.delete()
                        await msg.delete()
                        await ctx.send("Canceled due to timeout.", delete_after=15)
                        return
                    if e.content.isdigit():
                        if int(e.content) > pages:
                            await ctx.send('Invalid page. Try again.', delete_after=4)
                        elif int(e.content) < 1:
                            await ctx.send('Invalid page. Try again.', delete_after=4)
                        else:
                            await msg.delete()
                            await m.delete()
                            await ctx.invoke(self.bot.get_command('queue'), page=int(e.content))
                            return

    async def _queue(self, ctx, page: int=1):
        guild = ctx.guild
        player = self.bot.lavalink.players.get(guild.id)
        items_per_page = 10
        start = (page - 1) * items_per_page
        end = start + items_per_page
        queue_list = ''
        for i, track in enumerate(player.queue[start:end], start=start):
            next = i + 1
            try:
                title = track.title
            except:
                title = track['info']['title']
            try:
                queue_list += '{}) {}\n'.format(next, title())
            except:
                queue_list += '{}) {}\n'.format(next, title)
        queue = queue_list.replace('||', '|').replace('Spotify:','')
        return queue

    @commands.command(name="clear")
    @commands.guild_only()
    @commands.check(checks.in_voice)
    async def _clear(self, ctx):
        """Clears the queue, doesn't stop the player tho."""
        guild = ctx.guild
        player = self.bot.lavalink.players.get(guild.id)
        if not player.queue:
            msg = "<:tickred:539495579793883176> Nothing queued, use `play <song_name>`."
            await ctx.send(msg)
            return
        else:
            msg = await ctx.send('<a:loading:535996854400319489> Clearing queue..')
            player.queue.clear()
            await msg.edit(content="<:check:534931851660230666> Cleared queue.")

    @commands.command(name="remove")
    @commands.guild_only()
    @commands.check(checks.in_voice)
    async def _remove(self, ctx, index: int):
        """Remove a specific song number from the queue."""
        guild = ctx.guild
        player = self.bot.lavalink.players.get(guild.id)
        if not player.queue:
            msg = "<:tickred:539495579793883176>  Nothing queued, use `play <song_name>`."
            await ctx.send(msg)
            return
        if index > len(player.queue) or index < 1:
            await ctx.send('Song number must be greater than 1 and within the queue limit.')
            return
        index = index - 1
        player.queue.pop(index)
        await ctx.send('<:check:433159782287802369> Removed from the queue.')
        return

    @commands.command(name="seek")
    @commands.guild_only()
    @commands.check(checks.in_voice)
    async def _seek(self, ctx, seconds: int=5):
        """Seeks ahead or behind on a track by seconds."""
        guild = ctx.guild
        player = self.bot.lavalink.players.get(guild.id)
        if player.is_playing:
            try:
                stream = player.current.stream
            except:
                stream = player.current['info']['isStream']
            if stream:
                await ctx.send('Can\'t seek on a stream.')
            else:
                time_sec = seconds * 1000
                seek = player.position + time_sec
                await ctx.send('<:check:433159782287802369> Moved {}s to {}'.format(seconds, lavalink.Utils.format_time(seek)))
                return await player.seek(seek)

    @commands.command(aliases=['forceskip', 'fs'], name="skip")
    @commands.guild_only()
    @commands.check(checks.in_voice)
    async def _skip(self, ctx, number: int=None):
        """Skips to the next track in the queue."""
        author = ctx.author
        guild = ctx.guild
        player = self.bot.lavalink.players.get(guild.id)
        if player.current is None:
            msg = "<:tickred:539495579793883176> Nothing playing, use `play <song_name>`."
            await ctx.send(msg)
        if number is not None:
            query = player.queue[number-1].uri
            results = await self.bot.lavalink.get_tracks(query)
            track = results['tracks'][0]
            player.add(requester=author.id, track=track)
            jump = self.bot.lavalink.players.get(guild.id).queue[len(player.queue) - 1]
            player.queue.insert(0, jump)
            player.queue.pop(number)
            await player.skip()
        else:
            await player.skip()

    @commands.command(name="stop")
    @commands.guild_only()
    @commands.check(checks.in_voice)
    async def _stop(self, ctx):
        """Stops playback of the song and clears the queue."""
        guild = ctx.guild
        player = self.bot.lavalink.players.get(guild.id)
        if player.is_playing:
            await ctx.send('Stopping...')
            player.queue.clear()
            await player.stop()

    @commands.command(aliases=['vol'], name="volume")
    @commands.guild_only()
    @commands.check(checks.in_voice)
    async def _volume(self, ctx, volume: int=None):
        """Changes Kira's volume."""
        guild = ctx.guild
        player = self.bot.lavalink.players.get(guild.id)
        if not volume:
            return await ctx.send(f'🔈 | {player.volume}%')
        if volume > 150:
            volume = 150
        await player.set_volume(volume)
        await ctx.send(f'🔈 | Set to {player.volume}%')

    @commands.command(name="shuffle")
    @commands.guild_only()
    @commands.check(checks.in_voice)
    async def _shuffle(self, ctx):
        """Shuffles the queue as you listen."""
        guild = ctx.guild
        player = self.bot.lavalink.players.get(guild.id)
        if not player.is_playing:
            await ctx.send('<:tickred:539495579793883176> Nothing playing, use `play <song_name>`.')
            return
        await player.shuffle()
        await ctx.send('Shuffled queue.')

    @commands.command(name="repeat")
    @commands.guild_only()
    @commands.check(checks.in_voice)
    async def _repeat(self, ctx):
        """Puts the queue on repeat."""
        guild = ctx.guild
        player = self.bot.lavalink.players.get(guild.id)
        if not player.is_playing:
            await ctx.send('<:tickred:539495579793883176> Nothing playing, use `play <song_name>`.')
            return
        player.repeat = not player.repeat
        await ctx.send('Repeat ' + ('enabled.' if player.repeat else 'disabled.'))

    @commands.command(name="search")
    @commands.guild_only()
    @commands.check(checks.in_voice)
    async def _search(self, ctx, *, query: str):
        """Used to fetch items from a search query."""
        guild = ctx.guild
        author = ctx.author
        player = self.bot.lavalink.players.get(guild.id)
        query = f'ytsearch:{query}'
        results = await self.bot.lavalink.get_tracks(query)
        number = 0
        e = discord.Embed()
        e.colour = 0x36393E
        e.description = ""
        tracks = results['tracks']
        for r in tracks:
            number += 1
            title = r['info']['title']
            e.description += f"**{number})** {title}\n"
        if e.description == "":
            e.description = "Nothing found, please cancel and search something else."
        m = await ctx.send(embed=e)
        f = await ctx.send("Please choose a result. Examples: `start 1` to play, `link 1` to retrieve link, `cancel` to cancel this search and delete messages.")
        def a(m):
            return m.channel == ctx.channel and m.author == author
        while True:
            try:
                msg = await ctx.bot.wait_for('message', check=a, timeout=60.0)
            except asyncio.TimeoutError:
                await m.delete()
                await f.delete()
                await ctx.send("Canceled search due to timeout.", delete_after=15)
                return
            if msg.content == "cancel":
                await m.delete()
                await f.delete()
                return
            elif msg.content == "Cancel":
                await m.delete()
                await f.delete()
                return
            elif msg.content.startswith('Link') or msg.content.startswith('link'):
                content = msg.content.replace('Link ', '').replace('link ', '')
                if content.isdigit():
                    if int(content) > number:
                        await ctx.send("Invalid number, try again.", delete_after=2)
                    else:
                        await m.delete()
                        await f.delete()
                        number = int(content) - 1
                        link = results['tracks'][number]['info']['uri']
                        await ctx.send(f"Here is your link. <a:miyano_trippin:532417746248531968>\n{link}")
                        return
            elif msg.content.startswith('start') or msg.content.startswith('Start'):
                content = msg.content.replace('start ', '').replace('Start ', '')
                if content.isdigit():
                    if int(content) > number:
                        await ctx.send("Invalid number, try again.", delete_after=2)
                    else:
                        await m.delete()
                        await f.delete()
                        player.store('channel', ctx.channel.id)
                        msg = await ctx.send("<a:loading:535996854400319489> Adding to queue..")
                        if not player.is_connected:
                            await player.connect(author.voice.channel.id)
                            await ctx.send(f'<:check:534931851660230666> Joined {author.voice.channel.name}', delete_after=5)
                        number = int(content) - 1
                        track = results['tracks'][number]
                        player.add(requester=author.id, track=track)
                        await msg.edit(content=f"<a:loading:535996854400319489> Added `{track['info']['title']}` to the queue..")
                        if not player.is_playing:
                            await player.play()
                        await asyncio.sleep(2)
                        await msg.delete()
                        return

    async def _draw_time(self, ctx, guild):
        player = self.bot.lavalink.players.get(guild.id)
        paused = player.paused
        pos = player.position
        try:
            dur = player.current.duration
        except:
            dur = player.current['info']['length']
        sections = 12
        loc_time = round((pos / dur) * sections)
        bar = '\N{BOX DRAWINGS HEAVY HORIZONTAL}'
        seek = r'\🔘'
        if paused:
            msg = r'\⏸ '
        else:
            msg = r'\▶ '
        for i in range(sections):
            if i == loc_time:
                msg += seek
            else:
                msg += bar
        return msg

    async def _clear_react(self, message):
        try:
            await message.clear_reactions()
        except:
            return

    async def _queue_duration(self, ctx, guild):
        player = self.bot.lavalink.players.get(guild.id)
        duration = []
        queue_duration = sum(duration)
        if not player.queue:
            queue_duration = 0
        try:
            remain = 0
        except AttributeError:
            remain = 0
        queue_total_duration = remain + queue_duration
        return queue_total_duration

    async def _make_get(self, url, headers=None):
        async with self.bot.session.request("GET", url, headers=headers) as r:
            if r.status != 200:
                print("{}Issue making GET request to {}: [{}] {}{}".format(CRED, url, r.status, await r.json(), CEND))
            return await r.json()

    async def _check_token(self, token):
        now = int(time.time())
        return token["expires_at"] - now < 60

    async def _request_token(self):
        client_id = self.config["spotify_client_id"]
        client_secret = self.config["spotify_client_secret"]
        payload = {"grant_type": "client_credentials"}
        headers = self._make_token_auth(client_id, client_secret)
        r = await self._make_post("https://accounts.spotify.com/api/token", payload=payload, headers=headers)
        return r

    async def _make_post(self, url, payload, headers=None):
        async with self.bot.session.post(url, data=payload, headers=headers) as r:
            if r.status != 200:
                print("{}Issue making POST request to {}: [{}] {}{}".format(CRED, url, r.status, await r.json(), CEND))
            return await r.json()

    def _make_token_auth(self, client_id, client_secret):
        auth_header = base64.b64encode((client_id + ":" + client_secret).encode("ascii"))
        return {"Authorization": "Basic %s" % auth_header.decode("ascii")}

    async def _get_spotify_token(self):
        if self.spotify_token and not await self._check_token(self.spotify_token):
            return self.spotify_token["access_token"]
        token = await self._request_token()
        if token is None:
            print(CRED + "Requested a token from Spotify, did not end up getting one." + CEND)
        token["expires_at"] = int(time.time()) + token["expires_in"]
        self.spotify_token = token
        print("{}Created a new access token for Spotify: {}{}".format(CYELLOW, token, CEND))
        return self.spotify_token["access_token"]

    async def _make_spotify_req(self, url):
        token = await self._get_spotify_token()
        return await self._make_get(url, headers={"Authorization": "Bearer {0}".format(token)})

    @staticmethod
    def _dynamic_time(time):
        m, s = divmod(time, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)

        if d > 0:
            msg = "{0}d {1}h"
        elif d == 0 and h > 0:
            msg = "{1}h {2}m"
        elif d == 0 and h == 0 and m > 0:
            msg = "{2}m {3}s"
        elif d == 0 and h == 0 and m == 0 and s > 0:
            msg = "{3}s"
        else:
            msg = ""
        return msg.format(d, h, m, s)

    async def buildCogHelp(self, ctx, *modules):
        formatted = ""
        cog_fmt = "**{cmd_name} -** {doc}\n"
        for m in modules:
            for c in ctx.bot.commands:
                if c.cog_name == m and not (c.hidden):
                    if c.short_doc == '':
                        doc = "No doc specified."
                    else:
                        doc = c.short_doc
                    formatted += cog_fmt.format(cmd_name=c.name, doc=doc)
        return formatted.replace("```", "")

def setup(bot):
    n = Music(bot)
    bot.add_cog(n)
