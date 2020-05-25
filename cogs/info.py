import discord
import os 

from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
from utilities import datedifference, formatting

#env variables
VERIFIED_ROLE_ID = int(os.getenv('VERIFIED_ROLE_ID'))

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(help='(member)')
    @commands.has_role(VERIFIED_ROLE_ID)
    async def userinfo(self, ctx, target):
        try:
            member = ctx.guild.get_member(int(target))
        except ValueError:
            member = ctx.guild.get_member(int(formatting.strip(target)))

        roles = ''  
        time_since_created = datedifference.date_difference(member.created_at, datetime.utcnow())
        time_since_joined = datedifference.date_difference(member.joined_at, datetime.utcnow())
        try:
            time_since_nitro = datedifference.date_difference(member.premium_since, datetime.utcnow())
        except TypeError:
            time_since_nitro = "None as of current"

        for role in member.roles:
            roles = roles + f'{role.mention}, '
        roles = roles[:-2]

        embed = discord.Embed(title='User info', description=member.mention, color=0x64b4ff)
        embed.set_author(name=f'{member.name}#{member.discriminator}', icon_url=member.avatar_url)
        embed.set_thumbnail(url=member.avatar_url)
        embed.add_field(name='User', value=f'**{member.name}#{member.discriminator}**', inline=True)
        embed.add_field(name='Nickname', value=member.display_name, inline=True)
        embed.add_field(name='ID', value=member.id, inline=True)
        embed.add_field(name='Created', value=f'**__{time_since_created}__** - {member.created_at}', inline=False)
        embed.add_field(name='Joined', value=f'**__{time_since_joined}__** - {member.joined_at}', inline=False)
        embed.add_field(name='Nitro', value=f'**__{time_since_nitro}__** - {member.premium_since}', inline=False)
        embed.add_field(name='Roles', value=roles, inline=False)

        await ctx.send(embed=embed)   
        #await ctx.send(f'```ruby\n     User: {member.name}#{member.discriminator} \n Nickname: {member.display_name} \n       ID: {member.id} \n  Created: #{time_since_created} - {member.created_at} \n   Joined: {time_since_joined} - {member.joined_at} \n   Avatar: {member.avatar_url} \n    Nitro: {member.premium_since} \n    Roles: {roles}```')

    @commands.command(help='(role)')
    @commands.has_role(VERIFIED_ROLE_ID)
    async def howmany(self, ctx, role_id):
        try:
            role = ctx.guild.get_role(int(role_id))
        except ValueError:
            role = ctx.guild.get_role(int(formatting.strip(role_id)))

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
    @commands.has_role(VERIFIED_ROLE_ID)
    async def whoin(self, ctx, role_id):
        try:
            role = ctx.guild.get_role(int(role_id))
        except ValueError:
            role = ctx.guild.get_role(int(formatting.strip(role_id)))
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

    @commands.command(aliases=['av'], help='(user)')
    @commands.has_role(VERIFIED_ROLE_ID)
    async def avatar(self, ctx, user_id):
        try:
            user = self.bot.get_user(int(user_id))
        except ValueError:
            user = self.bot.get_user(int(formatting.strip(user_id)))

        embed = discord.Embed(title='Avatar', color=0x64b4ff)
        embed.set_author(name=f'{user.name}#{user.discriminator}', icon_url=user.avatar_url)
        embed.set_image(url=user.avatar_url_as(static_format='png', size=512))
        embed.timestamp = ctx.message.created_at

        await ctx.send(embed=embed)



def setup(bot):
    bot.add_cog(Info(bot))