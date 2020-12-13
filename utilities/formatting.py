import json

from datetime import datetime
from discord.ext import commands
from math import trunc
from re import findall
from string import ascii_letters, digits
from utilities import settings

settings = settings.config("settings.json")
allowed_char = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ "
trans_table = {49 : 105, 51 : 101, 52 : 97, 53 : 115, 55 : 116, 56 : 98, 48 : 111}

def get_from_in(bot, ctx, mode, inp): #Really wishing python had switch cases.
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
    elif mode == 'emo':
        try:
            out = bot.get_emoji(int(inp))
        except ValueError:
            out = bot.get_emoji(int(strip(inp)))
    return out

def strip(fancy):
    fancy = fancy[2:-1]
    while not fancy.isdigit():
        if not fancy:
            return(None)
        fancy = fancy[1:]
    return(fancy)

def simplify(string):
    out = ""
    for char in string:
        if char in allowed_char:
            if char == " " and out[-1] == "s":
                out = out[0:-1] + char
            else: 
                out = out + char
    if out[-1] == "s":
        out = out[:-1]
    return out.lower().translate(trans_table)

def fancify(fname):
    with open(fname, 'r') as read_file:
        parsed = json.load(read_file)
        read_file.close()
    with open(fname, 'w') as read_file:
        json.dump(parsed, read_file, indent=4, sort_keys=True)

def datetime_difference(pastest, presentest=None):
    if presentest:
        dt = presentest - pastest
        offset = dt.seconds + (dt.days * 60*60*24)

        delta_ms = trunc(dt.microseconds / 1000)
        delta_s = trunc(offset % 60)
        offset /= 60
        delta_mi = trunc(offset % 60)
        offset /= 60
        delta_h = trunc(offset % 24)
        offset /= 24
        delta_d = trunc(offset % 30)
        offset /= 30 #I know months aren't standard to 30 days, I also don't need that level of accuracy if it's in the range of months
        delta_mo = trunc(offset % 12)
        offset /= 12
        delta_y = trunc(offset)
    
    else:
        raise(ValueError("Must supply presentest"))
    
    if delta_y >= 1:
        return(f'{delta_y} year(s), {delta_mo} month(s), {delta_d} day(s)')

    elif delta_mo >= 1:
        return(f'{delta_mo} month(s), {delta_d} day(s), {delta_h} hour(s)')

    elif delta_d >= 1:
        return(f'{delta_d} day(s), {delta_h} hour(s), {delta_mi} minute(s)')

    elif delta_h >= 1:
        return(f'{delta_h} hour(s), {delta_mi} minute(s), {delta_s} second(s)')

    elif delta_mi >= 1:
        return(f'{delta_mi} minute(s), {delta_s} second(s)')
        
    else:
        return(f'{delta_s} second(s), {delta_ms} millisecond(s)')

def date_difference(pastest, presentest=None):
    if presentest:
        dt = presentest - pastest
        offset = dt.days

        delta_d = trunc(offset % 30)
        offset /= 30
        delta_m = trunc(offset % 12)
        offset /= 12
        delta_y = trunc(offset)

    else:
        raise(ValueError("Must supply presentest"))
    
    if delta_y >= 1:
        return(f'{delta_y} year(s), {delta_m} month(s), {delta_d} day(s)')
    
    elif delta_m >= 1:
        return(f'{delta_m} month(s), {delta_d} day(s)')
    
    elif delta_d > 1:
        return(f'{delta_d} days')

    else:
        return('Today')

def url_find(string):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = findall(regex,string)       
    return [x[0] for x in url]

def is_ascii(s):
    return all(ord(c) < 128 for c in s)