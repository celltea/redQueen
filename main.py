import discord
import os

from discord.ext import commands
from utilities import settings

settings = settings.config("settings.json")
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=',', intents=intents)
    
for file in os.listdir(settings.COG_PATH):
    if file.endswith('.py'):
        name = file[:-3]
        bot.load_extension(f"cogs.{name}")
        
bot.run(settings.DISCORD_TOKEN)