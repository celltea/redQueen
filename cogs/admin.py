import discord
import os 
import asyncio
import math

from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime, timedelta
from utilities import datedifference, formatting, settings

settings = settings.config("settings.json")


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = ''
        self.queue_position = 0


    @commands.command(help='Interviewer only: (member) (duration in minutes)')
    @commands.check_any(commands.has_role(settings.INTERVIEWER_ROLE_ID), commands.has_role(settings.STAFF_ROLE_ID))
    async def timeout(self, ctx, user, duration):
        member = formatting.getfromin(self.bot, ctx, 'mem', user)
        verified = ctx.guild.get_role(settings.VERIFIED_ROLE_ID)
        staff = ctx.guild.get_role(settings.STAFF_ROLE_ID)

        if staff not in ctx.author.roles and verified in member.roles:
            await ctx.send(content='Interviewers cannot target Verified users with this command')
        else:

            role = ctx.guild.get_role(settings.MUTED_ROLE_ID)

            mute_embed = discord.Embed(description=f'**{member.mention} was timed out for {duration} minute(s)**', color=0xff6464)
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


    @commands.command(help='Staff only: (role)')
    @commands.has_permissions(administrator=True)
    async def cleanupgen(self, ctx, role):
        role = formatting.getfromin(self.bot, ctx, "rol", role)
        member_list = role.members
        cleanup_file = open(settings.CLEANUP_PATH, 'w+')
        i = 0
        
        with open(settings.CLEANUP_PATH, 'w+') as cleanup_file:
            while i < len(member_list):
                cleanup_file.write(f'{member_list[i].name.encode(encoding="ascii", errors="replace")}, "{member_list[i].id}", {member_list[i].joined_at}\n')
                i = i + 1
        await ctx.send(content=f'Please see the console. There were {i} user(s)', file=discord.File(fp=settings.CLEANUP_PATH, filename=settings.CLEANUP_PATH))
    

    @commands.command(help='Interviewer only: (user) (reason)')
    @commands.check_any(commands.has_role(settings.INTERVIEWER_ROLE_ID), commands.has_role(settings.STAFF_ROLE_ID))
    async def kick(self, ctx, member, *, reason = None):
        member = formatting.getfromin(self.bot, ctx, "mem", member)
        
        verified = ctx.guild.get_role(settings.VERIFIED_ROLE_ID)
        staff = ctx.guild.get_role(settings.STAFF_ROLE_ID)
        if staff not in ctx.author.roles and verified in member.roles:
            await ctx.send(content='Interviewers cannot target Verified users with this command')

        else:
            embed = discord.Embed(title='Server Kick', color=0xff6464)
            embed.set_author(name=f'{member.name}#{member.discriminator}', icon_url=member.avatar_url)
            embed.add_field(name='Target', value=member.mention, inline=True)
            embed.add_field(name='Moderator', value=ctx.author.mention, inline=True)
            embed.timestamp = ctx.message.created_at
            
            try:
                await member.create_dm()
                await member.dm_channel.send(content=f'You have been kicked from {ctx.guild.name} with reason: __{reason}__')
            except discord.Forbidden:
                embed.add_field(value='Unable to DM target', inline=True)

            if reason:
                embed.add_field(name='Reason', value=reason, inline=False)
                await member.kick(reason=reason)
            else:
                embed.add_field(name='Reason', value='none', inline=False)
                await member.kick(reason='none')

            await member.kick(reason=reason)
            await ctx.send(embed=embed) 


    #temporarily gross looking code, I'll clean it up later, I broke it with my last update so this is a temporary fix
    @commands.command(help='Interviewer only: (user) (reason)')
    @commands.check_any(commands.has_role(settings.INTERVIEWER_ROLE_ID), commands.has_role(settings.STAFF_ROLE_ID))
    async def ban(self, ctx, userin, *, reason = None):
        user = formatting.getfromin(self.bot, ctx, "use", userin)
        member = formatting.getfromin(self.bot, ctx, "mem", userin)
        verified = ctx.guild.get_role(settings.VERIFIED_ROLE_ID)
        staff = ctx.guild.get_role(settings.STAFF_ROLE_ID)

        try:
            if staff not in ctx.author.roles and verified in member.roles:
                await ctx.send(content='Interviewers cannot target Verified users with this command')
                return
        except AttributeError:
            pass  
        
        embed = discord.Embed(title='Server Ban', color=0xff6464)
        embed.set_author(name=f'{user.name}#{user.discriminator}', icon_url=user.avatar_url)
        embed.add_field(name='Target', value=user.mention, inline=True)
        embed.add_field(name='Moderator', value=ctx.author.mention, inline=True)          
        embed.timestamp = ctx.message.created_at

        if reason:
            embed.add_field(name='Reason', value=reason, inline=False)
            await ctx.guild.ban(user, reason=reason, delete_message_days=0)
        else:
            embed.add_field(name='Reason', value='none', inline=False)
            await ctx.guild.ban(user, reason='none', delete_message_days=0)

        await ctx.send(embed=embed)
    

    @commands.command(help='Interviewer only: (user)')
    @commands.check_any(commands.has_role(settings.INTERVIEWER_ROLE_ID), commands.has_role(settings.STAFF_ROLE_ID))
    async def unban(self, ctx, user):
        user = formatting.getfromin(self.bot, ctx, "use", user)

        embed = discord.Embed(title='Server Unban', color=0x64ff64)
        embed.set_author(name=f'{user.name}#{user.discriminator}', icon_url=user.avatar_url)
        embed.add_field(name='Target', value=user.mention, inline=True)
        embed.add_field(name='Moderator', value=ctx.author.mention, inline=True)
        embed.timestamp = ctx.message.created_at

        await ctx.guild.unban(user)
        await ctx.send(embed=embed)
    

    @commands.command(help='Staff only: (quantity) (first joiner post to ban) (reason)')
    @commands.has_permissions(administrator=True)
    async def massban(self, ctx, num, start, *, reason):
        timestamp = discord.utils.snowflake_time(int(start)) + timedelta(milliseconds=1)
        channel = self.bot.get_channel(settings.JOIN_CHANNEL_ID)
        targets = []
        num = int(num)

        async for message in channel.history(limit=quantity, before=timestamp):
            targets.append(message.author)

        for user in targets:
            await ctx.guild.ban(user, reason=reason, delete_message_days=0)

        embed = discord.Embed(description=f'**{num} users have been banned**',color=0xff6464)
        embed.set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.avatar_url)
        embed.timestamp = ctx.message.created_at

        await ctx.send(embed=embed)
    

    @commands.command(help='Staff only: see detailed help command')
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
    @commands.has_role(settings.INTERVIEWER_ROLE_ID)
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
            user = formatting.getfromin(self.bot, ctx, "use", user)

            self.queue = self.queue + f'{self.queue_position}. {user.name}#{user.discriminator}\n'
            self.queue_position = self.queue_position + 1

        self.queue = self.queue + '```'

        await ctx.message.delete()
        await ctx.send(f'{self.queue}')
    

    @commands.command(help='Interviewer only: (user 1) (user 2) ...')
    @commands.has_role(settings.INTERVIEWER_ROLE_ID)
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
            user = formatting.getfromin(self.bot, ctx, "use", user)
                
            self.queue = self.queue + f'{self.queue_position}. {user.name}#{user.discriminator}\n'
            self.queue_position = self.queue_position + 1
        
        self.queue = self.queue + '```'
        await ctx.message.delete()
        await ctx.send(f'{self.queue}')
    

    @commands.command(help='Interviewer only: noarg')
    @commands.has_role(settings.INTERVIEWER_ROLE_ID)
    async def queue(self, ctx):
        try:
            await ctx.send(f'{self.queue}')
            await ctx.message.delete()
        except discord.HTTPException:
            await ctx.send('The queue is currently empty (probably)')


    @commands.command(help='(number of messages)')
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx, num):
        num = int(num) + 1 #accounting for the command usage
        i = num // 100
        r = num % 100

        while i > 0:
            messages = []
            async for message in ctx.channel.history(limit=100):
                messages.append(message)
            await ctx.channel.delete_messages(messages)
            i = i - 1

        messages = []
        async for message in ctx.channel.history(limit=r):
            messages.append(message)
        await ctx.channel.delete_messages(messages)

        embed = discord.Embed(title='Clear', description=f'{num - 1} messages deleted', color=0x64b4ff)
        embed.set_author(name=f'{ctx.author.name}#{ctx.author.discriminator}', icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed, delete_after=3)  


    @commands.command(help='Interviewer only: (member)')
    @commands.has_role(settings.INTERVIEWER_ROLE_ID)
    async def welcome(self, ctx, *, member):
        member = formatting.getfromin(self.bot, ctx, "mem", member)
        unverified_role = ctx.guild.get_role(settings.UNVERIFIED_ROLE_ID)
        verified_role = ctx.guild.get_role(settings.VERIFIED_ROLE_ID)
        
        await member.remove_roles(unverified_role, reason='user verified')
        await member.add_roles(verified_role, reason='user verified')

        try:
            await member.create_dm()
            await member.dm_channel.send(settings.WELCOME)
        except discord.Forbidden:
            bot_commands = self.bot.get_channel(settings.BOT_COMMANDS_ID)
            await bot_commands.send(content=f'{member.mention}\n{WELCOME}')

        general = self.bot.get_channel(settings.GENERAL_ID)

        embed = discord.Embed(description=f'Welcome to the server {member.mention}!', color=0x64b4ff)
        embed.set_author(name=f'{member.name}#{member.discriminator}', icon_url=member.avatar_url)
        embed.timestamp = ctx.message.created_at

        await general.send(content='@here', embed=embed)


    @commands.command(help='Marinated only: (member)')
    @commands.check_any(commands.has_role(settings.INTERVIEWER_ROLE_ID), commands.has_role(settings.STAFF_ROLE_ID), commands.has_role(settings.MARINATED_ROLE_ID))
    async def mute(self, ctx, member):
        member = formatting.getfromin(self.bot, ctx, "mem", member)
        verified = ctx.guild.get_role(settings.VERIFIED_ROLE_ID)
        staff = ctx.guild.get_role(settings.STAFF_ROLE_ID)

        if staff not in ctx.author.roles and verified in member.roles:
            await ctx.send(content='You cannot target Verified users with your permissions')
        else: 
            muted = ctx.guild.get_role(settings.MUTED_ROLE_ID)

            await member.add_roles(muted)

            embed = discord.Embed(description=f'**{member.mention} has been muted**', color=0xff6464)
            embed.set_author(name=f'{member.name}#{member.discriminator}', icon_url=member.avatar_url)
            embed.set_thumbnail(url=member.avatar_url)
            embed.timestamp = ctx.message.created_at

            await ctx.send(embed=embed)


    @commands.command(help='Marinated only: (member)')
    @commands.check_any(commands.has_role(settings.INTERVIEWER_ROLE_ID), commands.has_role(settings.STAFF_ROLE_ID), commands.has_role(settings.MARINATED_ROLE_ID))
    async def unmute(self, ctx, member):
        member = formatting.getfromin(self.bot, ctx, "mem", member)
        verified = ctx.guild.get_role(settings.VERIFIED_ROLE_ID)
        staff = ctx.guild.get_role(settings.STAFF_ROLE_ID)

        if staff not in ctx.author.roles and verified in member.roles:
            await ctx.send(content='You cannot target Verified users with your permissions')

        else: 
            muted = ctx.guild.get_role(settings.MUTED_ROLE_ID)

            await member.remove_roles(muted)

            embed = discord.Embed(description=f'**{member.mention} has been unmuted**', color=0x64ff64)
            embed.set_author(name=f'{member.name}#{member.discriminator}', icon_url=member.avatar_url)
            embed.set_thumbnail(url=member.avatar_url)
            embed.timestamp = ctx.message.created_at

            await ctx.send(embed=embed)


    async def cleanUpBlock(self, ctx, message_id, channel):
        message = await channel.fetch_message(int(message_id))

        for reaction in message.reactions:
            async for user in reaction.users():
                if type(user) == discord.User:

                    await reaction.remove(user)


    @commands.command(help='Staff only: (# of posts)')
    @commands.has_role(settings.STAFF_ROLE_ID)
    async def cleanuproles_channel(self, ctx, channel, num):
        channel = formatting.getfromin(self.bot, ctx, "cha", channel)

        async for message in channel.history(limit=int(num)):
            await Admin.cleanUpBlock(self, ctx, message.id, channel)


    @commands.command(help='Staff only: (# of posts)')
    @commands.has_role(settings.STAFF_ROLE_ID)
    async def cleanuproles_message(self, ctx, channel, message):
        channel = formatting.getfromin(self.bot, ctx, "cha", channel)

        await Admin.cleanUpBlock(self, ctx, message, channel)
        

def setup(bot):
    bot.add_cog(Admin(bot))