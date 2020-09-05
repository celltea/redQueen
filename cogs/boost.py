import discord

from discord.ext import commands
from utilities import formatting, settings
from tinydb import TinyDB, Query

settings = settings.config("settings.json")


class Boost(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(help='boosters only: (channel) (contents of message)')
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
    @commands.cooldown(rate=1, per=5)
    async def role(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Please choose to edit either the **color** or **name** of your role')

    @role.command()
    async def color(self, ctx, hex_color):
        db = TinyDB(settings.DB_PATH + str(ctx.author.id) + '.json')
        table = db.table('boost')
        member = Query()
        role_id = table.get(member.role_id != None)['role_id']

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
            await role.edit(position=category.position - 1)

            path = settings.DB_PATH + str(ctx.author.id) + '.json'
            db = TinyDB(path)
            member = Query()
            table = db.table('boost')

            table.upsert({'role_id' : role.id}, member.role_id != None) #If conditional is True: update. If False: insert.
            formatting.fancify(path)
        await ctx.send(content=f'{role.mention}\nHere\'s your new role!')   

    
    @role.command()
    async def name(self, ctx, *, name):
        db = TinyDB(settings.DB_PATH + str(ctx.author.id) + '.json')
        table = db.table('boost')
        member = Query()
        role_id = table.get(member.role_id != None)['role_id'] 

        role = ctx.guild.get_role(role_id) 

        try:
            await role.edit(name=name)
        except AttributeError:
            category = ctx.guild.get_role(settings.BOOSTER_CATEGORY)
            role = await ctx.guild.create_role(name=name, mentionable=True, reason=f'{ctx.author.name} booster role create')
            await ctx.author.add_roles(role)
            await role.edit(position=category.position - 1)

            path = settings.DB_PATH + str(ctx.author.id) + '.json'
            db = TinyDB(path)
            member = Query()
            table = db.table('boost')

            table.upsert({'role_id' : role.id}, member.role_id != None) #If conditional is True: update. If False: insert.
            formatting.fancify(path)
        await ctx.send(content=f'{role.mention}\nHere\'s your new role!')   


def setup(bot):
    bot.add_cog(Boost(bot))