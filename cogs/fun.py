import discord
import os 
import asyncio

from discord.ext import commands
from dotenv import load_dotenv
from utilities import formatting
from random import randint

#env vars
VERIFIED_ROLE_ID = int(os.getenv('VERIFIED_ROLE_ID'))

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        #rps vars
        self.rps1 = None #challenger member
        self.rps2 = None #challengee member
        self.input1 = None
        self.input2 = None
        self.rps_channel = None
        self.rps_state = 0

    #use subcommands with this later on to make it crisp
    @commands.command(help='(start/choose) (verified user)')
    #@commands.has_role(VERIFIED_ROLE_ID) #this breaks the dm-aspect of the game
    async def rps(self, ctx, state, *, selection=None):
        if state.lower() == 'start' and self.rps_state == 0:
            #print('start state')
            try:
                self.rps2 = ctx.guild.get_member(int(selection))
            except ValueError:
                self.rps2 = ctx.guild.get_member(int(formatting.strip(selection)))

            self.rps1 = ctx.message.author
            self.rps_state = 1
            self.rps_channel = ctx.message.channel

            await ctx.send(content='Please send your choice to my dm using: \n> **,rps choose rock**   **,rps choose paper**  **,rps choose scissors**')


            for i in range(60):
                if self.rps_state == 0:
                    return
                await asyncio.sleep(1)

            await self.rps_channel.send(content='No response, game has timed out')

            self.rps_state = 0
            self.rps1 = None 
            self.rps2 = None 
            self.input1 = None
            self.input2 = None
            self.rps_channel = None
        
        if state.lower() == 'start' and self.rps_state == 1:
            await self.rps_channel.send(content='There\'s an ongoing game, please wait for them to finish!')

        if state.lower() == 'choose' and ctx.guild is None :
            if ctx.author == self.rps1:
                self.input1 = selection.lower()
                await ctx.send(content='Choice received')
                await self.rps_channel.send(f'Received from **{self.rps1.name}#{self.rps1.discriminator}**')

            if ctx.author == self.rps2:
                self.input2 = selection.lower()
                await ctx.send(content='Choice recieved')
                await self.rps_channel.send(f'Received from **{self.rps2.name}#{self.rps2.discriminator}**')
        
        if self.input1 != None and self.input2 != None:
            #I'm not positive how to do this other than comparing the if statements. Maybe assigning them to numbers... but the hierachy makes a circle so there's no value comparison that works
            winner = None
            if self.input1 == self.input2: 
                winner = None
            elif self.input1 == 'rock' and self.input2 == 'paper':
                winner = self.rps2
            elif self.input1 == 'rock' and self.input2 == 'scissors':
                winner = self.rps1
            elif self.input1 == 'paper' and self.input2 == 'rock':
                winner = self.rps1
            elif self.input1 == 'paper' and self.input2 == 'scissors':
                winner = self.rps2
            elif self.input1 == 'scissors' and self.input2 == 'rock':
                winner = self.rps2
            elif self.input1 == 'scissors' and self.input2 == 'paper':
                winner = self.rps1
            else:
                await self.rps_channel.send(content='Someone gave an incorrect input. Please start a new game.')

                self.rps_state = 0
                self.rps1 = None 
                self.rps2 = None 
                self.input1 = None
                self.input2 = None
                self.rps_channel = None
            
                return

            try:
                embed = discord.Embed(title='Rock! Paper! Scissors!', description=f'**{winner.mention} is the winner!**', color=0x64b4ff)
            except AttributeError:
                embed = discord.Embed(title='Rock! Paper! Scissors!', description=f'', color=0x64b4ff)

            if randint(1, 100) == 1 and winner is not None:
                loser = None
                if winner is self.rps1:
                    loser = self.rps2
                else:
                    loser = self.rps1
                embed.description = f'**{winner.mention} would have won but they cheated so __{loser.mention} wins!__**'

            if winner is None:
                embed.set_thumbnail(url='https://i.imgur.com/TIGi71f.png') #thumbnail for no winner
                embed.description = '**It\'s a tie!**'
            else: 
                embed.set_thumbnail(url='https://i.imgur.com/GWKFyR9.png') #thumbnail for anyone winning

            embed.add_field(name=f'{self.rps1.name}#{self.rps1.discriminator}', value=f'{self.input1}', inline=False)
            embed.add_field(name=f'{self.rps2.name}#{self.rps2.discriminator}', value=f'{self.input2}', inline=False)
            embed.timestamp = ctx.message.created_at

            await self.rps_channel.send(embed=embed)
            
            self.rps_state = 0
            self.rps1 = None 
            self.rps2 = None 
            self.input1 = None
            self.input2 = None
            self.rps_channel = None

    @commands.command(help='(user)')
    @commands.has_role(VERIFIED_ROLE_ID)
    async def ship(self, ctx, target1, target2=None):
        try:
            member2 = ctx.guild.get_member(int(target1))
        except ValueError:
            member2 = ctx.guild.get_member(int(formatting.strip(target1)))

        #checking to see if author is implied as a target
        if target2:
            try:
                member1 = ctx.guild.get_member(int(target2))
            except ValueError:
                member1 = ctx.guild.get_member(int(formatting.strip(target2)))

        else:
            member1 = ctx.author

        num1 = member1.id%1000 #command user
        num2 = member2.id%1000 #target
        comp_num = (num1 + num2 - 40)%101
        bars_ref = comp_num//10
        bars_on = bars_ref*'<a:baron:725816473704202242>'
        bars_off = (10-bars_ref)*'<a:baroff:725816609176027635>'
        status = None

        #this seems sloppy, I think there's a better way to do this
        while True:
            if comp_num == 100:
                status = 'You\'re made for eachother <a:true_love:725827494585827481>'
            if comp_num >= 90:
                status = 'True love :heart_eyes:'
                break
            if comp_num >= 80:
                status = 'Wew is it hot in here? :fire:'
                break
            if comp_num >= 70:
                status = 'Just 2 gals being pals :wink:'
                break
            if comp_num == 69:
                status = 'Nice <a:okhandspin:644684375287660564>'
                break
            if comp_num >= 60:
                status = 'Budding potential :heart:'
                break
            if comp_num >= 50:
                status = 'Besties :smile:'
                break
            if comp_num >= 40:
                status = 'Lets just be friends :eyes:'
                break
            if comp_num >= 30:
                status = 'It\'s not you it\'s me... :eyes:'
                break
            if comp_num >= 20:
                status = 'Prepare to get ghosted :ghost:'
                break
            if comp_num >= 10:
                status = 'Bitter rivals :angry:'
                break
            if comp_num >= 1:
                status = 'Sworn enemies :right_facing_fist::left_facing_fist: '
                break
            else:
                status = 'She\'s practically your sister! :nauseated_face:'
                break

        embed = discord.Embed(description=f'**{comp_num}%** {bars_on}{bars_off} {status}', color=0xe484dc)

        await ctx.send(content=f'{member1.mention} and {member2.mention} sitting in a tree...', embed=embed)





def setup(bot):
    bot.add_cog(Fun(bot))