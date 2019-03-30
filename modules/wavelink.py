import asyncio
import math
import time
import datetime
import lavalink
import discord
import aiohttp
import humanize
import base64
import itertools
import re
import sys
import traceback
import wavelink
import motor.motor_asyncio
from utils import checks
from datetime import datetime, timedelta
from discord.ext import commands
from typing import Union
CCYAN = '\33[36m'
CGREEN = '\33[32m'
CYELLOW = '\33[33m'
CRED = '\33[31m'
CEND = '\33[0m'
try:
    client = motor.motor_asyncio.AsyncIOMotorClient('localhost', 27017)
    db = client['kira_playlists']
    db = db.music
    d = client['kira_settings']
    edb = d.settings
    print(CGREEN + 'Loaded database\'s for music.py' + CEND)
except Exception as e:
    print(f'{CGREEN}Error in loading music database\'s!{CEND}\n{e}')

CCYAN = '\33[36m'
CGREEN = '\33[32m'
CYELLOW = '\33[33m'
CRED = '\33[31m'
CEND = '\33[0m'
RURL = re.compile('https?:\/\/(?:www\.)?.+')

class MusicController:

    def __init__(self, bot, guild_id):
        self.bot = bot
        self.guild_id = guild_id
        self.channel = None
        self.next = asyncio.Event()
        self.queue = asyncio.Queue()
        self.volume = 40
        self.now_playing = None
        self.bot.loop.create_task(self.controller_loop())

    async def controller_loop(self):
        await self.bot.wait_until_ready()
        player = self.bot.wavelink.get_player(self.guild_id)
        await player.set_volume(self.volume)
        while True:
            if self.now_playing:
                await self.now_playing.delete()
            self.next.clear()
            song = await self.queue.get()
            try:
                if song.startswith('spotify:'):
                    song = song.replace('spotify', 'ytsearch')
                    hm = await self.bot.wavelink.get_tracks(song)
                    song = hm[0]
            except:
                pass
            await player.play(song)
            e = discord.Embed()
            e.colour = 0x36393E
            e.add_field(name="Now playing:", value=f"{player.current.title} `[{lavalink.Utils.format_time(song.length)}]`\n{song.uri}")
            e.set_thumbnail(url=song.thumb)
            self.now_playing = await self.channel.send(embed=e)
            await self.next.wait()


