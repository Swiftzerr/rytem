import os

BOT_TOKEN: str = "ODkzMjk0MjMwMTQ1OTk4ODU5.YVZXFQ.ema_6fXQqagbncVjqrfzja8m25E"
SPOTIFY_ID: str = ""
SPOTIFY_SECRET: str = ""
EMBED_COLOR = 0x000000
SUPPORTED_EXTENSIONS = ('.webm', '.mp4', '.mp3', '.avi', '.wav', '.m4v', '.ogg', '.mov')
COOKIE_PATH = "/config/cookies/cookies.txt"
FILTERS = {
    "nightcore": "aresample=48000,asetrate=48000*1.25",
    "earrape": "acontrast, acrusher=level_in=4:level_out=8:bits=8:mode=log:aa=1"
}