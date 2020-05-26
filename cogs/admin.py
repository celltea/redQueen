import discord
import os 
import asyncio
import math
import sys

from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, timedelta
from utilities import datedifference, formatting



#env variables
load_dotenv()
COGS = os.getenv('COG_PATH')

TURNOVER_CHANNEL_ID = int(os.getenv('TURNOVER_CHANNEL_ID'))
JOIN_CHANNEL_ID = int(os.getenv('JOIN_CHANNEL_ID'))

MUTED_ROLE_ID = int(os.getenv('MUTED_ROLE_ID'))
UNVERIFIED_ROLE_ID = int(os.getenv('UNVERIFIED_ROLE_ID'))
VERIFIED_ROLE_ID = int(os.getenv('VERIFIED_ROLE_ID'))
INTERVIEWER_ROLE_ID = int(os.getenv('INTERVIEWER_ROLE_ID'))

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = ''
        self.queue_position = 0

    @commands.command(help='staff only: (member) (duration in minutes)')
    @commands.has_permissions(administrator=True)
    async def timeout(self, ctx, user_id, duration):
        try:
            member = discord.utils.get(ctx.guild.members, id=int(user_id))
        except ValueError:
            member = discord.utils.get(ctx.guild.members, id=int(formatting.strip(user_id)))

        role = ctx.guild.get_role(MUTED_ROLE_ID)

        mute_embed = discord.Embed(description=f'**{member.mention} was timed out for {duration} minutes**', color=0xff6464)
        mute_embed.set_author(name=f'{member.name}#{member.discriminator}', icon_url=member.avatar_url)
        mute_embed.set_thumbnail(url=member.avatar_url)
        mute_embed.timestamp = ctx.message.created_at

        await member.add_roles(role, reason='timeout command: timing out user', atomic=True)
        await ctx.send(embed=mute_embed)

        await asyncio.sleep(60*int(duration))

        unmute_embed = discord.Embed(description=f'**{member.mention} is no longer timed out**', color=0x64ff64)
        unmute_embed.set_author(name=f'{member.name}#{member.discriminator}', icon_url=member.avatar_url)
        unmute_embed.set_thumbnail(url=member.avatar_url)
        unmute_embed.timestamp = ctx.message.created_at

        await member.remove_roles(role, reason='timeout command: removing timeout', atomic=True)
        await ctx.send(embed=unmute_embed)

    @commands.command(help='staff only: (role)')
    @commands.has_permissions(administrator=True)
    async def cleanupgen(self, ctx, role_id):
        try:
            role = ctx.guild.get_role(int(role_id))
        except ValueError:
            role = ctx.guild.get_role(int(formatting.strip(role_id)))

        member_list = role.members
        cleanup_file = open('cleanup_file.csv', 'w+')
        i = 0

        while i < len(member_list):
            cleanup_file.write(f'{member_list[i].name.encode(encoding="ascii", errors="replace")}, "{member_list[i].id}", {member_list[i].joined_at}\n')
            i = i + 1

        await ctx.send(content=f'Please see the console. There were {i} user(s)', file=discord.File(fp='cleanup_file.csv', filename='cleanup_file.csv'))
        cleanup_file.close()
    
    @commands.command(help='staff only: (user) (reason)')
    @commands.has_permissions(administrator=True)
    async def kick(self, ctx, target, *, reason):
        try:
            user = self.bot.get_user(int(target))
        except ValueError:
            user = self.bot.get_user(int(formatting.strip(target)))

        embed = discord.Embed(title='Server Kick', color=0xff6464)
        embed.set_author(name=f'{user.name}#{user.discriminator}', icon_url=user.avatar_url)
        embed.add_field(name='Target', value=user.mention, inline=True)
        embed.add_field(name='Moderator', value=ctx.author.mention, inline=True)
        embed.add_field(name='Reason', value=reason, inline=False)
        embed.timestamp = ctx.message.created_at

        await ctx.guild.kick(user, reason=reason)
        await ctx.send(embed=embed) 

    @commands.command(help='staff only: (user) (reason)')
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx, target, *, reason):
        try:
            user = self.bot.get_user(int(target))
        except ValueError:
            user = self.bot.get_user(int(formatting.strip(target))) 

        embed = discord.Embed(title='Server Ban', color=0xff6464)
        embed.set_author(name=f'{user.name}#{user.discriminator}', icon_url=user.avatar_url)
        embed.add_field(name='Target', value=user.mention, inline=True)
        embed.add_field(name='Moderator', value=ctx.author.mention, inline=True)
        embed.add_field(name='Reason', value=reason, inline=False)
        embed.timestamp = ctx.message.created_at

        await ctx.guild.ban(user, reason=reason, delete_message_days=0)
        await ctx.send(embed=embed)
    
    @commands.command(help='staff only: (quantity) (first joiner post to ban) (reason)')
    @commands.has_permissions(administrator=True)
    async def massban(self, ctx, quantity, start, *, reason):

        timestamp = discord.utils.snowflake_time(int(start))
        channel = self.bot.get_channel(JOIN_CHANNEL_ID)
        timestamp = timestamp + timedelta(milliseconds=1)
        targets = []
        quantity = int(quantity)
        i = 0

        async for message in channel.history(limit=quantity, before=timestamp):
            targets.append(message.author)
            i += 1

        for user in targets:
            await ctx.guild.ban(user, reason=reason, delete_message_days=0)

        embed = discord.Embed(description=f'**{i} users have been banned**',color=0xff6464)
        embed.set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.avatar_url)
        embed.timestamp = ctx.message.created_at

        await ctx.send(embed=embed)
    
    @commands.command(help='staff only: see detailed help command')
    @commands.has_permissions(administrator=True)
    async def cleanupkick(self, ctx, *, id_post):
        id_post = id_post + '-'
        id_build = ''
        user_ids = []
        i = 0
        user = None

        for char in id_post:

            if char == '\n' or char == '-':
                user_ids.append(id_build)
                id_build = ''
            else:
                id_build = id_build + char

        for user_id in user_ids:
            user = self.bot.get_user(int(user_id))
            i = i + 1
            await ctx.guild.kick(user, reason='Cleanup kick')
        
        embed = discord.Embed(description=f'**{i} members were kicked**', color=0xff6464)
        embed.set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.avatar_url)
        embed.add_field(name='Last kicked', value=f'{user.name}#{user.discriminator}')
        embed.add_field(name='ID', value=user.id)
        embed.timestamp = ctx.message.created_at  
        
        try:
            await ctx.message.delete()

        except discord.Forbidden:
            pass
        await ctx.send(embed=embed)

    @commands.command(help='Interviewer only: (user 1) (user 2) ...')
    @commands.has_role(INTERVIEWER_ROLE_ID)
    async def createqueue(self, ctx, *, string):
        user_ids = []
        id_build = ''
        string = string + '-' #can't add the final id without a space so we append some other symbol that we also check for instead

        for char in string:

            if char == ' ' or char == '-':
                user_ids.append(id_build)
                id_build = ''
            else:
                id_build = id_build + char

        self.queue = '```\nQueue--\n'
        self.queue_position = 1

        for user in user_ids:
            try:
                userobj = self.bot.get_user(int(user))
            except ValueError:
                userobj = self.bot.get_user(int(formatting.strip(user)))

            self.queue = self.queue + f'{self.queue_position}. {userobj.name}#{userobj.discriminator}\n'
            self.queue_position = self.queue_position + 1

        self.queue = self.queue + '```'
        await ctx.message.delete()
        await ctx.send(f'{self.queue}')
    
    @commands.command(help='Interviewer only: (user 1) (user 2) ...')
    @commands.has_role(INTERVIEWER_ROLE_ID)
    async def addqueue(self, ctx, *, string):
        self.queue = self.queue[0:len(self.queue)-3]

        user_ids = []
        id_build = ''
        string = string + '-'

        for char in string:

            if char == ' ' or char == '-':
                user_ids.append(id_build)
                id_build = ''
            else:
                id_build = id_build + char

        for user in user_ids:
            try:
                userobj = self.bot.get_user(int(user))
            except ValueError:
                userobj = self.bot.get_user(int(formatting.strip(user)))
                
            self.queue = self.queue + f'{self.queue_position}. {userobj.name}#{userobj.discriminator}\n'
            self.queue_position = self.queue_position + 1
        
        self.queue = self.queue + '```'
        await ctx.message.delete()
        await ctx.send(f'{self.queue}')
    
    @commands.command(help='Interviewer only: noarg')
    @commands.has_role(INTERVIEWER_ROLE_ID)
    async def queue(self, ctx):
        try:
            await ctx.send(f'{self.queue}')
            await ctx.message.delete()
        except discord.HTTPException:
            await ctx.send('The queue is currently empty (probably)')

    @commands.command(help='(number of messages)')
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx, num):
        i = 0
        num = int(num) + 1 #accounting for the command usage
        channel = ctx.channel

        if num // 100 >= 1:
            i = num // 100
        r = num % 100

        while i > 0:
            messages = []
            async for message in channel.history(limit=100):
                messages.append(message)
            await ctx.channel.delete_messages(messages)
            i = i - 1

        messages = []
        async for message in channel.history(limit=r):
            messages.append(message)
        await ctx.channel.delete_messages(messages)
        
        embed = discord.Embed(title='Clear', description=f'{num - 1} messages deleted', color=0x64b4ff)
        embed.set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed, delete_after=5)

    #only works on cogs, will not apply any module updates
    @commands.command(help='no arg: WARNING reloads all cogs')
    @commands.has_permissions(administrator=True)
    async def reload(self, ctx):
        for file in os.listdir(COGS):
            if file.endswith('.py'):
                name = file[:-3]
                self.bot.reload_extension(f"cogs.{name}")
        await ctx.send(content='cogs reloaded')
    
    @commands.command(help='no arg: WARNING stops bot')
    @commands.has_permissions(administrator=True)
    async def stop(self, ctx):
        await ctx.send(content='shutting down')
        sys.exit()



def setup(bot):
    bot.add_cog(Admin(bot))