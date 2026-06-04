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
"""

response = model.generate_content(prompt)
blog_content = response.text

# 4. Publish to Hashnode
print("Publishing to Hashnode...")
query = """
mutation PublishPost($input: PublishPostInput!) {
  publishPost(input: $input) { post { url } }
}
"""

variables = {
    "input": {
        "title": f"Market Evening Express — {datetime.now().strftime('%b %d, %Y')}",
        "contentMarkdown": blog_content,
        "publicationId": os.environ["HASHNODE_PUB_ID"],
        "tags": [{"name": "Stock Market", "slug": "stock-market"}]
    }
}

headers = {
    "Authorization": os.environ["HASHNODE_TOKEN"],
    "Content-Type": "application/json"
}

response = requests.post(
    "https://gql.hashnode.com",
    json={"query": query, "variables": variables},
    headers=headers
)

if "errors" in response.json():
    print("Failed to publish:", response.json()["errors"])
else:
    print("Success! Blog published.")
