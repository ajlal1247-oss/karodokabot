import yfinance as yf
import requests
import os

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
    send("🔔 Silver crossed ABOVE 10-day SMA")

if cur["Close"] < cur["SMA10"] and prev["Close"] >= prev["SMA10"]:
    send("🔔 Silver crossed BELOW 10-day SMA")

# --- SMA-20 CROSS ---
if cur["Close"] > cur["SMA20"] and prev["Close"] <= prev["SMA20"]:
    send("🔔 Silver crossed ABOVE 20-day SMA")

if cur["Close"] < cur["SMA20"] and prev["Close"] >= prev["SMA20"]:
    send("🔔 Silver crossed BELOW 20-day SMA")
