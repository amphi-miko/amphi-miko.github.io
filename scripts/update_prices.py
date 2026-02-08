import json
import requests
import time
from pathlib import Path
from datetime import datetime, timezone

item_names_ids = {
    "Santa Hat":176482232,
    "Santa Jacket":176481264,
    "Santa Trousers":176482233
}
prices = {}

for item in item_names_ids:
    API_URL = f"https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid={item_names_ids[item]}"  # <-- your real API URL here
    # Fetch data from API
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    data = response.json()
    # Extract price (adjust this key if needed)
    price = int(data["highest_buy_order"])
    # Example prices (replace with API results)
    prices[item] = price
    time.sleep(1)

data = {
    "updated": datetime.now(timezone.utc).isoformat(),
    "currency": "USD",
    "items": prices,
}

output_file = Path("prices.json")
output_file.write_text(json.dumps(data, indent=2))

print("Updated prices.json")
