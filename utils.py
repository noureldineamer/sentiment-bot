import re 
import logging
from datetime import datetime, timedelta
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os 
from dotenv import load_dotenv
from datetime import date
import emoji
from database import Message, Log, SessionLocal


load_dotenv()

nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()


log_path = os.getenv("LOG_PATH")
logger = logging.getLogger(__name__)
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",    
)

def is_emoji(message: str) -> bool:
    pattern = re.sub(r"<a?:\w+:\d+>", "", message)
    without_emoji = emoji.replace_emoji(pattern, "")
    return len(without_emoji.strip()) == 0


async def load_messages(bot, channel_id, limit=None):
    channel = bot.get_channel(channel_id)
    session = SessionLocal()
    if channel:
        async for msg in channel.history(limit=limit):
            if msg.stickers or msg.attachments or msg.embeds or msg.content.startswith("https://") or msg.author.bot or is_emoji(msg.content):
                continue
            if not session.query(Message).filter_by(id=msg.id).first():
                try:
                    message = Message(
                        id=msg.id,
                        author_name=msg.author.name,
                        author_id=msg.author.id,
                        message=msg.content,
                        message_send_timestamp=msg.created_at,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    session.add(message)
                    session.commit()
                except Exception as err:
                    logger.error(f"failed to insert message {err}")
        session.close()


async def get_messages(days):
    session = SessionLocal()
    messages = session.query(Message).filter(
        Message.message_send_timestamp.between(
            datetime.utcnow() - timedelta(days=days),
            datetime.utcnow()
        )
    ).all()
    result = [msg.message for msg in messages]
    session.close()
    return result
    
    

async def analyze(messages):
    session = SessionLocal()
    if not messages: 
        log = Log(
            message="no messages to analyze",
            level="INFO"
        )
        session.add(log)
        session.commit()
        logger.info("no messages to analyze")
        return 0
    scores = [sia.polarity_scores(msg)['compound'] for msg in messages]
    if scores:
        avg_compound = sum(scores) / len(scores)
        log = Log(
            message=f"average compound score {avg_compound}",
            level="INFO"
        )
        session.add(log)
        session.commit()
        logger.info(f"average compound score {avg_compound}")
        return avg_compound
    log = Log(
        message = "no valid sentiment score found",
        level = "INFO"
    )
    session.add(log)
    session.commit()
    logger.info("no valid sentiment score found")
    session.close()
    return 0



async def send_report(bot, channel_id, days):
    session = SessionLocal()
    messages = await get_messages(days)
    channel = bot.get_channel(channel_id)
    if not messages:
        log = Log(
            mesage="no messages to analyze",
            level="INFO"
        )
        session.add(log)   
        session.commit()
        logger.info("no messages to analyze")
        await channel.send("no data found to be analyzed")
        return
    scores = await analyze(messages)
    label = (f"for the past {days} days Investors are generally happy with the current market state" 
            if scores > 0.1 else f"for the past {days} days Investors are unhappy with the current state of the market"
            if scores < -0.1 else f"for the past {days} days Investors are neutral with the current sate of the market")
    await channel.send(f"{label}")

async def regular_update(last_7: date, last_30: date, last_180: date, bot, channel_id):
    session = SessionLocal()
    today = date.today()
    days_since_7 = (today - last_7).days
    days_since_30 = (today - last_30).days
    days_since_180 = (today - last_180).days

    if days_since_7 >= 7:
        try:
            await send_report(bot, channel_id, 7)
            last_7 = today
            log = Log(
                message="regular update over 7 days",
                level="INFO"
            )
            session.add(log)
            session.commit()
            logger.info("regular update over 7 days")
        except Exception as err:
            logger.error(f"failed to regularly update over 7 days {err}")
            log = Log(
                message=f"failed to regularly update over 7 days {err}",
                level="ERROR"
            )
            session.add(log)
            session.commit()
            
    if days_since_30 >= 30:
        try:
            await send_report(bot, channel_id, 30)
            last_30 = today
            log = Log(
                message="regular update over 30 days",
                level="INFO"
            )
            session.add(log)
            session.commit()        
            logger. info("regular update over 30 days") 
        except Exception as err:
            log= Log(
                message=f"failed to regularly update over 30 days {err}",
                level="ERROR"
            )
            session.add(log)
            session.commit()
            logger.error(f"failed to regularly update over 30 days {err}")

    if days_since_180 >= 180:
        try:
            await send_report(bot, channel_id, 180)
            last_180 = today
            log = Log(
                message="regular update over 180 days",
                level="INFO"
            )
            session.add(log)
            session.commit()
            logger.info("regular update over 180 days")
        except Exception as err:
            log = Log(
                message=f"failed to regularly update over 180 days {err}",
                level="ERROR"
            )
            session.add(log)
            session.commit()
            logger.error(f"failed to regularly update over 180 days {err}")
    else:
        session.close()
    return last_7, last_30, last_180