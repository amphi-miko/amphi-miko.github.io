import json
import requests
import time
from pathlib import Path
from datetime import datetime, timezone

item_info = {
    "Face Tattoos":{"id":176478961,"qty":146},
    "Neck Tattoos":{"id":176478409,"qty":136},
    "Santa Hat":{"id":176482232,"qty":3235},
    "Santa Jacket":{"id":176481264,"qty":2075},
    "Santa Trousers":{"id":176482233,"qty":1968},
    "Valentine Bear Head":{"id":176492719,"qty":2906},
    "Valentines Bear Top":{"id":176492722,"qty":2276},
    "Valentines Bear Trousers":{"id":176492721,"qty":2173},
    "Easter Bonnet":{"id":176508769,"qty":3514},
    "Easter Dungarees":{"id":176508770,"qty":2184},
    "Easter Slippers":{"id":176508771,"qty":3195},
    "Wizard Hat":{"id":176542129,"qty":7316},
    "Wizard Beard":{"id":176542131,"qty":7384},
    "Wizard Gown":{"id":176542130,"qty":6189},
    "Wizard Trousers":{"id":176542132,"qty":6035}
}
prices = {}

for item in item_info:
    API_URL = f"https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid={item_info[item]['id']}"  # <-- your real API URL here
    # Fetch data from API
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    data = response.json()
    # Extract price (adjust this key if needed)
    bid = int(data["highest_buy_order"])
    ask = int(data["lowest_sell_order"])
    # Example prices (replace with API results)
    prices[item] = {"ask":ask,"bid":bid,"mcap":item_info[item]["qty"]*bid}
    time.sleep(3)

data = {
    "updated": datetime.now(timezone.utc).isoformat(),
    "currency": "USD",
    "items": prices,
}

output_file = Path("prices.json")
output_file.write_text(json.dumps(data, indent=2))

print("Updated prices.json")
