import os
import logging
from datetime import date
import asyncio
import discord 
import utils
from discord.ext import commands
from dotenv import load_dotenv
import database

load_dotenv()

conn = utils.conn

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
async def analyze(ctx, days, channel=channel):
    cursor = conn.cursor()
    try:
        days = int(days)
        if days < 1 or days > 365:
            cursor.execute("INSERT INTO log (author_name, author_id, message, level) VALUES (%s, %s, %s, %s)", (ctx.author.name, ctx.author.id, f"invalid number of days {days}", "ERROR"))
            logger.error(f"invalid number of days {days}")
            await ctx.author.send("invalid number of days, max is 365")
            return
        cursor.execute("INSERT INTO log (author_name, author_id, message, level) VALUES (%s, %s, %s, %s)", (ctx.author.name, ctx.author.id, f"analyzing data for {days} days", "INFO"))
        logger.info(f"analyzing data for {days} days")
        await utils.send_report(bot, current_channel, days)
    except ValueError:
        await ctx.author.send("Invalid input! please enter a valid number between 1 and 365")
        logger.error(f"invalid input {days}")
        cursor.execute = ("INSERT INTO log (author_name, author_id, message, level) VALUES (%s, %s, %s, %s)", (ctx.author.name, ctx.author.id, f"invalid input {days}", "ERROR"))
        return
    except Exception as err:
        cursor.execute("INSERT INTO log (message, level) VALUES (%s, %s)", (f"failed to analyze data {err}", "ERROR",))
        logger.error(f"analyze error {err}")
    finally:
        cursor.close()
        conn.commit()
    

@bot.event
async def on_ready():
    database.create_database()
    bot.get_channel(current_channel)

    cursor = conn.cursor()
    cursor.execute("INSERT INTO log (message, level) VALUES (%s, %s)", ("bot started successfully", "INFO",))
    await utils.load_messages(bot, current_channel)
    
    last_7 = date(2025, 3, 1)
    last_30 = date(2025, 2, 15)
    last_180 = date(2024, 9, 1)
    while True:
        last_7, last_30, last_180 = await utils.regular_update(last_7, last_30, last_180, bot, regular_update_channel)
        await asyncio.sleep(86400)

    
        
try:
    cursor = conn.cursor()
    bot.run(TOKEN)
except Exception as err:
    cursor.execute ("INSERT INTO log (message, level) VALUES (%s, %s)", (f"bot failed to start {err}", "ERROR"))
    logger.error(f"bot failed to start {err}")
finally:
    cursor.close()
    conn.commit()
