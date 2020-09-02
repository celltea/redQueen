import json

from discord.ext import commands
from utilities import settings

settings = settings.config("settings.json")

def getfromin(bot, ctx, mode, inp):
    if mode == 'use':
        try:
            out = bot.get_user(int(inp))
        except ValueError:
            out = bot.get_user(int(strip(inp)))
    elif mode == 'mem':
        try:
            out = ctx.guild.get_member(int(inp))
        except ValueError:
            out = ctx.guild.get_member(int(strip(inp)))
    elif mode == 'rol':
        try:
            out = ctx.guild.get_role(int(inp))
        except ValueError:
            out = ctx.guild.get_role(int(strip(inp)))
    elif mode == 'cha':
        try:
            out = bot.get_channel(int(inp))
        except ValueError:
            out = bot.get_channel(int(strip(inp)))
    return out

def strip(fancy):
    fancy = fancy[2:-1]
    while not fancy.isdigit():
        if not fancy:
            return(None)
        fancy = fancy[1:]
    return(fancy)

def fancify(fname):
    with open(settings.DB_PATH, 'r') as read_file:
        parsed = json.load(read_file)
        read_file.close()
    with open(settings.DB_PATH, 'w') as read_file:
        json.dump(parsed, read_file, indent=4, sort_keys=True)
