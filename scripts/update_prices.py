import json
import requests
from pathlib import Path
from datetime import datetime, timezone

API_URL = "https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid=176482232"  # <-- your real API URL here
# Fetch data from API
response = requests.get(API_URL, timeout=10)
response.raise_for_status()

data = response.json()
# Extract price (adjust this key if needed)
price = int(data["highest_buy_order"])

# Example prices (replace with API results)
prices = {
    "Santa Hat": price,
}

data = {
    "updated": datetime.now(timezone.utc).isoformat(),
    "currency": "USD",
    "items": prices,
}

output_file = Path("prices.json")
output_file.write_text(json.dumps(data, indent=2))

print("Updated prices.json")
