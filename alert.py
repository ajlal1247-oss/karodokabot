import yfinance as yf
import requests
import os

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
SYMBOL = "SILVERMIC.NS"

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

df = yf.download(SYMBOL, period="60d", interval="1d", progress=False)
df["SMA10"] = df["Close"].rolling(10).mean()
df["SMA20"] = df["Close"].rolling(20).mean()
df = df.dropna()

cur, prev = df.iloc[-1], df.iloc[-2]

if cur["Close"] > cur["SMA10"] and prev["Close"] <= prev["SMA10"]:
    send("MCX Silver crossed ABOVE SMA-10")

if cur["Close"] < cur["SMA10"] and prev["Close"] >= prev["SMA10"]:
    send("MCX Silver crossed BELOW SMA-10")

if cur["Close"] > cur["SMA20"] and prev["Close"] <= prev["SMA20"]:
    send("MCX Silver crossed ABOVE SMA-20")

if cur["Close"] < cur["SMA20"] and prev["Close"] >= prev["SMA20"]:
    send("MCX Silver crossed BELOW SMA-20")
