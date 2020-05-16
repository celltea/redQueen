import os

from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()   
TOKEN = os.getenv('DISCORD_TOKEN')
COGS = os.getenv('COG_PATH')
bot = commands.Bot(command_prefix=',')

for file in os.listdir(COGS):
    if file.endswith('.py'):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")

bot.run(TOKEN)
