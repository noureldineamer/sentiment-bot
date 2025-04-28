import re 
import logging
from datetime import datetime
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import mysql.connector
import os 
from dotenv import load_dotenv
from datetime import date
import emoji


load_dotenv()

nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

def is_emoji(message: str) -> bool:
    pattern = re.sub(r"<a?:\w+:\d+>", "", message)
    without_emoji = emoji.replace_emoji(pattern, "")
    return len(without_emoji.strip()) == 0

log_path = os.getenv("LOG_PATH")
logger = logging.getLogger(__name__)
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",    
)
user=os.getenv("USER")
password=os.getenv("PASSWORD")
host=os.getenv("HOST")
database=os.getenv("DATABASE")
conn = mysql.connector.connect(
    user=user,
    password=password,
    host=host,
    database=database
)


async def load_messages(bot, channel_id, limit=None):
    channel = bot.get_channel(channel_id)
    cursor = conn.cursor()
    if channel:
        async for msg in channel.history(limit=limit):
            if msg.stickers or msg.attachments or msg.embeds or msg.content.startswith("https://") or msg.author.bot or is_emoji(msg.content):
                continue
            cursor.execute("SELECT 1 FROM messages WHERE id = %s", (msg.id,))
            if cursor.fetchone() is None:
                try:
                    cursor.execute("INSERT IGNORE INTO messages (id, author_name, author_id, message, message_send_timestamp, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (msg.id, msg.author.name, msg.author.id, msg.content, msg.created_at, datetime.utcnow(), datetime.utcnow()))
                except mysql.connector.Error as err:
                    cursor.execute ("INSERT INTO log (message, level) VALUES (%s, %s)", (f"failed to insert message {err}", "ERROR"))
                    logger.error(f"failed to insert message {err}")
        cursor.close()  
        conn.commit()


async def get_messages(days):
    cursor = conn.cursor()
    cursor.execute("SELECT message FROM messages WHERE message_send_timestamp BETWEEN NOW() - INTERVAL %s DAY AND NOW()", (days,))
    messages = cursor.fetchall()
    result = [msg[-1] for msg in messages]
    cursor.close()
    conn.commit() 
    return result
    
    

async def analyze(messages):
    cursor = conn.cursor()
    if not messages: 
        cursor.execute("INSERT INTO log (message, level) VALUES (%s, %s)", ("no messages to analyze", "INFO"))
        logger.info("no messages to analyze")
        return 0
    scores = [sia.polarity_scores(msg)['compound'] for msg in messages]
    if scores:
        avg_compound = sum(scores) / len(scores)
        cursor.execute("INSERT INTO log (message, level) VALUES (%s, %s)", (f"average compound score {avg_compound}", "INFO"))
        return avg_compound
    cursor.execute("INSERT INTO log (message, level) VALUES (%s, %s)", ("no valid sentiment score found", "INFO"))
    cursor.close()
    conn.commit()
    return 0



async def send_report(bot, channel_id, days):
    cursor = conn.cursor()
    messages = await get_messages(days)
    channel = bot.get_channel(channel_id)
    if not messages:
        cursor.execute("INSERT INTO log (message, level) VALUES (%s, %s)", ("no messages to analyze", "INFO"))
        logger.info("no messages to analyze")
        await channel.send("no data found to be analyzed")
        return
    scores = await analyze(messages)
    label = (f"for the past {days} days Investors are generally happy with the current market state" 
            if scores > 0.1 else f"for the past {days} days Investors are unhappy with the current state of the market"
            if scores < -0.1 else f"for the past {days} days Investors are neutral with the current sate of the market")
    await channel.send(f"{label}")

async def regular_update(last_7: date, last_30: date, last_180: date, bot, channel_id):
    cursor = conn.cursor()
    today = date.today()
    days_since_7 = (today - last_7).days
    days_since_30 = (today - last_30).days
    days_since_180 = (today - last_180).days

    if days_since_7 >= 7:
        try:
            await send_report(bot, channel_id, 7)
            last_7 = today
            cursor.execute("INSERT INTO log (message, level) VALUES (%s, %s)", ("regular update over 7 days", "INFO",))
            logger.info("regular update over 7 days")
        except Exception as err:
            logger.error(f"failed to regularly update over 7 days {err}")
            cursor.execute("INSERT INTO log (message, level) VALUES (%s, %s)", (f"failed to regularly update over 7 days {err}", "ERROR",))
            
    if days_since_30 >= 30:
        try:
            await send_report(bot, channel_id, 30)
            last_30 = today
            cursor.execute("INSERT INTO log (message, level) VALUES (%s, %s)", ("regular update over 30 days", "INFO"))
            logger. info("regular update over 30 days") 
        except Exception as err:
            cursor.execute("INSERT INTO log (message, level) VALUES (%s, %s)", (f"failed to regularly update over 30 days {err}", "ERROR",))
            logger.error(f"failed to regularly update over 30 days {err}")

    if days_since_180 >= 180:
        try:
            await send_report(bot, channel_id, 180)
            last_180 = today
            cursor.execute("INSERT INTO log (message, level) VALUES (%s, %s)", ("regular update over 180 days", "INFO"))
            logger.info("regular update over 180 days")
        except Exception as err:
            cursor.execute("INSERT INTO log (message, level) VALUES (%s, %s)", (f"failed to regularly update over 180 days {err}", "ERROR",))
            logger.error(f"failed to regularly update over 180 days {err}")
    else:
        cursor.close()
        conn.commit()
    return last_7, last_30, last_180