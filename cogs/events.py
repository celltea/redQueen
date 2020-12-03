import discord
import os
import asyncio
import sys

from discord.ext.commands import errors
from discord.ext import commands
from datetime import datetime, date
from utilities import settings, dbinteract, formatting  
from random import randint
from tinydb import database, TinyDB, Query

settings = settings.config("settings.json")


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.members = []
        self.ban_time = 0
        self.warnings = [[], []]

        #Embed Log Constant (change name & color when )
        self.embed_log = None

        #Object Constants (after initial assignment)
        self.guild = None
        self.log_channel = None
        self.booster_role = None
        self.verified_role = None
        self.unverified_role = None
        self.joiner_role = None


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

    @commands.command(help='Staff only: (minutes)')
    @commands.has_permissions(administrator=True)
    async def toggle(self, ctx, min=0):
        self.ban_time = min
        if self.ban_time:
            await ctx.send(content=f"Users with accounts less than __{min} minutes__ old are being filtered")
        else:
            await ctx.send(content="Alternate account filtering is currently off")

    
    @commands.command(help='Staff only: (member)')
    @commands.has_permissions(administrator=True)
    async def pardon(self, ctx, member):
        member = formatting.getfromin(self.bot, ctx, 'mem', member)
        try:
            self.warnings[0].remove(member.id)
        except ValueError: #They gotta be in one of the arrays if we're at this point in the code.
            try:
                self.warnings[1].remove(member.id)
            except ValueError:
                pass

        embed = discord.Embed(description=f'**{member.mention} has had their warnings removed**', color=0x64ff64)
        embed.set_author(name=f'{member.name}#{member.discriminator}', icon_url=member.avatar_url)
        embed.set_thumbnail(url=member.avatar_url)
        embed.timestamp = ctx.message.created_at

        await ctx.send(embed=embed)


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


    async def log_block(self, member):
        channel = self.bot.get_channel(settings.TURNOVER_CHANNEL_ID)

        await channel.send(f':blue_heart: **__Joined:__** {member.mention} aka *{member.name}#{member.discriminator}* __\'{member.id}\'__ ')  

        #handle the unfortunate double-joiner single-user event
        path = settings.DB_PATH + str(member.id) + '.json'
        db = TinyDB(path)
        member = Query()
        table = db.table('information')
        table.upsert({'last_seen' : str(datetime.now().date())}, member.last_seen != None)
        formatting.fancify(path)


    async def role_block(self, member):
        role = self.guild.get_role(settings.JOINER_ROLE_ID)

        await member.add_roles(role, reason='joined')

    async def ban_toggle(self, member):
        if self.ban_time:
            time_elapsed = datetime.utcnow() - member.created_at
            if time_elapsed.seconds <= self.ban_time * 60:
                await self.guild.ban(member)

                greeter_talk = self.bot.get_channel(settings.GREETER_TALK_ID)
                await greeter_talk.send(content=f'**{after.name}#{after.discriminator}** has been banned from the server for having an account that is {(time_elapsed)/60} minutes old')


    @commands.Cog.listener()
    async def on_member_join(self, member):
        await Events.log_block(self, member)
        await Events.role_block(self, member)
        await Events.ban_toggle(self, member)
    

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = self.bot.get_channel(settings.TURNOVER_CHANNEL_ID)

        await channel.send(f':heart: **__Left:__** {member.mention} aka *{member.name}#{member.discriminator}* __\'{member.id}\'__') 

        try: 
            self.members.pop(self.members.index(member.id))
        except ValueError:
            pass

        try:
            os.remove(settings.DB_PATH + str(member.id) + '.json')
        except OSError:
            pass

    
    async def chat_warn(self, message, ban=False):
        await Events.global_assignment(self)
        author = message.author
        
        if author.id in self.warnings[0]:
            self.warnings[0].remove(author.id)
            self.warnings[1].append(author.id)
        elif author.id in self.warnings[1]:
            ban = True
        else:
            self.warnings[0].append(author.id)
            
        embed = discord.Embed(description=f'You have been warned for your previous message {author.mention}', color=0xfefefe)
        embed.set_author(name=f'{author.name}{author.discriminator}', icon_url=author.avatar_url)
        await message.channel.send(embed=embed)

        await Events.embed_log_edit(self, 0xeeee30, message.author, "Message contains blacklisted word(s)")
        self.embed_log.add_field(name='Message', value=message.content, inline=True)
        await self.log_channel.send(embed=self.embed_log)
        self.embed_log.clear_fields()

        await message.delete()

        if ban:
            await author.ban(delete_message_days=0)
            try:
                self.warnings[0].remove(author.id)
            except ValueError: #They gotta be in one of the arrays if we're at this point in the code.
                self.warnings[1].remove(author.id)


    async def chat_filter(self, message):
        if self.unverified_role in message.author.roles:
            content = formatting.simplify(message.content)

            if any(string in content for string in settings.CHAT_BLACKLIST): #Blacklisted words are automatic bans
                await Events.chat_warn(self, message, True)

            if any(string in content for string in settings.CHAT_GREYLIST): #Greylisted words are warnings
                await Events.chat_warn(self, message)


    async def disboard_onm(self, message):
    #disboard successful bump message
        if message.author.id == 302050872383242240 and str(message.embeds[0].color) == '#24b7b7' and ':thumbsup:' in message.embeds[0].description: 
            role = self.guild.get_role(settings.SPEED_FINGERS_ID)
            for member in role.members:
                await member.remove_roles(role, reason='bump role')

            embed = message.embeds[0]
            i = embed.description.find(',')
            member_id = embed.description[2:(i-1)]
            member = self.guild.get_member(int(member_id))
            await member.add_roles(role, reason='bump role')   


    async def activity_upd(self, message):
        if message.author.id not in self.members:
            self.members.append(message.author.id)

    
    async def boost_onm(self, message):
        await Events.global_assignment(self)
        if self.booster_role in message.author.roles:
            seed = randint(1,100)
            if seed <= 25: #5
                db = TinyDB(settings.DB_PATH + str(message.author.id) + '.json')
                table = db.table('boost')
                member = Query()
                try:
                    emote_id = table.get(member.emote_id != None)['emote_id'] #Grabs document_id X containing member.y and then finds value corresponding to ['key_str']
                except TypeError:
                    return
                emote = self.bot.get_emoji(emote_id)
                try:
                    await message.add_reaction(emote)
                except discord.errors.InvalidArgument:
                    await message.author.create_dm()
                    await message.author.dm_channel.send(content=f'Your custom booster emote has been removed, please choose a new one using ```,boost emote (emote)```')
            

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.guild.id == settings.GUILD_ID:
            await Events.chat_filter(self, message)
            await Events.disboard_onm(self, message)
            await Events.activity_upd(self, message)
            try:
                await Events.boost_onm(self, message)
            except: 
                pass


    async def unv_upd(self, before, after):
        timestamp_now = datetime.utcnow()
        await Events.global_assignment(self)
        #checking when zira removes the joiner role to send the welcome message
        if self.unverified_role not in before.roles and self.joiner_role in before.roles and self.unverified_role in after.roles:
            channel = self.bot.get_channel(settings.WELCOME_CHANNEL_ID)
            staff_role = self.guild.get_role(settings.STAFF_ROLE_ID)
            greeter_role = self.guild.get_role(settings.GREETER_ROLE_ID)
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
                await welcome_channel.send(f'Welcome to {self.guild.name}, {after.mention} Please please please make sure you\'ve read over our {unverified_rules.mention}. You should be greeted by our {greeter_role.mention}s shortly. \nAdditionally if you have any questions feel free to ask {staff_role.mention}. I promise we don\'t bite :purple_heart: \nYou took *{elapsed_time}* to read the rules. ')
        

    async def boost_upd(self, before, after):
        await Events.global_assignment(self)
        #checking when a user begins boosting the server
        verified_cond = self.booster_role in after.roles and self.booster_role not in before.roles and self.verified_role in after.roles #verified user boosts
        unverified_cond = self.unverified_role in before.roles and self.unverified_role not in after.roles and self.verified_role in after.roles and self.booster_role in after.roles #unverified user boosts
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


    async def unboost_upd(self, before, after):
        await Events.global_assignment(self)
        if self.booster_role in after.roles and self.booster_role not in before.roles and self.verified_role in after.roles:
            path = settings.DB_PATH + str(after.id) + '.json'
            db = TinyDB(path)
            table = db.table('boost')
            member = Query()
            role_id = table.get(member.role_id != None)['role_id']

            table.remove(member.role_id != None)
            table.remove(member.emote_id != None)
            formatting.fancify(path)

            role = self.guild.get_role(role_id)
            await role.delete(reason=f'{before.name} is not longer boosting')


    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        await Events.unv_upd(self, before, after)
        await Events.boost_upd(self, before, after)
        await Events.unboost_upd(self, before, after)

    
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        await Events.embed_log_edit(self, 0xff6464, user, "Banned")
        await self.log_channel.send(embed=self.embed_log)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        await Events.embed_log_edit(self, 0x64ff64, user, "Unbanned")
        await self.log_channel.send(embed=self.embed_log) 

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if self.unverified_role in after.author.roles:
            await Events.embed_log_edit(self, 0x64b4ff, after.author, "Unverified message edit")
            if len(before.content) > 300:
                content = before.content[0:300] + "..."
            else:
                content = before.content
            self.embed_log.add_field(name='Before', value=content)
            if len(after.content) > 300:
                content = after.content[0:300] + "..."
            else:
                content = after.content
            self.embed_log.add_field(name='After', value=after.content)
            self.embed_log.clear_fields()
            await self.log_channel.send(embed=self.embed_log)


    @commands.Cog.listener()
    async def on_message_delete(self, message):

        if self.unverified_role in message.author.roles:

            async for entry in self.guild.audit_logs(limit=1):
                latest_audit = entry
            audit_difference = datetime.utcnow() - latest_audit.created_at

            latest_log = await self.log_channel.fetch_message(self.log_channel.last_message_id)
            log_difference = datetime.utcnow() - latest_log.created_at

            audit_log_cond = message.author != latest_audit.target and audit_difference.total_seconds() > 2
            mod_log_cond = latest_log.embeds[0].author.icon_url != message.author.avatar_url and log_difference.total_seconds() > 2
            if audit_log_cond and mod_log_cond :
                await Events.embed_log_edit(self, 0x64b4ff, message.author, "Unverified message delete")
                if len(message.content) > 300:
                    content = message.content[0:300] + "..."
                else:
                    content = message.content
                self.embed_log.add_field(name='Message', value=content)
                await self.log_channel.send(embed=self.embed_log)
                self.embed_log.clear_fields()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == settings.JOINER_RULES_REACT_ID and self.bot.get_emoji(settings.JOINER_RULES_EMOJI_ID) == payload.emoji:
            role_unv = self.guild.get_role(settings.UNVERIFIED_ROLE_ID)
            role_join = self.guild.get_role(settings.JOINER_ROLE_ID)

            await payload.member.add_roles(role_unv, reason='unverified react')
            try:
                await payload.member.remove_roles(role_join, reason='unverified react')
            except AttributeError as e:
                print(f'Error: {e}') #if she removes bans them too quickly then this should throw. Not sure if this is causing the error that comes up here or not.

    
    async def global_assignment(self):
        if not self.guild:
            self.guild = self.bot.get_guild(settings.GUILD_ID)
            self.log_channel = self.bot.get_channel(settings.MOD_LOG_ID)
            self.booster_role = self.guild.get_role(settings.BOOSTER_ROLE_ID)
            self.verified_role = self.guild.get_role(settings.VERIFIED_ROLE_ID)
            self.unverified_role = self.guild.get_role(settings.UNVERIFIED_ROLE_ID)
            self.joiner_role = self.guild.get_role(settings.JOINER_ROLE_ID)


    async def embed_log_assignment(self):
            if not self.embed_log:
                self.embed_log = discord.Embed(description='Action taken', color=0x64b4ff)

    
    async def embed_log_edit(self, color, target, action):
        """
        :type color: Hexcode representing color
        :type target: Discord Member/User object
        :type action: String - Ban, Kick, Warn, etc.
        """
        self.embed_log = discord.Embed(description=f'{target.mention} - **{action}**', color=color)
        self.embed_log.set_author(name=f'{target.name}#{target.discriminator}', icon_url=target.avatar_url)
        self.embed_log.set_thumbnail(url=target.avatar_url)
        self.embed_log.timestamp = datetime.utcnow()
            

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
            try:
                await ctx.send(f'**Error:** {error} \n**-**I didn\'t ever expect to see this error so I didn\'t write an exception for it. Please contact @Cat')
            except discord.HTTPException:
                await ctx.send(f'**Error:** Please see console for full error\nI didn\'t ever expect to see this error so I didn\'t write an exception for it. Please contact @Cat')
                print(error)


def setup(bot):
    bot.add_cog(Events(bot))