import yfinance as yf
import requests
import os
TARGET_PRICE = float(os.environ.get("TARGET_PRICE", "0"))

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

SYMBOL = "XAGUSD=X"   # Silver Spot (reliable)

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

df = yf.download(SYMBOL, period="90d", interval="1d", progress=False)

# SAFETY CHECK
if df is None or df.empty or len(df) < 25:
    print("No sufficient data. Skipping run.")
    exit(0)

df["SMA10"] = df["Close"].rolling(10).mean()
df["SMA20"] = df["Close"].rolling(20).mean()
df = df.dropna()

cur = df.iloc[-1]
prev = df.iloc[-2]

# --- SMA-10 CROSS ---
if cur["Close"] > cur["SMA10"] and prev["Close"] <= prev["SMA10"]:
    send(
    f"📉 Silver BELOW 10-day SMA\n"
    f"Price: {cur['Close']:.2f}\n"
    f"SMA-10: {cur['SMA10']:.2f}"
)


if cur["Close"] < cur["SMA10"] and prev["Close"] >= prev["SMA10"]:
    send(
    f"📉 Silver BELOW 10-day SMA\n"
    f"Price: {cur['Close']:.2f}\n"
    f"SMA-10: {cur['SMA10']:.2f}"
)


# --- SMA-20 CROSS ---
if cur["Close"] > cur["SMA20"] and prev["Close"] <= prev["SMA20"]:
    send(
    f"📉 Silver BELOW 20-day SMA\n"
    f"Price: {cur['Close']:.2f}\n"
    f"SMA-10: {cur['SMA10']:.2f}"
)

if cur["Close"] < cur["SMA20"] and prev["Close"] >= prev["SMA20"]:
   send(
    f"📉 Silver BELOW 20-day SMA\n"
    f"Price: {cur['Close']:.2f}\n"
    f"SMA-10: {cur['SMA10']:.2f}"
)

    
# --- CUSTOM PRICE ALERT ---
if TARGET_PRICE > 0:
    if prev["Close"] > TARGET_PRICE and cur["Close"] <= TARGET_PRICE:
        send(f"🎯 Silver hit BELOW your target price: {TARGET_PRICE}\nCurrent: {cur['Close']:.2f}")

    if prev["Close"] < TARGET_PRICE and cur["Close"] >= TARGET_PRICE:
        send(f"🎯 Silver hit ABOVE your target price: {TARGET_PRICE}\nCurrent: {cur['Close']:.2f}")

# --- TREND REVERSAL ---
prev_trend = "UP" if prev["Close"] > df.iloc[-3]["Close"] else "DOWN"
cur_trend = "UP" if cur["Close"] > prev["Close"] else "DOWN"

if prev_trend == "DOWN" and cur_trend == "UP":
    send(f"🔄 Bullish trend reversal detected\nPrice: {cur['Close']:.2f}")

if prev_trend == "UP" and cur_trend == "DOWN":
    send(f"🔄 Bearish trend reversal detected\nPrice: {cur['Close']:.2f}")

