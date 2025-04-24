import re 
from datetime import datetime, timedelta
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import mysql.connector
import os 
from dotenv import load_dotenv
import logging
from datetime import date
import emoji

load_dotenv()

nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

def is_emoji(message: str) -> bool:
    pattern = re.sub(r"<a?:\w+:\d+>", "", message)
    without_emoji = emoji.replace_emoji(pattern, "")
    return len(without_emoji.strip()) == 0



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
                print("fetching")
                try:
                    cursor.execute("INSERT IGNORE INTO messages (id, author_name, author_id, message, message_send_timestamp, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (msg.id, msg.author.name, msg.author.id, msg.content, msg.created_at, datetime.utcnow(), datetime.utcnow()))
                except mysql.connector.Error as err:
                    logging.error(f"failed to insert message {err}")

        cursor.close()  
        conn.commit()


async def get_messages(days):
    cursor = conn.cursor()
    cursor.execute("SELECT message FROM messages WHERE message_send_timestamp BETWEEN NOW() - INTERVAL %s DAY AND NOW()", (days,))
    messages = cursor.fetchall()
    result = [msg[-1] for msg in messages]
    cursor.close()
    return result

    

async def analyze(messages):
    print(len(messages))
    if not messages: 
        logging.info("no messages to analyze")
        return 0
    scores = [sia.polarity_scores(msg)['compound'] for msg in messages]
    if scores:
        avg_compound = sum(scores) / len(scores)
        logging.info(f"average compound score {avg_compound}")
        return avg_compound
    logging.info("no valid sentiment score found")
    return 0

async def send_report(bot, channel_id, days):
    messages = await get_messages(days)
    channel = bot.get_channel(channel_id)
    if not messages:
        await channel.send("no data found to be analyzed")
        return
    scores = await analyze(messages)
    label = (f"for the past ({days}) days Investors are generally happy with the current market state" 
            if scores > 0.1 else f"for the past ({days}) days Investors are unhappy with the current state of the market"
            if scores < -0.1 else f"for the past ({days}) days Investors are neutral with the current sate of the market")
    await channel.send(f"{label}")

async def regular_update(last_7: date, last_30: date, last_180: date, bot, channel_id):
    today = date.today()
    days_since_7 = (today - last_7).days
    days_since_30 = (today - last_30).days
    days_since_180 = (today - last_180).days

    if days_since_7 >= 7:
        try:
            await send_report(bot, channel_id, 7)
            last_7 = today
            logging.info("regular update over 7 days")
        except Exception as err:
            logging.error(f"failed to regularly update over 7 days {err}")
            
    if days_since_30 >= 30:
        try:
            await send_report(bot, channel_id, 30)
            last_30 = today
            logging.info("regular update over 30 days ")
        except Exception as err:
            logging.error(f"failed to regularly update over 30 days {err}")    

    if days_since_180 >= 180:
        try:
            await send_report(bot, channel_id, 180)
            last_180 = today
            logging.info("regular update over 180 days")
        except Exception as err:
            logging.error(f"failed to regualrly update over 180 days {err}")    
            
    return last_7, last_30, last_180