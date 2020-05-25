import discord
import os

from discord.ext import commands
from dotenv import load_dotenv

#env variables
load_dotenv()

VERIFIED_ROLE_ID = int(os.getenv('VERIFIED_ROLE_ID'))

VERIFYING_RULES = os.getenv('VERIFYING_RULES')
TRANSGENDER_RULES = os.getenv('TRANSGENDER_RULES')
AGE_RULES = os.getenv('AGE_RULES')
BOOST_DM = os.getenv('BOOST_DM')
ADVERTISEMENT = os.getenv('ADVERTISEMENT')


class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #the try except segments allow for the command to be used in dm's without throwing an exception because the bot is unable to delete messages there
    @commands.command(aliases=['verify', 'verification', 'vewify'], help='noarg: prints the verification section of the rules')
    @commands.cooldown(rate='1', per='120', type=commands.BucketType.channel)
    async def verifying(self, ctx):
        await ctx.send(content=VERIFYING_RULES, delete_after=120)
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

    @commands.command(help='noarg: prints the transgender section of the rules')
    @commands.cooldown(rate='1', per='120', type=commands.BucketType.channel)
    async def transgender(self, ctx):
        await ctx.send(content=TRANSGENDER_RULES, delete_after=120)
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
    
    @commands.command(help='noarg: prints the age section of the rules')
    @commands.cooldown(rate='1', per='120', type=commands.BucketType.channel)
    async def age(self, ctx):
        await ctx.send(content=AGE_RULES, delete_after=120)
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass

    @commands.command(help='noarg: prints the nitro dm')
    @commands.has_role(VERIFIED_ROLE_ID)
    async def boost(self, ctx):
        await ctx.send(content=BOOST_DM, delete_after=120)
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
    
    @commands.command(help='noarg: prints the disboard advertisement')
    @commands.has_role(VERIFIED_ROLE_ID)
    async def advertisement(self, ctx):
        await ctx.send(content=ADVERTISEMENT)
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass


def setup(bot):
    bot.add_cog(Rules(bot))