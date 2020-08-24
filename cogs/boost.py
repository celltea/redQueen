import discord
import os

from discord.ext import commands
from dotenv import load_dotenv
from utilities import formatting

load_dotenv()
SAY_LOG_ID = int(os.getenv('SAY_LOG_ID'))

BOOSTER_ROLE_ID = int(os.getenv('BOOSTER_ROLE_ID'))
VERIFIED_ROLE_ID = int(os.getenv('VERIFIED_ROLE_ID'))
STAFF_ROLE_ID = int(os.getenv('STAFF_ROLE_ID'))

class Boost(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='boosters only: (channel) (contents of message)')
    @commands.has_role(VERIFIED_ROLE_ID)
    @commands.check_any(commands.has_role(BOOSTER_ROLE_ID), commands.has_role(STAFF_ROLE_ID))
    async def say(self, ctx, channel_id, *, msg):
        try:
            channel = self.bot.get_channel(int(channel_id))
        except ValueError:
            channel = self.bot.get_channel(int(formatting.strip(channel_id)))

        log_channel = self.bot.get_channel(int(SAY_LOG_ID))

        if ctx.author.permissions_in(channel).send_messages:
            if len(ctx.message.role_mentions) != 0 or '@everyone' in msg or '@here' in msg: #checking if there are any mentions in the message
                await ctx.send(content='You cannot mention roles with this command')
                return
            else:
                print('@here' in msg + 'does this work?')
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