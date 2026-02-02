import yfinance as yf
import pandas as pd
from telegram.ext import Application, CommandHandler
from telegram import Bot
import os
import asyncio

from config import BOT_TOKEN, CHAT_ID, SYMBOL, PRICE_FILE, STATE_FILE

bot = Bot(BOT_TOKEN)

def fetch_data():
    df = yf.download(SYMBOL, period="90d", interval="1d", progress=False)
    df["SMA10"] = df["Close"].rolling(10).mean()
    df["SMA20"] = df["Close"].rolling(20).mean()
    df["SMA50"] = df["Close"].rolling(50).mean()
    return df.dropna()

async def status(update, context):
    df = fetch_data()
    c, p1, p2 = df.iloc[-1], df.iloc[-2], df.iloc[-3]

    trend1 = "Up" if c["Close"] > p1["Close"] else "Down"
    trend2 = "Up" if p1["Close"] > p2["Close"] else "Down"

    msg = (
        f"MCX SILVER STATUS\n\n"
        f"Price: {c['Close']:.2f}\n"
        f"SMA10: {c['SMA10']:.2f} ({'Above' if c['Close']>c['SMA10'] else 'Below'})\n"
        f"SMA20: {c['SMA20']:.2f} ({'Above' if c['Close']>c['SMA20'] else 'Below'})\n"
        f"SMA50: {c['SMA50']:.2f}\n\n"
        f"Last candles:\n"
        f"Candle-1: {trend1}\n"
        f"Candle-2: {trend2}"
    )

    await update.message.reply_text(msg)

async def setprice(update, context):
    price = context.args[0]
    with open(PRICE_FILE, "w") as f:
        f.write(price)
    await update.message.reply_text(f"Alert price set at {price}")

async def auto_alert_loop():
    while True:
        df = fetch_data()
        cur, prev = df.iloc[-1], df.iloc[-2]

        state = open(STATE_FILE).read() if os.path.exists(STATE_FILE) else ""

        if cur["Close"] > cur["SMA10"] and state != "ABOVE":
            bot.send_message(chat_id=CHAT_ID, text="Silver crossed ABOVE SMA-10")
            open(STATE_FILE, "w").write("ABOVE")

        if cur["Close"] < cur["SMA10"] and state != "BELOW":
            bot.send_message(chat_id=CHAT_ID, text="Silver crossed BELOW SMA-10")
            open(STATE_FILE, "w").write("BELOW")

        await asyncio.sleep(3600)  # hourly

async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("setprice", setprice))

    asyncio.create_task(auto_alert_loop())
    await app.run_polling()

asyncio.run(main())
