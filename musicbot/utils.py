import asyncio
from config import config

# A dictionary that remembers which guild belongs to which audiocontroller
guild_to_audiocontroller = {}

# A dictionary that remembers which settings belongs to which guild
guild_to_settings = {}


def get_guild(bot, command):
    """Gets the guild a command belongs to. Useful, if the command was sent via pm."""
    return bot.get_guild(command)


async def connect_to_channel(guild, dest_channel_name, ctx, switch=False, default=True):
    """Connects the bot to the specified voice channel.

        Args:
            guild: The guild for witch the operation should be performed.
            switch: Determines if the bot should disconnect from his current channel to switch channels.
            default: Determines if the bot should default to the first channel, if the name was not found.
    """
    for channel in guild.voice_channels:
        if str(channel.name).strip() == str(dest_channel_name).strip():
            if switch:
                try:
                    await guild.voice_client.disconnect()
                except:
                    await ctx.respond(config.NOT_CONNECTED_MESSAGE)

            await channel.connect()
            return

    if default:
        try:
            await guild.voice_channels[0].connect()
        except:
            await ctx.respond(config.DEFAULT_CHANNEL_JOIN_FAILED)
    else:
        await ctx.respond(config.CHANNEL_NOT_FOUND_MESSAGE + str(dest_channel_name))


async def is_connected(ctx):
    try:
        voice_channel = ctx.guild.voice_client.channel
        return voice_channel
    except:
        return None


async def play_check(ctx):

    sett = guild_to_settings[ctx.guild]

    cm_channel = sett.get('command_channel')
    vc_rule = sett.get('user_must_be_in_vc')

    if cm_channel != None:
        if cm_channel != ctx.message.channel.id:
            await ctx.respond(config.WRONG_CHANNEL_MESSAGE)
            return False

    if vc_rule == True:
        author_voice = ctx.author.voice.channel
        bot_vc = ctx.voice_client.channel
        if author_voice == None:
            await ctx.respond("gfdgdfg")
            return False
        elif ctx.author.voice.channel != bot_vc:
            await ctx.respond("gfdgdf")
            return False

def format_time(duration):
    if not duration:
        return "00:00"

    hours = duration // 60 // 60
    minutes = duration // 60 % 60
    seconds = duration % 60

    # Looks like `h:mm:ss`
    return "{}{}{:02d}:{:02d}".format(
        hours if hours else "",
        ":" if hours else "",
        minutes,
        seconds
    )

class Timer:
    def __init__(self, callback):
        self._callback = callback
        self._task = asyncio.create_task(self._job())

    async def _job(self):
        await asyncio.sleep(config.VC_TIMEOUT)
        await self._callback()

    def cancel(self):
        self._task.cancel()
