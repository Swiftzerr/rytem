import discord
from config import config
from discord.ext import commands
from discord.ext.commands import has_permissions
from musicbot import utils
from musicbot.audiocontroller import AudioController
from musicbot.utils import guild_to_audiocontroller, guild_to_settings


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(description="Makes the bot clear queue and leave the VC (DJ role required)")
    async def leave(self, ctx, guild=False):
        current_guild = ctx.guild
        audiocontroller = utils.guild_to_audiocontroller[current_guild]
        await audiocontroller.udisconnect()


def setup(bot):
    bot.add_cog(General(bot))
