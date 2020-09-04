import os
import discord
from tinydb import TinyDB, Query


from datetime import datetime, timezone, date
from dotenv import load_dotenv
from discord.ext import commands
from utilities import formatting, settings, dbinteract
from random import randint

settings = settings.config("settings.json")


class Requests(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def test1(self, ctx):
        path = settings.DB_PATH + 'temp' + '.json'
        db = TinyDB(path)
        table = db.table('test')
        member = Query()
        table.upsert({'key2' : 666731127267917835}, member.test_key1 != None)
        formatting.fancify(path)


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def boostsetup(self, ctx):
        member_list = []
        role = ctx.guild.get_role(settings.BOOSTER_ROLE_ID)

        for member in role.members:
            path = settings.DB_PATH + str(member.id) + '.json'
            db = TinyDB(path)
            table = db.table('boost')
            member = Query()
            table.upsert({'role_id' : 'temp'}, member.role_id != None)
            formatting.fancify(path)


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def test2(self, ctx):
        path = settings.DB_PATH + 'temp' + '.json'
        db = TinyDB(path)
        table = db.table('test')
        member = Query()
        table.remove(member.key1 != None)
        formatting.fancify(path) 


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def test3(self, ctx):
        db = TinyDB(settings.DB_PATH + 'temp' + '.json')
        table = db.table('test')
        member = Query()
        test = table.get(member.test_key1 != None)['test_key1'] #Grabs document_id X containing member.y and then finds value corresponding to ['key_str']
        print(test)


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def bunnysetup(self, ctx, *, id_post):
        id_post = id_post + '-'
        id_build = ''
        user_ids = []
        dates = []
        i = 0

        for char in id_post:
            if char == '\n' or char == ',':
                if i % 2 == 0:
                    user_ids.append(id_build)
                else:
                    dates.append(id_build)
                id_build = ''
                i = i + 1
            else:
                id_build = id_build + char
        
        i = 0
        while i < len(user_ids) and i < len(dates): #Doesn't update the DB, only adds to it
            path = settings.DB_PATH + user_ids[i] + '.json'
            db = TinyDB(path)
            member = Query()
            table = db.table('information')
            table.upsert({'last_seen' : dates[i]}, member.last_seen != None)
            i = i + 1
            formatting.fancify(path)
    
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def dbsetup(self, ctx):
        member_list = []
        for member in ctx.guild.members:
            member_list.append(member.id)

        dbinteract.activity_push(member_list, 'before 2020-08-31')
 

    @commands.command(help='noarg: a simple way to tell if the bot is online')
    @commands.has_role(settings.VERIFIED_ROLE_ID)
    async def ping(self, ctx):
        await ctx.send('pong')
    

    @commands.command(help='noarg: laney\'s request')
    @commands.has_role(settings.VERIFIED_ROLE_ID)
    async def bing(self, ctx):
        await ctx.send('bong')


    @commands.command(help='noarg: myka\'s request')
    @commands.has_role(settings.VERIFIED_ROLE_ID)
    async def alice(self, ctx):
        await ctx.send('You\'re all going to die down here.')


    @commands.command(help='noarg: cat\'s request')
    @commands.has_role(settings.VERIFIED_ROLE_ID)
    async def howlong(self, ctx):
        await ctx.send('too long')


    @commands.command(help='noarg: annalina\'s request')
    @commands.has_role(settings.VERIFIED_ROLE_ID)
    async def serverowner(self, ctx):
        await ctx.message.delete(delay=1)


    #negative mod action
    @commands.command(help='no arg')
    @commands.has_permissions(administrator=True)
    async def format1(self, ctx):
        embed = discord.Embed(title='Name of the action', color=0xff6464)
        embed.set_author(name='Target of the action', icon_url='https://i.imgur.com/oKHBjZt.png')
        embed.add_field(name='Category1', value='Body1', inline=True)
        embed.add_field(name='Category2', value='Body2', inline=True)
        embed.add_field(name='Category3', value='Body3', inline=False)
        embed.timestamp = ctx.message.created_at
        embed.set_footer(text='Timestamp of action')

        await ctx.send(content='Negative Moderation Action Template (banning, kicking, timing-out)', embed=embed) 


    #positive mod action
    @commands.command(help='no arg')
    @commands.has_permissions(administrator=True)
    async def format2(self, ctx):
        embed = discord.Embed(title='Name of the action', color=0x64ff64)
        embed.set_author(name='Target of the action', icon_url='https://i.imgur.com/oKHBjZt.png')
        embed.add_field(name='Category1', value='Body1', inline=True)
        embed.add_field(name='Category2', value='Body2', inline=True)
        embed.add_field(name='Category3', value='Body3', inline=False)
        embed.timestamp = ctx.message.created_at
        embed.set_footer(text='Timestamp of action')

        await ctx.send(content='Positive Moderation Action Template (unbanning, ?unkicking?, un-timing-out)', embed=embed)
    

    #neutral info/short response
    @commands.command(help='no arg')
    @commands.has_permissions(administrator=True)
    async def format3(self, ctx):
        embed = discord.Embed(title='Name of the command', color=0x64b4ff)
        embed.set_author(name='Target of the command (if none then user who called the command or potentially empty section)', icon_url='https://i.imgur.com/oKHBjZt.png')
        embed.add_field(name='Category1', value='Body1', inline=True)
        embed.add_field(name='Category2', value='Body2', inline=True)
        embed.add_field(name='Category3', value='Body3', inline=False)
        embed.timestamp = ctx.message.created_at
        embed.set_footer(text='Timestamp of action')

        await ctx.send(content='Information Response Template (userinfo, whoin, howmany), also used for short responses to commands', embed=embed)


    #log
    @commands.command(help='no arg')
    @commands.has_permissions(administrator=True)
    async def format4(self, ctx):
        embed = discord.Embed(description='**(mention user) was (banned/kicked/action taken)', color=0xfefefe)
        embed.set_author(name='Target of the action', icon_url='https://i.imgur.com/oKHBjZt.png')
        embed.set_thumbnail(url='https://i.imgur.com/oKHBjZt.png')
        embed.timestamp = ctx.message.created_at
        embed.set_footer(text='Timestamp of action')

        await ctx.send(content='Logging Template (logged bans, logged kicks, logged...) \n__Color will change dependent on what action is taken__\nAuthor pic and thumbnail will both be the target\'s pfp', embed=embed)


def setup(bot):
    bot.add_cog(Requests(bot))