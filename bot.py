import logging
import os

import nextcord
from dotenv import load_dotenv
from nextcord.ext import commands

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO, format='[DISCORD_BOT_INFO] %(message)s')

intents = nextcord.Intents.all()
bot = commands.Bot(intents=intents)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py') and filename != '__init__.py':
        bot.load_extension(f'cogs.{filename[:-3]}')


@bot.event
async def on_ready():
    activity = nextcord.ActivityType.listening
    logging.info(f'Logged in as {bot.user}')
    await bot.change_presence(
        status=nextcord.Status.online,
        activity=nextcord.Activity(type=activity, name="commands")
    )


if __name__ == "__main__":
    bot.run(TOKEN)
