import os
import logging
from datetime import datetime, timedelta, date

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from dotenv import load_dotenv

load_dotenv()

log_path = os.getenv("LOG_PATH")
logger = logging.getLogger(__name__)
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    
)


nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

async def get_messages(bot, channel_id,days, limit=None):
    channel = bot.get_channel(channel_id)
    messages = []
    if channel:
        now = datetime.utcnow()
        after_date = now - timedelta(days=days)
    async for message in channel.history(limit=limit, after=after_date):
        messages.append(message)    
    return messages


async def analyze(messages):
    if not messages: 
        logging.info("no messages to analyze")
        return 0
    scores = [sia.polarity_scores(msg.content)['compound'] for msg in messages]
    if scores:
        avg_compound = sum(scores) / len(scores)
        logging.info(f"average compound score {avg_compound}")
        return avg_compound
    logging.info("no valid sentiment score found")
    return 0

async def send_report(bot, channel_id, days, limit):
    messages = await get_messages(bot, channel_id, days, limit)
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
            await send_report(bot, channel_id, 7, limit=None)
            last_7 = today
            logging.info("regular update over 7 days")
        except Exception as err:
            logging.error(f"failed to regularly update over 7 days {err}")
            
    if days_since_30 >= 30:
        try:
            await send_report(bot, channel_id, 30, limit=None)
            last_30 = today
            logging.info("regular update over 30 days ")
        except Exception as err:
            logging.error(f"failed to regularly update over 30 days {err}")    

    if days_since_180 >= 180:
        try:
            await send_report(bot, channel_id, 180, limit=None)
            last_180 = today
            logging.info("regular update over 180 days")
        except Exception as err:
            logging.error(f"failed to regualrly update over 180 days {err}")    
            
    return last_7, last_30, last_180
