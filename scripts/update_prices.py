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

with open("prices.json", "r", encoding="utf-8") as f:
    data = json.load(f)

current_time_str = datetime.now(timezone.utc).isoformat()

for item in item_info:
    API_URL = f"https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid={item_info[item]['id']}"  # <-- your real API URL here
    # Fetch data from API
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    orderbook_data = response.json()
    # Extract price (adjust this key if needed)
    bid = int(orderbook_data["highest_buy_order"])
    ask = int(orderbook_data["lowest_sell_order"])
    mcap = item_info[item]["qty"]*bid
    if item in data["items"]:
        data["items"][item]["history"].append({"timestamp":current_time_str,"ask":ask,"bid":bid,"mcap":mcap})
        if len(data["items"][item]["history"]) >= 13:
            data["items"][item]["history"].pop(0)
    else:
        data["items"][item] = {"history":[{"timestamp":current_time_str,"ask":ask,"bid":bid,"mcap":mcap}]}
    time.sleep(3)

output_file = Path("prices.json")
output_file.write_text(json.dumps(data, indent=2))

print("Updated prices.json")
