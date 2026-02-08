import requests
from pathlib import Path

API_URL = "https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid=176482232"  # <-- your real API URL here
PRICE_FILE = Path("number.txt")

# Fetch data from API
response = requests.get(API_URL, timeout=10)
response.raise_for_status()

data = response.json()

# Extract price (adjust this key if needed)
price = data["highest_buy_order"]

# Write price to file
PRICE_FILE.write_text("$" + str(price/100))

print(f"Updated price to {price}")