class Music:

    def __init__(self, bot):
        self.bot = bot
        self.controllers = {}
        self.config = {"spotify_client_id": "51f8615447044a8bb0068c0c61d16ec1", "spotify_client_secret": "922bbdd2eafb4cd5a4631935f7d0c2a8", "youtube_api": "AIzaSyAYgC8XC8Rfh-SDvWhp96p6Xf_hIYzWB7g"}
        self.spotify_token = None
        self.play_lock = []
        self.session = aiohttp.ClientSession()
        if not hasattr(bot, 'wavelink'):
            self.bot.wavelink = wavelink.Client(self.bot)
        self.bot.loop.create_task(self.start_nodes())

    async def start_nodes(self):
        await self.bot.wait_until_ready()
        # Initiate our nodes. For this example we will use one server.
        # Region should be a discord.py guild.region e.g sydney or us_central (Though this is not technically required)
        node = await self.bot.wavelink.initiate_node(host='0.0.0.0',
                                                     port=2333,
                                                     rest_uri='http://0.0.0.0:2333',
                                                     password='youshallnotpass',
                                                     identifier='MAIN',
                                                     region='us_central')
        # Set our node hook callback
        node.set_hook(self.event_hook)

    async def event_hook(self, event):
        """Node hook callback."""
        if isinstance(event, (wavelink.TrackEnd, wavelink.TrackException)):
            controller = self.get_controller(event.player)
            controller.next.set()

    def get_controller(self, value: Union[commands.Context, wavelink.Player]):
        if isinstance(value, commands.Context):
            gid = value.guild.id
        else:
            gid = value.guild_id
        try:
            controller = self.controllers[gid]
        except KeyError:
            controller = MusicController(self.bot, gid)
            self.controllers[gid] = controller
        return controller

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    @commands.check(checks.in_voice)
    @commands.command(name='connect')
    async def connect_(self, ctx, *, channel: discord.VoiceChannel=None):
        """Connect to a valid voice channel."""
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise discord.DiscordException('No channel to join. Please either specify a valid channel or join one.')
        player = self.bot.wavelink.get_player(ctx.guild.id)
        await ctx.send(f'Connecting to **{channel.name}**', delete_after=15)
        await player.connect(channel.id)
        controller = self.get_controller(ctx)
        controller.channel = ctx.channel

    @commands.command(name="search", pass_context=True)
    @commands.check(checks.in_voice)
    async def _search(self, ctx, *, query: str):
        """Used to fetch items from a search query."""
        query = f'ytsearch:{query}'
        player = self.bot.wavelink.get_player(ctx.guild.id)
        controller = self.get_controller(ctx)
        results = await self.bot.wavelink.get_tracks(query)
        number = 0
        e = discord.Embed()
        e.colour = 0x36393E
        e.description = ""
        for r in results:
            number += 1
            title = r.title
            e.description += f"**{number})** {title}\n"
        m = await ctx.send(embed=e)
        f = await ctx.send("Please choose a result. Example: `start 1`. Or you can type `cancel` to cancel this.")
        def a(m):
            return m.channel == ctx.channel and m.author == ctx.author
        while True:
            try:
                msg = await ctx.bot.wait_for('message', check=a, timeout=60.0)
            except asyncio.TimeoutError:
                await m.delete()
                await f.delete()
            if msg.content == "cancel":
                await m.delete()
                await f.delete()
                return
            elif msg.content == "Cancel":
                await m.delete()
                await f.delete()
                return
            elif msg.content.startswith('start') or msg.content.startswith('Start'):
                content = msg.content.replace('start ', '').replace('Start ', '')
                if content.isdigit():
                    if int(content) > number:
                        await ctx.send("Invalid number.")
                    else:
                        await m.delete()
                        await f.delete()
                        if not player.is_connected:
                            await ctx.invoke(self.connect_)
                        number = int(content) - 1
                        track = results[number]
                        await controller.queue.put(track)
                        await ctx.send(f"Added `{track.title}` to the queue..", delete_after=15)
                        return

    @commands.group(aliases=["pl"])
    async def playlists(self, ctx):
        """Shows you commands for your playlists... remove the ..help at the beginning
        want to add a playlist?
        try.
        k.playlists add https://www.youtube.com/playlist?list=PLByvRxAlykqMXqz3-akzuMG4IocsqOYUn hours"""
        if ctx.invoked_subcommand is None:
            e = discord.Embed()
            e.colour = 0x36393E
            e.set_author(name="Help for Kira's command group playlists.", icon_url=ctx.guild.me.avatar_url)
            e.description = "**show - ** Lets you see your saved playlists..\n"
            e.description += "**start -** Start one of those lit playlists.\n"
            e.description += "**add -** Will add a playlist to your database.\n"
            e.description += "**del -** Will delete a playlist from your databse.\n"
            e.description += "**push -** Add links to a existing playlists.\n"
            e.description += "**pull -** Remove links to a existing playlists.\n"
            e.set_thumbnail(url=ctx.guild.me.avatar_url)
            await ctx.send(embed=e)

    @playlists.command()
    async def show(self, ctx, *, playlist: str=None):
        """Shows your saved playlists."""
        author = ctx.author
        settings = {
            "user_id": author.id,
        }
        logs = await db.find_one({"user_id": ctx.author.id})
        if not logs:
            await ctx.send("Database not found for you, create one by making a playlist.")
            return
        if logs:
            if logs == settings:
                await ctx.send("You have a database, but you don't have any playlists, use the command `k.myplaylists` to add some, use this as an example `k.myplaylists add <name> <link>")
                return
        if playlist is None:
            number = 0
            data = discord.Embed()
            data.set_author(name="Here are those lit playlists.", icon_url=ctx.author.avatar_url)
            data.colour = 0x36393E
            data.description = f"For more info on a playlist try {ctx.prefix}myplaylists show  <playlist>\n\n**Available Playlists:**\n"
            for key, val in logs.items():
                if "_id" in key:
                    continue
                number += 1
                data.description += f"`{number})` {key}\n"
            if data.description == "":
                data.description = "Oh you don't have any playlists. You should really add some.\n\n**To add playlists use the command `k.myplaylists`, use this as an example `k.myplaylists add <name> <link>`"
                data.set_image(url="https://i.imgur.com/8FfFpVB.png")
            await ctx.send(embed=data)
            return
        if playlist is not None:
            data = discord.Embed()
            data.set_author(name=f"More info on playlist {playlist}:", icon_url=ctx.author.avatar_url)
            data.add_field(name="Playlist name:", value=playlist)
            data.add_field(name="# of links:", value=len(logs[playlist]))
            data.colour = 0x36393E
            if len(logs[playlist]) < 10:
                data.add_field(name="Playlist links:", value="\n".join(link for link in logs[playlist]), inline=False)
            if len(logs[playlist]) > 10:
                data.add_field(name="Playlist links:", value=f"I cannot show all the links.", inline=False)
            await ctx.send(embed=data)

    @playlists.command(name="start")
    @commands.check(checks.in_voice)
    async def start_(self, ctx, *, name: str):
        """Starts one of your custom playlists."""
        author = ctx.author
        guild = ctx.guild
        message = ctx.message
        channel = ctx.channel
        controller = self.get_controller(ctx)
        logs = await db.find_one({"user_id": author.id})
        if guild.id in self.play_lock:
            await channel.send("Please wait, you are already queueing a playlist in this server...")
            return
        if logs:
            player = self.bot.wavelink.get_player(ctx.guild.id)
            if not player.is_connected:
                await ctx.invoke(self.connect_)
            keys = {k:v for k,v in logs.items() if not k.endswith('_id')}
            if name in keys:
                self.play_lock.append(guild.id)
                msg = await channel.send("<a:loading:532575409506746369> Loading your playlist...")
                for link in keys[name]:
                    query = link
                    if "open.spotify.com" in query:
                        query = "spotify:{}".format(re.sub("(http[s]?:\/\/)?(open.spotify.com)\/", "", query).replace("/", ":"))
                    if query.startswith("spotify:"):
                        parts = query.split(":")
                        if "track" in parts:
                            res = await self._make_spotify_req("https://api.spotify.com/v1/tracks/{0}".format(parts[-1]))
                            query = "ytsearch:{} {}".format(res["artists"][0]["name"], res["name"])
                            hm = await self.bot.wavelink.get_tracks(f'{query}')
                            track = hm[0]
                            await controller.queue.put(track)
                            await msg.edit(content=f'<a:loading:532575409506746369> Added {str(track)} to the queue.')
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
                                await controller.queue.put(track)
                            await msg.edit(content=f"<a:loading:532575409506746369> Added spotify album **{r['name']}** with **{r['total_tracks']}** tracks")
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
                                numberoftracks += 1
                                track = "spotify:{} {}".format(i["track"]["name"], i["track"]["artists"][0]["name"])
                                await controller.queue.put(track)
                            await msg.edit(content=f"<a:loading:532575409506746369> Added spotify playlist **{r['name']}** with **{numberoftracks}** tracks")
                    if "youtube.com/playlist?list=" in query:
                        oi = await self.bot.wavelink.get_tracks(f'{query}')
                        data  = oi.data
                        if data['loadType'] == 'PLAYLIST_LOADED':
                            for track in oi.tracks:
                                await controller.queue.put(track)
                        await msg.edit(content=f"<a:loading:532575409506746369> Add YouTube playlist {data['playlistInfo']['name']} to the queue.")
                    else:
                        query = f'ytsearch:{query}'
                        lol = await self.bot.wavelink.get_tracks(f'{query}')
                        track = lol[0]
                        await controller.queue.put(track)
                        await msg.edit(content=f'<a:loading:532575409506746369> Added {str(track)} to the queue.')
                    await asyncio.sleep(3)
                await msg.edit(content="<:check:433159782287802369> Done! I have loaded your playlist!")
                self.play_lock.remove(guild.id)
                await asyncio.sleep(3)
                await msg.delete()
                return
            else:
                await channel.send("Playlist not found.")
        else:
            await channel.send("You don't have a database. Why don't you make one?")
            return


    @playlists.command(name="add")
    async def _add(self, ctx, link, *, name: str):
        """Add a playlists to you database.

        Try.
        k.mp add https://www.youtube.com/watch?v=ly9zUw2jVcc&list=PLQh6qjoTV_I-6SVu_gW13_4fiG3B0YhxQ Suicide Boys"""
        author = ctx.author
        settings = {
            "user_id": author.id,
        }
        logs = await db.find_one({"user_id": ctx.author.id})
        if name == "":
            await ctx.send("Playlist name cannot be empty.")
            return
        if not logs:
            creating = await ctx.send("<a:loading:532575409506746369> Creating your database...")
            await db.insert_one(settings)
            await asyncio.sleep(4)
            await creating.edit(content="<a:loading:532575409506746369> Created your databse....now it's time to add your playlists to it.")
            await db.update_one({"user_id": author.id}, {'$set': {name: []}})
            await db.update_one({"user_id": author.id}, {'$push': {name: link}})
            await asyncio.sleep(4)
            await creating.edit(content="<:check:433159782287802369> Done! I have created your databse, and added your first playlist to it! You're all set to go!")
            return
        else:
            await db.update_one({"user_id": author.id}, {'$set': {name: []}})
            await db.update_one({"user_id": author.id}, {'$push': {name: link}})
            await ctx.send("Added the playlist to your database!")
            return

    @playlists.command(name="push")
    async def _push(self, ctx, link, *, name: str):
        """Add links to a existing playlists."""
        author = ctx.author
        logs = await db.find_one({"user_id": ctx.author.id})
        if logs:
            await db.update_one({"user_id": author.id}, {'$push': {name: link}})
            await ctx.send('Done, added the link to the playlist.')
            return
        else:
            await ctx.send("I'm sorry, but you don't have a playlist database.")

    @playlists.command(name="pull")
    async def _pull(self, ctx, link, *, name: str):
        """Remove links to a existing playlists."""
        author = ctx.author
        logs = await db.find_one({"user_id": ctx.author.id})
        if logs:
            await db.update_one({"user_id": author.id}, {'$pull': {name: link}})
            await ctx.send('Done, removed the link to the playlist.')
            return
        else:
            await ctx.send("I'm sorry, but you don't have a playlist database.")

    @playlists.command(name="del")
    async def _del(self, ctx, *, name: str):
        """Deletes a playlist from your databse."""
        author = ctx.author
        logs = await db.find_one({"user_id": ctx.author.id})
        keys = {k:v for k,v in logs.items() if not k.endswith('_id')}
        if name not in keys:
            await ctx.send("Playlist not found in database.")
            return
        if not logs:
            await ctx.send("You don't have any playlists, make one.")
        else:
            await db.update_one({"user_id": author.id}, {"$unset":{name: keys[name]}})
            await ctx.send("Removed the playlist from your databse.")

    @commands.check(checks.in_voice)
    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query: str):
        """Search for and add a song to the Queue."""
        guild = ctx.guild
        channel = ctx.channel
        controller = self.get_controller(ctx)
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            await ctx.invoke(self.connect_)
        try:
            if "open.spotify.com" in query:
                query = "spotify:{}".format(re.sub("(http[s]?:\/\/)?(open.spotify.com)\/", "", query).replace("/", ":"))
            if query.startswith("spotify:"):
                parts = query.split(":")
                if "track" in parts:
                    res = await self._make_spotify_req("https://api.spotify.com/v1/tracks/{0}".format(parts[-1]))
                    query = "ytsearch:{} {}".format(res["artists"][0]["name"], res["name"])
                    hm = await self.bot.wavelink.get_tracks(f'{query}')
                    track = hm[0]
                    await controller.queue.put(track)
                    await ctx.send(f'Added {str(track)} to the queue.', delete_after=15)
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
                        await controller.queue.put(track)
                    await ctx.send(f"Added spotify album **{r['name']}** with **{r['total_tracks']}** tracks", delete_after=15)
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
                        numberoftracks += 1
                        track = "spotify:{} {}".format(i["track"]["name"], i["track"]["artists"][0]["name"])
                        await controller.queue.put(track)
                    await ctx.send(f"Added spotify playlist **{r['name']}** with **{numberoftracks}** tracks", delete_after=15)
                    return
                else:
                    await ctx.send(content="This doesn't seem to be a valid Spotify URL or code.", delete_after=15)
                    return
            if "youtube.com/playlist?list=" in query:
                oi = await self.bot.wavelink.get_tracks(f'{query}')
                data  = oi.data
                if data['loadType'] == 'PLAYLIST_LOADED':
                    for track in oi.tracks:
                        await controller.queue.put(track)
                    await ctx.send(f"Add YouTube playlist {data['playlistInfo']['name']} to the queue.", delete_after=15)
                    return
            else:
                query = f'ytsearch:{query}'
                lol = await self.bot.wavelink.get_tracks(f'{query}')
                track = lol[0]
                await controller.queue.put(track)
                await ctx.send(f'Added {str(track)} to the queue.', delete_after=15)
                return
        except Exception as e:
            print(e)
            await ctx.send('Nothing found!', delete_after=15)
            return

    @commands.check(checks.in_voice)
    @commands.command()
    async def pause(self, ctx):
        """Pause the player."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send('I am not currently playing anything!', delete_after=15)
        await ctx.send('Pausing the song!', delete_after=15)
        await player.set_pause(True)

    @commands.check(checks.in_voice)
    @commands.command()
    async def resume(self, ctx):
        """Resume the player from a paused state."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.paused:
            return await ctx.send('I am not currently paused!', delete_after=15)
        await ctx.send('Resuming the player!', delete_after=15)
        await player.set_pause(False)

    @commands.check(checks.in_voice)
    @commands.command()
    async def skip(self, ctx):
        """Skip the currently playing song."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send('I am not currently playing anything!', delete_after=15)
        await ctx.send('Skipping the song!', delete_after=15)
        await player.stop()

    @commands.check(checks.in_voice)
    @commands.command()
    async def volume(self, ctx, *, vol: int=None):
        """Set the player volume."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        controller = self.get_controller(ctx)
        if vol == None:
            await ctx.send(f'Volume is currently set to `{player.volume}`')
            return
        vol = max(min(vol, 150), 0)
        controller.volume = vol
        await ctx.send(f'Setting the player volume to `{vol}`')
        await player.set_volume(vol)

    @commands.command(aliases=['np', 'current', 'nowplaying'])
    async def now(self, ctx):
        """Retrieve the currently playing song."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.current:
            return await ctx.send('I am not currently playing anything!')
        controller = self.get_controller(ctx)
        try:
            await controller.now_playing.delete()
        except:
            pass
        pos = lavalink.Utils.format_time(player.position)
        if player.current.is_stream:
            dur = 'LIVE'
        else:
            dur = lavalink.Utils.format_time(player.current.duration)
        e = discord.Embed()
        e.colour = 0x36393E
        e.add_field(name="Now playing:", value=f"{player.current.title} `[{pos}/{dur}]`\n{player.current.uri}")
        e.set_thumbnail(url=player.current.thumb)
        controller.now_playing = await ctx.send(embed=e)

    @commands.command(aliases=['q'])
    async def queue(self, ctx):
        """Retrieve information on the next 5 songs from the queue."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        controller = self.get_controller(ctx)
        if not player.current or not controller.queue._queue:
            return await ctx.send('There are no songs currently in the queue.', delete_after=20)
        pos = lavalink.Utils.format_time(player.position)
        if player.current.is_stream:
            dur = 'LIVE'
        else:
            dur = lavalink.Utils.format_time(player.current.duration)
        e = discord.Embed()
        e.colour = 0x36393E
        e.add_field(name="Now playing:", value=f"{player.current.title} `[{pos}/{dur}]`\n{player.current.uri}")
        e.set_thumbnail(url=player.current.thumb)
        upcoming = list(itertools.islice(controller.queue._queue, 0, 10))
        fmt = '\n'.join(f'{str(song)}' for song in upcoming)
        e.add_field(name="Up Next:", value=fmt.replace('spotify:', ''))
        await ctx.send(embed=e)

    @commands.check(checks.in_voice)
    @commands.command(aliases=['disconnect', 'dc'])
    async def stop(self, ctx):
        """Stop and disconnect the player and controller."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        try:
            del self.controllers[ctx.guild.id]
        except KeyError:
            await player.disconnect()
            return await ctx.send('There was no controller to stop.')
        await player.disconnect()
        await ctx.send('Disconnected player and killed controller.', delete_after=20)

    @commands.check(checks.in_voice)
    @commands.command(name='seteq')
    async def set_eq(self, ctx, *, eq: str):
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if eq.upper() not in player.equalizers:
            return await ctx.send(f'`{eq}` - Is not a valid equalizer!\nTry Flat, Boost, Metal, Piano.')
        player.eq = await player.set_preq(eq.upper())
        await ctx.send(f'The player Equalizer was set to - {eq.upper()}')


    @commands.command()
    async def winfo(self, ctx):
        """Retrieve various Node/Server/Player information."""
        player = self.bot.wavelink.get_player(ctx.guild.id)
        node = player.node
        used = humanize.naturalsize(node.stats.memory_used)
        total = humanize.naturalsize(node.stats.memory_allocated)
        free = humanize.naturalsize(node.stats.memory_free)
        cpu = node.stats.cpu_cores
        fmt = f'**WaveLink:** `{wavelink.__version__}`\n\n' \
              f'Connected to `{len(self.bot.wavelink.nodes)}` nodes.\n' \
              f'Best available Node `{self.bot.wavelink.get_best_node().__repr__()}`\n' \
              f'`{len(self.bot.wavelink.players)}` players are distributed on nodes.\n' \
              f'`{node.stats.players}` players are distributed on server.\n' \
              f'`{node.stats.playing_players}` players are playing on server.\n\n' \
              f'Server Memory: `{used}/{total}` | `({free} free)`\n' \
              f'Server CPU: `{cpu}`\n\n' \
              f'Server Uptime: `{datetime.timedelta(milliseconds=node.stats.uptime)}`'
        await ctx.send(fmt)

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

    def _make_token_auth(self, client_id, client_secret):
        auth_header = base64.b64encode((client_id + ":" + client_secret).encode("ascii"))
        return {"Authorization": "Basic %s" % auth_header.decode("ascii")}
    async def _make_post(self, url, payload, headers=None):
        async with self.session.post(url, data=payload, headers=headers) as r:
            if r.status != 200:
                print("{}Issue making POST request to {}: [{}] {}{}".format(CRED, url, r.status, await r.json(), CEND))
            return await r.json()

    async def _make_get(self, url, headers=None):
        async with self.session.request("GET", url, headers=headers) as r:
            if r.status != 200:
                print("{}Issue making GET request to {}: [{}] {}{}".format(CRED, url, r.status, await r.json(), CEND))
            return await r.json()

def setup(bot):
    bot.add_cog(Music(bot))