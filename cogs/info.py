import discord
import os 

from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, date
from utilities import formatting, settings
from tinydb import TinyDB, Query

settings = settings.config("settings.json")


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=['userinfo'], help='(member)')
    @commands.has_role(settings.VERIFIED_ROLE_ID)
    async def memberinfo(self, ctx, member):
        member = formatting.getfromin(self.bot, ctx, "mem", member)
        now = datetime.utcnow()

        db = TinyDB(settings.DB_PATH + str(member.id) + '.json')
        table = db.table('information')
        last_seen = table.get(Query().last_seen != None)['last_seen']
        last_seen = datetime.strptime(last_seen, "%Y-%m-%d")
        time_since_message = formatting.date_difference(last_seen, datetime.today())

        roles = ''  
        time_since_created = formatting.datetime_difference(member.created_at, now)
        time_since_joined = formatting.datetime_difference(member.joined_at, now)
        try:
            time_since_nitro = formatting.datetime_difference(member.premium_since, now)
        except TypeError:
            time_since_nitro = "None"

        for role in member.roles:
            roles = roles + f'{role.mention}, '
        roles = roles[:-2]

        embed = discord.Embed(title='User info', description=member.mention, color=0x64b4ff)
        embed.set_author(name=f'{member.name}#{member.discriminator}', icon_url=member.avatar_url)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name='User', value=f'**{member.name}#{member.discriminator}**', inline=True)
        embed.add_field(name='Nickname', value=member.display_name, inline=True)
        embed.add_field(name='ID', value=member.id, inline=True)
        try:
            i = str(member.activity.type).index('.')
            embed.add_field(name='Status', value=f'{str(member.activity.type)[i+1:]} **--** {member.activity.name}')
        except AttributeError:
            embed.add_field(name='Status', value='None')
        embed.add_field(name='Created', value=f'**__{time_since_created}__** - {member.created_at}', inline=False)
        embed.add_field(name='Joined', value=f'**__{time_since_joined}__** - {member.joined_at}', inline=False)
        embed.add_field(name='Last seen', value=f'**__{time_since_message}__** - {last_seen.date()}', inline=False)
        embed.add_field(name='Nitro', value=f'**__{time_since_nitro}__** - {member.premium_since}', inline=False)
        embed.add_field(name='Roles', value=roles, inline=False)

        await ctx.send(embed=embed)   


    @commands.command(help='(role)')
    @commands.has_role(settings.VERIFIED_ROLE_ID)
    async def howmany(self, ctx, role):
        role = formatting.getfromin(self.bot, ctx, "rol", role)

        i = 0

        for member in role.members:
            i = i + 1

        embed = discord.Embed(title='How Many', color=0x64b4ff)
        embed.set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=f'{ctx.author.avatar_url}')
        embed.add_field(name='Role', value=f'{role.mention}')
        embed.add_field(name='Users', value=f'{i}')
        embed.timestamp = ctx.message.created_at

        await ctx.send(embed=embed)


    @commands.command(help='(role)')
    @commands.has_role(settings.VERIFIED_ROLE_ID)
    async def whoin(self, ctx, role):
        role = formatting.getfromin(self.bot, ctx, "rol", role)
        members = ''

        for member in role.members:
            members = members + f'{member.name}#{member.discriminator}, '

        embed = discord.Embed(title='Who In', color=0x64b4ff)
        embed.set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=f'{ctx.author.avatar_url}')
        embed.add_field(name='Role', value=f'{role.mention}', inline=False)
        embed.add_field(name='Users', value=f'{members}')
        embed.timestamp = ctx.message.created_at
            
        try:
            await ctx.send(embed=embed)
        except discord.HTTPException:
            await ctx.send(f'**Error:** Too many users have this role to send the message through discord. Consider using ,cleanupgen instead')


    @commands.command(aliases=['av', 'pfp'], help='(user)')
    @commands.has_role(settings.VERIFIED_ROLE_ID)
    async def avatar(self, ctx, user):
        user = formatting.getfromin(self.bot, ctx, "use", user)

        embed = discord.Embed(title='Avatar', color=0x64b4ff)
        embed.set_author(name=f'{user.name}#{user.discriminator}', icon_url=user.avatar_url)
        embed.set_image(url=user.avatar_url_as(static_format='png', size=512))
        embed.timestamp = ctx.message.created_at

        await ctx.send(embed=embed)


    @commands.command(help=('note: implied target is message above command call, at the moment this command only works on the first reaction (not sure if that means the first in-client or the first by some arbitrary measure)'))
    @commands.has_role(settings.VERIFIED_ROLE_ID)
    async def whoreact(self, ctx):
        react_message = None

        async for message in ctx.channel.history(limit=2):
            if ctx.message != message:
                react_message = message
            pass
        
        message = '```'
        i = 1

        async for user in react_message.reactions[0].users():
            message = message + f'{i}. {user.name}#{user.discriminator}\n'
            i += 1
        message = message + '```'
        
        await ctx.send(content=message)


def setup(bot):
    bot.add_cog(Info(bot))