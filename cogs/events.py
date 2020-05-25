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
BOT_COMMANDS_ID = int(os.getenv('BOT_COMMANDS_ID'))
GENERAL_ID = int(os.getenv('GENERAL_ID'))

UNVERIFIED_ROLE_ID = int(os.getenv('UNVERIFIED_ROLE_ID'))
STAFF_ID = int(os.getenv('STAFF_ROLE_ID'))
GREETER_ID = int(os.getenv('GREETER_ROLE_ID'))
JOINER_ROLE_ID = int(os.getenv('JOINER_ROLE_ID'))
VERIFIED_ROLE_ID = int(os.getenv('VERIFIED_ROLE_ID'))
SPEED_FINGERS_ID = int(os.getenv('SPEED_FINGERS_ID'))
BOOSTER_ROLE_ID = int(os.getenv('BOOSTER_ROLE_ID'))

BOOST_DM = os.getenv('BOOST_DM')

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot 
        self.bot_commands = self.bot.get_channel(BOT_COMMANDS_ID)

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

    @commands.Cog.listener()
    async def on_message(self, message):

        #disboard successful bump message
        if message.author.id == 302050872383242240 and str(message.embeds[0].color) == '#24b7b7' and ':thumbsup:' in message.embeds[0].description: 
        #type(message.embeds[0].thumbnail) == discord.embeds.EmbedProxy
        
            #print('if cleared')
            #await message.channel.send(content=f'if statement cleared with: {message.jump_url}')
            role = message.guild.get_role(SPEED_FINGERS_ID)
            for member in role.members:
                await member.remove_roles(role, reason='bump role')

            embed = message.embeds[0]
            i = embed.description.find(',')
            member_id = embed.description[2:(i-1)]
            member = message.guild.get_member(int(member_id))
            await member.add_roles(role, reason='bump role')

        #maybe add a verified status check here?
        #await self.bot.process_commands(message)



#    @commands.Cog.listener()
#    async def on_message_delete(self, message):
#
#        if self.unverified_role in message.author.roles:
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

    async def unv_upd(self, before, after):
        joiner_role = after.guild.get_role(JOINER_ROLE_ID)
        unverified_role = after.guild.get_role(UNVERIFIED_ROLE_ID)
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

                if elapsed_seconds <= 15:
                    await after.ban(delete_message_days=0)
                    await welcome_channel.send(f'**{after.name}#{after.discriminator}** has been banned from the server for spending *{elapsed_time}* reading the rules.')
                    try:
                        await after.create_dm()
                        await after.dm_channel.send(f'You have automatically been banned from the server for spending too little time reading the rules.')
                    except discord.Forbidden:
                        pass

                else:
                    await welcome_channel.send(f'Welcome to {after.guild.name}, {after.mention} Please please please make sure you\'ve read over our {unverified_rules.mention}. You should be greeted by our {greeter_role.mention}s shortly. \nAdditionally if you have any questions feel free to ask {staff_role.mention}. I promise we don\'t bite :purple_heart: \nYou took *{elapsed_time}* to read the rules. ')
        return

    async def boost_upd(self, before, after):
        #checking when a user begins boosting the server
        booster_role = after.guild.get_role(BOOSTER_ROLE_ID)
        if booster_role in after.roles and booster_role not in before.roles:
            embed = discord.Embed(title='Server Boost!', description=f'{after.mention} boosted the server!', color=0xe164e1)
            embed.set_thumbnail(url=after.avatar_url)
            embed.timestamp = ctx.message.created_at

            general = self.bot.get_channel(GENERAL_ID)

            try:
                await after.create_dm()
                await after.dm_channel.send(content=BOOST_DM)
            except discord.Forbidden:
                pass
            await general.send(content=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        await Events.unv_upd(self, before, after)
        await Events.boost_upd(self, before, after)

    #catching updates... this is gonna suck
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