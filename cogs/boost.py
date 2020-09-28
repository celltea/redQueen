import discord
import asyncio

from discord.ext import commands
from utilities import formatting, settings
from tinydb import TinyDB, Query

settings = settings.config("settings.json")


class Boost(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(help='Booster only: (channel) (contents of message)')
    @commands.has_role(settings.VERIFIED_ROLE_ID)
    @commands.check_any(commands.has_role(settings.BOOSTER_ROLE_ID), commands.has_role(settings.STAFF_ROLE_ID))
    async def say(self, ctx, channel, *, msg):
        channel = formatting.getfromin(self.bot, ctx, "cha", channel)
        log_channel = self.bot.get_channel(int(settings.SAY_LOG_ID))

        if ctx.author.permissions_in(channel).send_messages and len(ctx.message.role_mentions) == 0 or '@everyone' not in msg or '@here' not in msg: #checking if there are any mentions in the message:
            if len(ctx.message.role_mentions) != 0 or '@everyone' in msg or '@here' in msg: #checking if there are any mentions in the message
                await ctx.send(content='You cannot mention roles with this command')
                return
            else:
                await log_channel.send(f'__{ctx.message.author.name}:__ {msg} **in** *{channel.name}*')
                await channel.send(f'{msg}')

            try:
                await ctx.message.delete()

            except discord.Forbidden:
                pass
        else:
            await ctx.send(f'You\'re only allowed to use this command in channels you may speak in! You can\'t speak in **{channel.name}**')

    @commands.group()
    @commands.has_role(settings.VERIFIED_ROLE_ID)
    @commands.check_any(commands.has_role(settings.BOOSTER_ROLE_ID), commands.has_role(settings.STAFF_ROLE_ID))
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.member)
    async def boost(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Please choose what you\'d like to edit: __role__ or __emote__')
    
    @boost.group()
    #@commands.has_role(settings.VERIFIED_ROLE_ID)
    #@commands.check_any(commands.has_role(settings.BOOSTER_ROLE_ID), commands.has_role(settings.STAFF_ROLE_ID))
    #@commands.cooldown(rate=1, per=5, type=commands.BucketType.member)
    async def role(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Please choose to edit either the __color__ or __name__ of your role')

    @role.command(help='Booster only: (hexcode color)')
    async def color(self, ctx, hex_color):
        db = TinyDB(settings.DB_PATH + str(ctx.author.id) + '.json')
        table = db.table('boost')
        member = Query()
        try:
            role_id = table.get(member.role_id != None)['role_id']
        except TypeError:
            category = ctx.guild.get_role(settings.BOOSTER_CATEGORY)
            role = await ctx.guild.create_role(name=str(ctx.author.id), mentionable=True, color=discord.Color(hexadecimal), reason=f'{ctx.author.name} booster role create')
            role_id = role.id
            await ctx.author.add_roles(role)
            await asyncio.sleep(1)
            await role.edit(position=category.position - 1)

            path = settings.DB_PATH + str(ctx.author.id) + '.json'
            db = TinyDB(path)
            member = Query()
            table = db.table('boost')

            table.upsert({'role_id' : role.id}, member.role_id != None) #If conditional is True: update. If False: insert.
            formatting.fancify(path)

        role = ctx.guild.get_role(role_id) 

        if hex_color[0] == '#':
            hex_color = hex_color[1:]
    
        hexadecimal = int(hex_color.lower(), 16)
        
        try:
            await role.edit(color=discord.Color(hexadecimal))
        except AttributeError:
            category = ctx.guild.get_role(settings.BOOSTER_CATEGORY)
            role = await ctx.guild.create_role(name=str(ctx.author.id), mentionable=True, color=discord.Color(hexadecimal), reason=f'{ctx.author.name} booster role create')
            await ctx.author.add_roles(role)
            await asyncio.sleep(1)
            await role.edit(position=category.position - 1)

            path = settings.DB_PATH + str(ctx.author.id) + '.json'
            db = TinyDB(path)
            member = Query()
            table = db.table('boost')

            table.upsert({'role_id' : role.id}, member.role_id != None) #If conditional is True: update. If False: insert.
            formatting.fancify(path)
        await ctx.send(content=f'{role.mention}\nHere\'s your new custom role!')   

    
    @role.command(help='Booster only: (role name)')
    async def name(self, ctx, *, name):
        path = settings.DB_PATH + str(ctx.author.id) + '.json'
        db = TinyDB(path)
        table = db.table('boost')
        member = Query()
        try:
            role_id = table.get(member.role_id != None)['role_id'] 
        except TypeError:
            category = ctx.guild.get_role(settings.BOOSTER_CATEGORY)
            role = await ctx.guild.create_role(name=str(ctx.author.id), mentionable=True, reason=f'{ctx.author.name} booster role create')
            role_id = role.id
            await ctx.author.add_roles(role)
            await asyncio.sleep(1)
            await role.edit(position=category.position - 1)

            db = TinyDB(path)
            member = Query()
            table = db.table('boost')

            table.upsert({'role_id' : role.id}, member.role_id != None) #If conditional is True: update. If False: insert.
            formatting.fancify(path)

        role = ctx.guild.get_role(role_id) 
        name = name.replace('\n', " ")
        namet = name.strip().lower()

        for role_temp in ctx.guild.roles:
            if role_temp.name.strip().lower() == namet or namet in settings.NAME_BLACKLIST:
                await ctx.send('A role with that name already exists. Please choose another.')
                return

        try:
            await role.edit(name=name)
        except AttributeError:
            category = ctx.guild.get_role(settings.BOOSTER_CATEGORY)
            role = await ctx.guild.create_role(name=name, mentionable=True, reason=f'{ctx.author.name} booster role create')
            await ctx.author.add_roles(role)
            await asyncio.sleep(1)
            await role.edit(position=category.position - 1)

            db = TinyDB(path)
            member = Query()
            table = db.table('boost')

            table.upsert({'role_id' : role.id}, member.role_id != None) #If conditional is True: update. If False: insert.
            formatting.fancify(path)

        await ctx.send(content=f'{role.mention}\nHere\'s your new custom role!')

    @boost.command(help='Booster only: (emote)')
    async def emote(self, ctx, emote):
        try:
            emote = formatting.getfromin(self.bot, ctx, "emo", emote)
        except TypeError:
            await ctx.send(content='Please select an emote from this server')   
            return
        path = settings.DB_PATH + str(ctx.author.id) + '.json'
        db = TinyDB(path)
        table = db.table('boost')
        member = Query()
        
        try:
            emote_id = table.get(member.emote_id != None)['emote_id']
        except TypeError: 
            #make the emote portion in the DB
            db = TinyDB(path)
            member = Query()
            table = db.table('boost')

            try:
                table.upsert({'emote_id' : emote.id}, member.emote_id != None)
            except AttributeError:
                await ctx.send(content='Please select an emote from this server')
                return
                
            formatting.fancify(path)

            emote_id = table.get(member.emote_id != None)['emote_id']
        
        try:
            if emote_id != emote.id:
                table.upsert({'emote_id' : emote.id}, member.emote_id != None)
        except AttributeError:
            await ctx.send(content='Please select an emote from this server')
            return

        await ctx.send(content=f'{emote}\nHere\'s your new auto-react emote!')


def setup(bot):
    bot.add_cog(Boost(bot))