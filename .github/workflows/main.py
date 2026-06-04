import yfinance as yf
import google.generativeai as genai
import requests
import os
from datetime import datetime

# 1. Setup the AI
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Fetch Market Data
print("Fetching data...")
nifty = yf.Ticker("^NSEI")
hist = nifty.history(period="2d")
current_price = round(hist['Close'].iloc[-1], 2)
prev_price = round(hist['Close'].iloc[-2], 2)
change = round(current_price - prev_price, 2)

market_summary = f"Nifty 50 closed at {current_price}, change {change} points."

# 3. Ask AI to write the newspaper
print("Generating report...")
prompt = f"""
You are the editor of 'Market Evening Express'. Today is {datetime.now().strftime("%d %b %Y")}.
Raw Data: {market_summary}
Write a short, exciting 2-paragraph evening summary for Indian stock market investors.
Use emojis to make it look like a news bulletin.
"""

response = model.generate_content(prompt)
blog_content = response.text

# 4. Publish to Telegram Channel
print("Publishing to Telegram...")
telegram_url = f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendMessage"

payload = {
    "chat_id": os.environ["TELEGRAM_CHAT_ID"],
    "text": blog_content,
    "parse_mode": "Markdown" # Allows bold text and emojis
}

response = requests.post(telegram_url, data=payload)

if response.status_code == 200:
    print("Success! Newspaper delivered to Telegram.")
else:
    print("Failed to publish:", response.text)
