#strips off discord formatting so even @'s of channels can still be used for command inputs
from discord.ext import commands

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
