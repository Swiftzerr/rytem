import os

import discord
from discord.ext import commands

from config import config
from musicbot.audiocontroller import AudioController
from musicbot.settings import Settings
from musicbot.utils import guild_to_audiocontroller, guild_to_settings

initial_extensions = ['musicbot.commands.music', 'musicbot.commands.general']
bot = commands.Bot()


if __name__ == '__main__':

    if config.BOT_TOKEN == "":
        print("Error: No bot token!")
        exit

    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(e)


@bot.event
async def on_ready():
    print("Starting le bot\n\n\n")
    print("In servers:\n\n")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="Hentai Ballons TM"))

    for guild in bot.guilds:
        await register(guild)
        print("Server: {}\n".format(guild.name))


@bot.event
async def on_guild_join(guild):
    print("\nJust joined server: " + guild.name)
    await register(guild)


async def register(guild):

    guild_to_settings[guild] = Settings(guild)
    guild_to_audiocontroller[guild] = AudioController(bot, guild)

    sett = guild_to_settings[guild]

    try:
        await guild.me.edit(nick=sett.get('default_nickname'))
    except:
        pass

    vc_channels = guild.voice_channels

    if sett.get('vc_timeout') == False:
        if sett.get('start_voice_channel') == None:
            try:
                await guild_to_audiocontroller[guild].register_voice_channel(guild.voice_channels[0])
            except Exception as e:
                print(e)

        else:
            for vc in vc_channels:
                if vc.id == sett.get('start_voice_channel'):
                    try:
                        await guild_to_audiocontroller[guild].register_voice_channel(vc_channels[vc_channels.index(vc)])
                    except Exception as e:
                        print(e)

config.COOKIE_PATH = os.path.dirname(os.path.abspath(__file__)) + config.COOKIE_PATH
bot.run(config.BOT_TOKEN, reconnect=True)
