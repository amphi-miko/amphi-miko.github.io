import json
import requests
import time
from pathlib import Path
from datetime import datetime, timezone

with open("item_info.json", "r", encoding="utf-8") as f:
    data = json.load(f)

current_time_str = datetime.now(timezone.utc).isoformat()

for item in data:
    API_URL = f"https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid={data[item]['id']}"  # <-- your real API URL here
    # Fetch data from API
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    orderbook_data = response.json()
    # Extract price (adjust this key if needed)
    bid = int(orderbook_data["highest_buy_order"])
    ask = int(orderbook_data["lowest_sell_order"])
    listed = int(orderbook_data["sell_order_summary"].split('</span>')[0].split(">")[1])
    mcap = data[item]["qty"]*bid
    if "history" in data[item]:
        data[item]["history"].append({"timestamp":current_time_str,"ask":ask,"bid":bid,"mcap":mcap,"qty":listed})
        if len(data[item]["history"]) >= 13:
            data[item]["history"].pop(0)
    else:
        data[item]["history"] = [{"timestamp":current_time_str,"ask":ask,"bid":bid,"mcap":mcap,"qty":listed}]
    time.sleep(5)

output_file = Path("item_info.json")
output_file.write_text(json.dumps(data, indent=2))

print("Updated item_info.json")
