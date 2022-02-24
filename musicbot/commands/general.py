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

    @commands.slash_command(description="Change server settings (Admin required)")
    async def settings(self, ctx, setting, value):

        sett = guild_to_settings[ctx.guild]

        if len(args) == 0:
            await ctx.send(embed=await sett.format())
            return

        args_list = list(args)
        args_list.remove(args[0])

        response = await sett.write(args[0], " ".join(args_list), ctx)

        if response is None:
            await ctx.send("`Error: Setting not found`")
        elif response is True:
            await ctx.send("Setting updated!")


def setup(bot):
    bot.add_cog(General(bot))
