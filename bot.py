import os
import logging
from datetime import date
import asyncio
import discord 
import utils
from discord.ext import commands
from dotenv import load_dotenv
from database import Message, Log, SessionLocal, init_db
from sqlalchemy import Select, update


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
async def analyze(ctx, days, channel=channel):
    session = SessionLocal()
    try:
        days = int(days)
        if days < 1 or days > 365:
            log = Log(
            author_name=ctx.author.name,
            author_id=ctx.author.id,
            message=f"invalid number of days {days}",
            level="ERROR",
            )
            session.add(log)
            session.commit()
            logger.error(f"invalid number of days {days}")
            await ctx.author.send("invalid number of days, max is 365")
            return
        log = Log(
            author_name=ctx.author.name,
            author_id=ctx.author.id,
            message=f"analyzing data for {days} days",
            level="INFO"
        )
        session.add(log)
        session.commit()
        logger.info(f"analyzing data for {days} days")
        await utils.send_report(bot, current_channel, days)
    except ValueError:
        await ctx.author.send("Invalid input! please enter a valid number between 1 and 365")
        logger.error(f"invalid input {days}")
        log = Log(
            author_name=ctx.author.name,
            author_id=ctx.author.id,
            message=f"invalid input {days}",
            level="ERROR"
        )
        session.add(log)
        session.commit()
        return
    except Exception as err:
        log = Log(
            author_name=ctx.author.name,
            author_id=ctx.author.id,
            message=f"failed to analyze data {err}",
            level="ERROR"
        )
        session.add(log)
        session.commit()
        logger.error(f"analyze error {err}")
    finally:
        session.close()



@bot.event
async def on_message_edit(before, after):
    print("in message edit")
    if before.author.bot:
        return
    session = SessionLocal()
    try: 
        if before.content != after.content:
            stmt = update(Message).where(Message.id == before.id and before.author.id == Message.author_id).values(
                message=after.content,
                updated_at=after.created_at
                )
            session.execute(stmt)
            session.commit()
            log = Log(
                message="message updated",
                level="INFO"
            )
            session.add(log)
            session.commit()
            logger.info("message edited by user {before.author.name}")
    except Exception as err:
        log = Log(
            message=f"failed to update message {err}",
            level="ERROR"
        )
        session.add(log)
        session.commit()
        logger.error(f"failed to update message {err}")
    finally:
        session.close()


    
@bot.event
async def on_message(message):
    if message.channel.id == current_channel and not message.author.bot:
        session = SessionLocal()
        try:
            await utils.load_messages(bot, current_channel)
        except Exception as err:
            log = Log(
                message=f"failed to load messages {err}",
                level="ERROR"
            )
            session.add(log)
            session.commit()
            logger.error(f"Failed to save message: {err}")
        finally:
            session.close()



@bot.event
async def on_ready():
    session = SessionLocal()
    init_db()

    bot.get_channel(current_channel)

    log = Log(
        message="bot started successfully",
        level="INFO"
    )
    session.add(log)
    session.commit()
    logger.info("bot started successfully")
    
    last_7 = date(2025, 3, 1)
    last_30 = date(2025, 2, 15)
    last_180 = date(2024, 9, 1)
    while True:
        last_7, last_30, last_180 = await utils.regular_update(last_7, last_30, last_180, bot, regular_update_channel)
        await asyncio.sleep(86400)

    
        
try:
    session = SessionLocal()
    bot.run(TOKEN)
except Exception as err:
    log = Log(
        message=f"bot failed to start {err}",
        level="ERROR"
    )
    session.add(log)
    session.commit()
    logger.error(f"bot failed to start {err}")
finally:
    session.close()