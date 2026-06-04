import yfinance as yf
import google.generativeai as genai
import requests
import os
from datetime import datetime

# 1. Setup the AI
try:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    print(f"AI Setup Error: {e}")

# 2. Fetch Market Data (Safely)
print("Fetching data...")
market_summary = "Market data unavailable today."
try:
    nifty = yf.Ticker("^NSEI")
    # Fetch 5 days of data to account for weekends/holidays
    hist = nifty.history(period="5d") 
    
    if len(hist) >= 2:
        current_price = round(hist['Close'].iloc[-1], 2)
        prev_price = round(hist['Close'].iloc[-2], 2)
        change = round(current_price - prev_price, 2)
        market_summary = f"Nifty 50 closed at {current_price}, change {change} points."
    else:
        market_summary = "Market was likely closed today (weekend/holiday). No price data available."
except Exception as e:
    print(f"Data Fetch Error: {e}")

# 3. Ask AI to write the newspaper
print("Generating report...")
try:
    prompt = f"""
    You are the editor of 'Market Evening Express'. Today is {datetime.now().strftime("%d %b %Y")}.
    Raw Data: {market_summary}
    Write a short, exciting 2-paragraph evening summary for Indian stock market investors.
    Use emojis to make it look like a news bulletin.
    """
    response = model.generate_content(prompt)
    blog_content = response.text
except Exception as e:
    print(f"AI Generation Error: {e}")
    blog_content = f"Market Update for {datetime.now().strftime('%d %b %Y')}: {market_summary}"

# 4. Publish to Telegram Channel
print("Publishing to Telegram...")
telegram_url = f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/sendMessage"

payload = {
    "chat_id": os.environ["TELEGRAM_CHAT_ID"],
    "text": blog_content
    # Removed Markdown parse mode to prevent formatting errors
}

try:
    response = requests.post(telegram_url, data=payload)
    if response.status_code == 200:
        print("Success! Newspaper delivered to Telegram.")
    else:
        print(f"Failed to publish. Status: {response.status_code}")
        print(f"Telegram said: {response.text}")
except Exception as e:
    print(f"Telegram Connection Error: {e}")
