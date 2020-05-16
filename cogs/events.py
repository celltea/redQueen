import discord
import os
import asyncio
import math

from discord.ext.commands import errors
from discord.ext import commands
from dotenv import load_dotenv
from datetime import datetime
from utilities import datedifference

#env variables
load_dotenv()
GUILD_ID = int(os.getenv('GUILD_ID'))
WELCOME_CHANNEL_ID = int(os.getenv('WELCOME_CHANNEL_ID'))
TURNOVER_CHANNEL_ID = int(os.getenv('TURNOVER_CHANNEL_ID'))
UNVERIFIED_RULES_ID = int(os.getenv('UNVERIFIED_RULES_ID'))
MOD_LOG_ID = int(os.getenv('MOD_LOG_ID'))

UNVERIFIED_ROLE_ID = int(os.getenv('UNVERIFIED_ROLE_ID'))
STAFF_ID = int(os.getenv('STAFF_ROLE_ID'))
GREETER_ID = int(os.getenv('GREETER_ROLE_ID'))
JOINER_ROLE_ID = int(os.getenv('JOINER_ROLE_ID'))
VERIFIED_ROLE_ID = int(os.getenv('VERIFIED_ROLE_ID'))

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user.name} has connected succesfully!')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(TURNOVER_CHANNEL_ID)
        user = self.bot.get_user(member.id)
        await channel.send(f':blue_heart: **__Joined:__** {user.mention} aka *{user.name}#{member.discriminator}* __\'{member.id}\'__ ')  
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.bot.get_channel(TURNOVER_CHANNEL_ID)
        user = self.bot.get_user(member.id)
        verified_role = member.guild.get_role(VERIFIED_ROLE_ID)

        if VERIFIED_ROLE_ID in member.roles:
            await channel.send(f':heart: **__Left:__** {user.mention} aka *{user.name}#{member.discriminator}* __\'{member.id}\'__. We\'ll miss you! :heart:') 
        else:
            await channel.send(f':heart: **__Left:__** {user.mention} aka *{user.name}#{member.discriminator}* __\'{member.id}\'__') 

#    @commands.Cog.listener()
#    async def on_message_delete(self, message):
#        unverified_role = message.guild.get_role(UNVERIFIED_ROLE_ID)
#
#        if unverified_role in message.author.roles:
#
#            async for entry in message.guild.audit_logs(limit=1):
#                latest = entry
#
#            difference = datetime.utcnow() - latest.created_at
#            if message.author == latest.target and difference.total_seconds() <= 3:
#                pass
#
#            else:
#                channel = self.bot.get_channel(MOD_LOG_ID)
#                await channel.send(f'__{message.author}__ deleted: {message.content}')
#        else:
#            pass
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        joiner_role = before.guild.get_role(JOINER_ROLE_ID)
        unverified_role = before.guild.get_role(UNVERIFIED_ROLE_ID)
        #checking when zira removes the joiner role to send the welcome message

        if joiner_role in before.roles:

            if joiner_role not in after.roles and unverified_role in after.roles:
                channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
                staff_role = after.guild.get_role(STAFF_ID)
                greeter_role = after.guild.get_role(GREETER_ID)
                welcome_channel = self.bot.get_channel(WELCOME_CHANNEL_ID)
                unverified_rules = self.bot.get_channel(UNVERIFIED_RULES_ID)
                
                elapsed_time = datedifference.date_difference(after.joined_at, datetime.utcnow())
                difference = datetime.utcnow() - after.joined_at
                elapsed_seconds = difference.total_seconds()

                if elapsed_seconds <= 1:
                    await after.create_dm()
                    await after.dm_channel.send(f'You have automatically been banned from the server for spending too little time reading the rules.')
                    await welcome_channel.send(f'**{after.name}#{after.discriminator}** has been banned from the server for spending *{math.trunc(elapsed_seconds)} seconds* reading the rules.')
                    await after.ban(delete_message_days=0)

                else:
                    await welcome_channel.send(f'Welcome to {after.guild.name}, {after.mention} Please please please make sure you\'ve read over our {unverified_rules.mention}. You should be greeted by our {greeter_role.mention}s shortly. \nAdditionally if you have any questions feel free to ask {staff_role.mention}. I promise we don\'t bite :purple_heart: \nYou took *{elapsed_time}* to read the rules. ')

    #CATCHING ERRORS... THIS IS GONNA SUCK
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        print(error)
        if isinstance(error, errors.MissingRequiredArgument):
            await ctx.send(f'**Error:** {error} \n**-**It looks like you were missing a few arguments there')
        elif isinstance(error, errors.BadArgument):
            await ctx.send(f'**Error:** {error} \n**-**It looks like the argument you gave me wasn\'t quite what I was looking for')
        elif isinstance(error, errors.PrivateMessageOnly):
            await ctx.send(f'**Error:** {error} \n**-**This only works in a direct message')
        elif isinstance(error, errors.NoPrivateMessage):
            await ctx.send(f'**Error:** {error} \n**-**This doesn\'t work in a direct message')
        elif isinstance(error, errors.CommandNotFound):
            await ctx.send(f'**Error:** {error} \n**-**I don\'t have any commands with that name')
        elif isinstance(error, errors.DisabledCommand):
            await ctx.send(f'**Error:** {error} \n**-**This command is currently disabled')
        elif isinstance(error, errors.TooManyArguments):
            await ctx.send(f'**Error:** {error} \n**-**That was too many arguments')
        elif isinstance(error, errors.UserInputError):
            await ctx.send(f'**Error:** {error} \n**-**Something went wrong with your input')
        elif isinstance(error, errors.CommandOnCooldown):
            await ctx.send(f'**Error:** {error}')
        elif isinstance(error, errors.MaxConcurrencyReached):
            await ctx.send(f'**Error:** {error} \n**-**This command is running the maximum number of instances allowed')
        elif isinstance(errors, errors.MissingPermissions):
            await ctx.send(f'**Error:** {error} \n**-**You don\'t have the necessary permissions to use this command')
        elif isinstance(errors, errors.MissingRole):
            await ctx.send(f'**Error:** {error} \n**-**You don\'t have the necessary role to use this command')
        else:
            await ctx.send(f'**Error:** {error} \n**-**I didn\'t ever expect to see this error so I didn\'t write an exception for it. Please contact @Cat')


def setup(bot):
    bot.add_cog(Events(bot))