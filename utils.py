from datetime import datetime, timedelta
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')
sia = SentimentIntensityAnalyzer()

async def get_messages(bot, channel_id, days):
    channel = bot.get_channel(channel_id)
    messages = []
    if channel:
        now = datetime.utcnow()
        after_date = now - timedelta(days=days)
    async for message in channel.history(limit=None, after=after_date):
        messages.append(message)    
    return messages


async def analyze(messages):
    if not messages: 
        return 0
    scores = [sia.polarity_scores(msg.content)['compound'] for msg in messages]
    if scores:
        avg_compound = sum(scores) / len(scores)
        return avg_compound
    print(avg_compound)
    return 0

async def send_report(bot, channel_id, days):
    messages = await get_messages(bot, channel_id, days)
    channel = bot.get_channel(channel_id)
    if not messages:
        await channel.send("no data found to be analyzed")
        return
    scores = await analyze(messages)
    label = ("Investors are generally happy with the current market state" 
            if scores > 0.1 else "Investors are unhappy with the current state of the market"
            if scores < -0.1 else "Investors are neutral with the current sate of the market")
    await channel.send(f"{label}")