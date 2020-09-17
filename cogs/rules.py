import discord

from discord.ext import commands
from utilities import settings

settings = settings.config("settings.json")


class Rules(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=['verify', 'verification', 'vewify'], help='noarg: prints the verification section of the rules')
    @commands.cooldown(rate='1', per='120', type=commands.BucketType.channel)
    async def verifying(self, ctx):
        await ctx.send(content=settings.VERIFYING_RULES, delete_after=120)
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass


    @commands.command(help='noarg: prints the transgender section of the rules')
    @commands.cooldown(rate='1', per='120', type=commands.BucketType.channel)
    async def transgender(self, ctx):
        await ctx.send(content=settings.TRANSGENDER_RULES, delete_after=120)
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass


    @commands.command(help='noarg: prints the age section of the rules')
    @commands.cooldown(rate='1', per='120', type=commands.BucketType.channel)
    async def age(self, ctx):
        await ctx.send(content=settings.AGE_RULES, delete_after=120)
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass


    @commands.command(help='noarg: prints the nitro dm')
    @commands.has_role(settings.VERIFIED_ROLE_ID)
    async def boosting(self, ctx):
        await ctx.send(content=settings.BOOST_DM, delete_after=120)
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
    
    
    @commands.command(help='noarg: prints the disboard advertisement')
    @commands.has_role(settings.VERIFIED_ROLE_ID)
    async def advertisement(self, ctx):
        await ctx.send(content=settings.ADVERTISEMENT)
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass


def setup(bot):
    bot.add_cog(Rules(bot))