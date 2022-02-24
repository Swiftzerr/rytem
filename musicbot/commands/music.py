import asyncio

import discord
from config import config
from discord.ext import commands
from musicbot import linkutils, utils


class Emojis():
    loop = "\U0001F501"
    no = "\u274C"
    play = "\u25B6"
    down_arrow = "\u2935"
    check = "\u2705"


def send_message(ctx, message):
    a = ctx.respond(embed=discord.Embed(title=message, color=config.EMBED_COLOR))
    return a

async def find_filters(ctx):
    return [filters for filters in config.FILTERS]


class Music(commands.Cog):
    """ A collection of the commands related to music playback.

        Attributes:
            bot: The instance of the bot that is executing the commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Plays a song")
    async def play(self, ctx: commands.Context, *, song: discord.commands.Option(str, "Song or url to play")):

        current_guild = ctx.guild
        audiocontroller = utils.guild_to_audiocontroller[current_guild]

        if(await utils.is_connected(ctx) == None):
            if await audiocontroller.uconnect(ctx) == False:
                return

        if song.isspace() or not song:
            return

        if await utils.play_check(ctx) == False:
            return

        # reset timer
        audiocontroller.timer.cancel()
        audiocontroller.timer = utils.Timer(audiocontroller.timeout_handler)

        if audiocontroller.playlist.loop == True:
            await send_message(ctx, Emojis.no + " Cannot add songs to queue while looping is enabled")
            return

        song = await audiocontroller.process_song(song, ctx)

        if song is None:
            await ctx.respond(config.SONGINFO_ERROR)
            return

        if song.origin == linkutils.Origins.Default:

            if audiocontroller.current_song != None and len(audiocontroller.playlist.playque) == 0:
                await ctx.respond(embed=song.info.format_output(config.SONGINFO_NOW_PLAYING))
            else:
                await ctx.respond(embed=song.info.format_output(config.SONGINFO_QUEUE_ADDED))

        elif song.origin == linkutils.Origins.Playlist:
            await ctx.respond(config.SONGINFO_PLAYLIST_QUEUED)

    @commands.slash_command(description="Toggles song looping")
    async def loop(self, ctx: commands.Context):

        current_guild = ctx.guild
        audiocontroller = utils.guild_to_audiocontroller[current_guild]

        if await utils.play_check(ctx) == False:
            return

        if len(audiocontroller.playlist.playque) < 1 and current_guild.voice_client.is_playing() == False:
            await ctx.respond("No songs in queue!")
            return

        if audiocontroller.playlist.loop == False:
            audiocontroller.playlist.loop = True
            await send_message(ctx, Emojis.loop + " Enabled")
        else:
            audiocontroller.playlist.loop = False
            await send_message(ctx, Emojis.loop + " Disabled")

    @commands.command(name='pause', description=config.HELP_PAUSE_LONG, help=config.HELP_PAUSE_SHORT)
    async def pause(self, ctx):
        current_guild = ctx.guild

        if await utils.play_check(ctx) == False:
            return

        if current_guild is None:
            await ctx.respond(config.NO_GUILD_MESSAGE)
            return
        if current_guild.voice_client is None or not current_guild.voice_client.is_playing():
            return
        current_guild.voice_client.pause()
        await send_message(ctx, ":pause_button: Paused")

    @commands.slash_command(description="Shows the songs in the current queue")
    async def queue(self, ctx):
        current_guild = ctx.guild

        if await utils.play_check(ctx) == False:
            return

        if current_guild is None:
            await ctx.respond(config.NO_GUILD_MESSAGE)
            return
        if current_guild.voice_client is None or not current_guild.voice_client.is_playing():
            await send_message(ctx, Emojis.no + " Nothing in the queue")
            return

        playlist = utils.guild_to_audiocontroller[current_guild].playlist

        # Embeds are limited to 25 fields
        if config.MAX_SONG_PRELOAD > 25:
            config.MAX_SONG_PRELOAD = 25

        total_runtime = utils.format_time(
            sum([int(song.info.duration if song.info.duration else 0) for song in list(playlist.playque)]))

        embed = discord.Embed(title=":scroll: {} songs in queue | {} total length".format(
            len(playlist.playque), total_runtime), color=config.EMBED_COLOR, inline=False)

        in_queue_formats = []
        for counter, song in enumerate(list(playlist.playque)[:config.MAX_SONG_PRELOAD], start=1):
            if song.info.title is None:
                in_queue_formats.append("`{}.` [{}]({}) `{}`".format(
                    str(counter), song.info.webpage_url, song.info.webpage_url,
                    utils.format_time(song.info.duration)))
            else:
                in_queue_formats.append("`{}.` [{}]({}) `{}`".format(
                    str(counter), song.info.title, song.info.webpage_url,
                    utils.format_time(song.info.duration)))

                if len(in_queue_formats):
                    embed.description = '\n'.join(in_queue_formats)

        await ctx.respond(embed=embed)

    @commands.slash_command(description="Votes to skip the song")
    async def skip(self, ctx):
        current_guild = ctx.guild

        if await utils.play_check(ctx) == False:
            return

        audiocontroller = utils.guild_to_audiocontroller[current_guild]
        audiocontroller.playlist.loop = False

        audiocontroller.timer.cancel()
        audiocontroller.timer = utils.Timer(audiocontroller.timeout_handler)

        if current_guild is None:
            await ctx.respond(config.NO_GUILD_MESSAGE)
            return
        if current_guild.voice_client is None or (
                not current_guild.voice_client.is_paused() and not current_guild.voice_client.is_playing()):
            await send_message(ctx, Emojis.no + " Nothing in the queue")
            return
        current_guild.voice_client.stop()
        await send_message(ctx, ":fast_forward: Skipped song")

    @commands.slash_command(description="Clears the queue")
    async def clear(self, ctx):
        current_guild = ctx.guild

        if await utils.play_check(ctx) == False:
            return

        audiocontroller = utils.guild_to_audiocontroller[current_guild]
        audiocontroller.clear_queue()
        current_guild.voice_client.stop()
        audiocontroller.playlist.loop = False
        await send_message(ctx, ":no_entry_sign: Cleared queue")

    @commands.slash_command(description="Applies nightcore to the music")
    async def nightcore(self, ctx):
        audiocontroller = utils.guild_to_audiocontroller[ctx.guild]
        if "nightcore" not in audiocontroller.filters:
            audiocontroller.filters.append("nightcore")
            await audiocontroller.restart_player()
            await send_message(ctx, Emojis.check + " Enabled Nightcore")
        else:
            audiocontroller.filters.remove("nightcore")
            await audiocontroller.restart_player()
            await send_message(ctx, Emojis.no + " Disabled Nightcore")


    # @commands.slash_command(description="Applies a filter to music")
    # async def filter(self, ctx, *, arg: discord.commands.Option(str, "Filter name", name="filter", autocomplete=find_filters)):
    #     audiocontroller = utils.guild_to_audiocontroller[ctx.guild]
    #     arg = arg.split()
    #     print(arg)
    #     print(arg[0])
    #     if ctx.guild is None:
    #         await ctx.respond(config.NO_GUILD_MESSAGE)
    #         return
    #
    #     if await utils.play_check(ctx) == False:
    #         return
    #
    #     if len(arg) == 0:
    #         await ctx.respond(f':information_source: | Current filters: `{", ".join(audiocontroller.filters)}`')
    #         return
    #
    #     if arg[0] == 'off':
    #         audiocontroller.filters = []
    #         await audiocontroller.restart_player()
    #         await ctx.respond(':no_entry_sign: | All filters disabled!')
    #     elif arg[0] in config.FILTERS:
    #         if arg[0] not in audiocontroller.filters:
    #             audiocontroller.filters.append(arg[0])
    #             await audiocontroller.restart_player()
    #             await ctx.respond(f':notes: | Filter `{arg[0]}` enabled!')
    #         else:
    #             audiocontroller.filters.remove(arg[0])
    #             await audiocontroller.restart_player()
    #             await ctx.respond(f':no_entry_sign: | Filter `{arg[0]}` disabled!')
    #     else:
    #         await ctx.respond(":warning: | Invalid filter!")

def setup(bot):
    bot.add_cog(Music(bot))
