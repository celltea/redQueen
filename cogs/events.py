import discord
import os
import asyncio
import sys

from discord.ext.commands import errors
from discord.ext import commands
from datetime import datetime
from utilities import settings, dbinteract, formatting
from random import randint
from tinydb import database, TinyDB, Query

settings = settings.config("settings.json")


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.members = []


    #only works on cogs, will not apply any module updates
    @commands.command(help='no arg: WARNING reloads all cogs')
    @commands.has_permissions(administrator=True)
    async def reload(self, ctx):
        dbinteract.activity_push(self.members, datetime.now().date())

        for file in os.listdir(settings.COG_PATH):
            if file.endswith('.py'):
                name = file[:-3]
                self.bot.reload_extension(f"cogs.{name}")

        await ctx.send(content='cogs reloaded')

    
    @commands.command(help='no arg: WARNING stops bot')
    @commands.has_permissions(administrator=True)
    async def stop(self, ctx):
        dbinteract.activity_push(self.members, datetime.now().date())
        await ctx.send(content='shutting down')
        sys.exit()


    async def periodic_push(self):
        duration = (datetime.max - datetime.today()).seconds + 5
        await asyncio.sleep(duration)
        while True:
            dbinteract.activity_push(self.members, datetime.now().date())
            self.members = []  
            await asyncio.sleep(86400)      


    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.bot.user.name} has connected succesfully!')

        await Events.periodic_push(self)


    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(settings.TURNOVER_CHANNEL_ID)

        await channel.send(f':blue_heart: **__Joined:__** {member.mention} aka *{member.name}#{member.discriminator}* __\'{member.id}\'__ ')  

        #handle the unfortunate double-joiner single-user event
        path = settings.DB_PATH + str(member.id) + '.json'
        db = TinyDB(path)
        member = Query()
        table = db.table('information')
        table.upsert({'last_seen' : str(datetime.now().date())}, member.last_seen != None)
        formatting.fancify(path)
    

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.bot.get_channel(settings.TURNOVER_CHANNEL_ID)
        user = self.bot.get_user(member.id)

        await channel.send(f':heart: **__Left:__** {user.mention} aka *{user.name}#{member.discriminator}* __\'{member.id}\'__') 

        try: 
            self.members.pop(self.members.index(member.id))
        except ValueError:
            pass

        try:
            os.remove(settings.DB_PATH + str(member.id) + '.json')
        except OSError:
            pass


    async def disboard_onm(self, message):
    #disboard successful bump message
        if message.author.id == 302050872383242240 and str(message.embeds[0].color) == '#24b7b7' and ':thumbsup:' in message.embeds[0].description: 
            role = message.guild.get_role(settings.SPEED_FINGERS_ID)
            for member in role.members:
                await member.remove_roles(role, reason='bump role')

            embed = message.embeds[0]
            i = embed.description.find(',')
            member_id = embed.description[2:(i-1)]
            member = message.guild.get_member(int(member_id))
            await member.add_roles(role, reason='bump role')


    async def anna_onm(self, message):
        if message.author.id == 583861014794207237:
            if randint(1, 20) == 1:
                emote = self.bot.get_emoji(726170090026041456)
                await message.add_reaction(emote)          


    async def activity_upd(self, message):
        if message.author.id not in self.members:
            self.members.append(message.author.id)


    @commands.Cog.listener()
    async def on_message(self, message):
        await Events.disboard_onm(self, message)
        await Events.anna_onm(self, message)
        await Events.activity_upd(self, message)
        

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
        timestamp_now = datetime.utcnow() 
        joiner_role = after.guild.get_role(settings.JOINER_ROLE_ID)
        unverified_role = after.guild.get_role(settings.UNVERIFIED_ROLE_ID)
        #checking when zira removes the joiner role to send the welcome message
        if joiner_role in before.roles and joiner_role not in after.roles and unverified_role in after.roles:
            channel = self.bot.get_channel(settings.WELCOME_CHANNEL_ID)
            staff_role = after.guild.get_role(settings.STAFF_ROLE_ID)
            greeter_role = after.guild.get_role(settings.GREETER_ROLE_ID)
            welcome_channel = self.bot.get_channel(settings.WELCOME_CHANNEL_ID)
            unverified_rules = self.bot.get_channel(settings.UNVERIFIED_RULES_ID)
                
            elapsed_time = formatting.datetime_difference(after.joined_at, timestamp_now)
            difference = timestamp_now - after.joined_at
            elapsed_seconds = difference.total_seconds()

            if elapsed_seconds < 16:
                await after.ban(delete_message_days=0)
                message = await welcome_channel.send(f'**{after.name}#{after.discriminator}** has been banned from the server for spending *{elapsed_time}* reading the rules.')
                emote = self.bot.get_emoji(720091197594534001)
                await message.add_reaction(emote)
                try:
                    await after.create_dm()
                    await after.dm_channel.send(f'You have automatically been banned from the server for spending too little time reading the rules.')
                except discord.Forbidden:
                    pass

            else:
                await welcome_channel.send(f'Welcome to {after.guild.name}, {after.mention} Please please please make sure you\'ve read over our {unverified_rules.mention}. You should be greeted by our {greeter_role.mention}s shortly. \nAdditionally if you have any questions feel free to ask {staff_role.mention}. I promise we don\'t bite :purple_heart: \nYou took *{elapsed_time}* to read the rules. ')
        

    async def boost_upd(self, before, after):
        booster_role = after.guild.get_role(settings.BOOSTER_ROLE_ID)
        verified_role = after.guild.get_role(settings.VERIFIED_ROLE_ID)
        unverified_role = after.guild.get_role(settings.UNVERIFIED_ROLE_ID)
        #checking when a user begins boosting the server
        verified_cond = booster_role in after.roles and booster_role not in before.roles and verified_role in after.roles #verified user boosts
        unverified_cond = unverified_role in before.roles and unverified_role not in after.roles and verified_role in after.roles and booster_role in after.roles #unverified user boosts
        if verified_cond or unverified_cond:
            embed = discord.Embed(title='Server Boost!', description=f'{after.mention} boosted the server!', color=0xe164e1)
            embed.set_thumbnail(url=after.avatar_url)
            embed.timestamp = datetime.utcnow()

            general = self.bot.get_channel(settings.GENERAL_ID)

            try:
                await after.create_dm()
                await after.dm_channel.send(content=settings.BOOST_DM)
            except discord.Forbidden:
                await general.send(content=settings.BOOST_DM)
                pass

            await general.send(embed=embed)

            category = after.guild.get_role(settings.BOOSTER_CATEGORY)
            role = await after.guild.create_role(name=str(after.id), mentionable=True, reason=f'{after.name} boosted the server!')
            await role.edit(position=category.position - 1)
            await after.add_roles(role)

            path = settings.DB_PATH + str(after.id) + '.json'
            db = TinyDB(path)
            member = Query()
            table = db.table('boost')

            table.upsert({'role_id' : role.id}, member.role_id != None) #If conditional is True: update. If False: insert.
            formatting.fancify(path)


    async def unboost_upd(self, before, after):
        booster_role = after.guild.get_role(settings.BOOSTER_ROLE_ID)
        verified_role = after.guild.get_role(settings.VERIFIED_ROLE_ID)
        if booster_role in after.roles and booster_role not in before.roles and verified_role in after.roles:
            path = settings.DB_PATH + str(after.id) + '.json'
            db = TinyDB(path)
            table = db.table('boost')
            member = Query()
            role_id = table.get(member.role_id != None)['role_id']

            table.remove(member.role_id != None)
            formatting.fancify(path)

            role = after.guild.get_role(role_id)
            await role.delete(reason=f'{before.name} is not longer boosting')


    @commands.Cog.listener()
    async def on_member_update(self, before, after): #Assign here so shared vars avoid overlap
        await Events.unv_upd(self, before, after)
        await Events.boost_upd(self, before, after)
        await Events.unboost_upd(self, before, after)


    #catching updates... this is gonna suck
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
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