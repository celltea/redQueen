import discord
import os

from discord.ext import commands
from dotenv import load_dotenv
from utilities import formatting, settings

settings = settings.config("settings.json")


class Boost(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(help='boosters only: (channel) (contents of message)')
    @commands.has_role(settings.VERIFIED_ROLE_ID)
    @commands.check_any(commands.has_role(settings.BOOSTER_ROLE_ID), commands.has_role(settings.STAFF_ROLE_ID))
    async def say(self, ctx, channel, *, msg):
        channel = formatting.getfromin(self.bot, ctx, "cha", channel)
        log_channel = self.bot.get_channel(int(settings.SAY_LOG_ID))

        if ctx.author.permissions_in(channel).send_messages and len(ctx.message.role_mentions) == 0 or '@everyone' not in msg or '@here' not in msg: #checking if there are any mentions in the message:
            if len(ctx.message.role_mentions) != 0 or '@everyone' in msg or '@here' in msg: #checking if there are any mentions in the message
                await ctx.send(content='You cannot mention roles with this command')
                return
            else:
                await log_channel.send(f'__{ctx.message.author.name}:__ {msg} **in** *{channel.name}*')
                await channel.send(f'{msg}')

            try:
                await ctx.message.delete()

            except discord.Forbidden:
                pass
        else:
            await ctx.send(f'You\'re only allowed to use this command in channels you may speak in! You can\'t speak in **{channel.name}**')


def setup(bot):
    bot.add_cog(Boost(bot))