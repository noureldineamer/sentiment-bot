import discord 
import utils
from discord.ext import tasks, commands
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
current_channel = os.getenv("current_channel")
regular_update_channel = os.getenv("regular_update_channel")

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
channel = bot.get_channel(current_channel)
bot.get_channel(current_channel)


@tasks.loop(hours=168)
async def report_over_7_days():
    await utils.send_report(bot, regular_update_channel, 7)

@tasks.loop(hours=720)
async def report_over_1_month():
    await utils.send_report(bot, regular_update_channel, 30)
    
@tasks.loop(hours=4320)
async def report_over_3_months():
    await utils.send_report(bot, regular_update_channel, 180)

@bot.command()
async def analyze(ctx, days, channel=channel):
    try:
        days = int(days)
        if days < 1 or days > 365:
            await ctx.author.send("invalid number of days")
            return
        await utils.send_report(bot, current_channel, days)
    except ValueError:
        await ctx.author.send("Invalid input! please enter a valid number between 1 and 31")
        return
    

@bot.event
async def on_ready():
    bot.get_channel(current_channel)
    print(f"logged in as {bot.user}")
    print("-----")
    if not report_over_7_days:
        report_over_7_days.start()
    if not report_over_1_month:
        report_over_1_month.start()

    if not report_over_3_months:
        report_over_3_months.start()


bot.run(TOKEN)