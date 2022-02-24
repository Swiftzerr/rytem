import datetime

import discord
from config import config


class Song():
    def __init__(self, origin, host, base_url=None, uploader=None, title=None, duration=None, webpage_url=None, thumbnail=None, ctx=None):
        self.host = host
        self.origin = origin
        self.base_url = base_url
        self.info = self.Sinfo(uploader, title, duration,
                               webpage_url, thumbnail, ctx)

    class Sinfo:
        def __init__(self, uploader, title, duration, webpage_url, thumbnail, ctx):
            self.uploader = uploader
            self.title = title
            self.duration = duration
            self.webpage_url = webpage_url
            self.thumbnail = thumbnail
            self.output = ""
            self.requester = ctx.author

        def format_output(self, playtype):

            embed = discord.Embed(title=playtype, description="**" + self.title + "**", color=config.EMBED_COLOR)
            embed.timestamp = datetime.datetime.now()
            embed.set_footer(text="Requested by: " + self.requester.name, icon_url=self.requester.avatar)
            return embed
