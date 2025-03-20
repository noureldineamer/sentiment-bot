import os
import logging
from datetime import date
import asyncio


import discord 
import utils
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

log_path = os.getenv("LOG_PATH")
logger = logging.getLogger(__name__)
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    
)

TOKEN = os.getenv("TOKEN")
current_channel = int(os.getenv("CURRENT_CHANNEL"))
regular_update_channel = int(os.getenv("REGULAR_UPDATE_CHANNEL"))
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
channel = bot.get_channel(current_channel)
bot.get_channel(current_channel)



@bot.command()
async def analyze(ctx, days, limit=None, channel=channel):
    print("HELLO")
    try:
        days = int(days)
        if days < 1 or days > 365:
            await ctx.author.send("invalid number of days")
            return
        await utils.send_report(bot, current_channel, days, limit=limit)
        logging.info(f"analyzed data for: {ctx.author}")
    except ValueError:
        await ctx.author.send("Invalid input! please enter a valid number between 1 and 365")
        logging.error("user input invalid number of days")
        return
    except Exception as err:
        logger.error(f"analyze error {err}")
    

@bot.event
async def on_ready():
    bot.get_channel(current_channel)
    print(f"logged in as {bot.user}")
    print("-----")
    logging.info("bot started successfully")
    
    last_7 = date(2025, 3, 1)
    last_30 = date(2025, 2, 15)
    last_180 = date(2024, 9, 1)
    while True:
        last_7, last_30, last_180 = await utils.regular_update(last_7, last_30, last_180, bot, regular_update_channel)
        await asyncio.sleep(86400)

        
try:
    bot.run(TOKEN)
except Exception as err:
    logging.error(f"bot encountered an error {err}")