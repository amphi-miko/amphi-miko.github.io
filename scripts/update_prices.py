import json
import requests
import time
from pathlib import Path
from datetime import datetime, timezone

item_info = {
    "Face Tattoos":{"id":176478961,"mcap":1},
    "Neck Tattoos":{"id":176478409,"mcap":1},
    "Santa Hat":{"id":176482232,"mcap":1},
    "Santa Jacket":{"id":176481264,"mcap":1},
    "Santa Trousers":{"id":176482233,"mcap":1},
    "Valentine Bear Head":{"id":176492719,"mcap":1},
    "Valentines Bear Top":{"id":176492722,"mcap":1},
    "Valentines Bear Trousers":{"id":176492721,"mcap":1},
    "Easter Bonnet":{"id":176508769,"mcap":1},
    "Easter Dungarees":{"id":176508770,"mcap":1},
    "Easter Slippers":{"id":176508771,"mcap":1},
    "Wizard Hat":{"id":176542129,"mcap":1},
    "Wizard Beard":{"id":176542131,"mcap":1},
    "Wizard Gown":{"id":176542130,"mcap":1},
    "Wizard Trousers":{"id":176542132,"mcap":1}
}
prices = {}

for item in item_names_ids:
    API_URL = f"https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid={item_info[item]["id"]}"  # <-- your real API URL here
    # Fetch data from API
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    data = response.json()
    # Extract price (adjust this key if needed)
    price = int(data["highest_buy_order"])
    # Example prices (replace with API results)
    prices[item] = {"price":price,"mcap":item_info[item]["mcap"]}
    time.sleep(3)

data = {
    "updated": datetime.now(timezone.utc).isoformat(),
    "currency": "USD",
    "items": prices,
}

output_file = Path("prices.json")
output_file.write_text(json.dumps(data, indent=2))

print("Updated prices.json")
