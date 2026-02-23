import os
import json
import time
import re
from pathlib import Path
from datetime import datetime, timezone
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC

def update_market_prices(item_info):
    current_time_str = datetime.now(timezone.utc).isoformat()
    for item in item_info:
        API_URL = f"https://steamcommunity.com/market/itemordershistogram?country=US&language=english&currency=1&item_nameid={item_info[item]['id']}"  # <-- your real API URL here
        # Fetch data from API
        response = requests.get(API_URL, timeout=10)
        time.sleep(7)
        response.raise_for_status()
        orderbook_data = response.json()
        # Extract price (adjust this key if needed)
        if "highest_buy_order" in orderbook_data and orderbook_data["highest_buy_order"]:
            bid = int(orderbook_data["highest_buy_order"])
        else:
            bid = 0
        if "lowest_sell_order" in orderbook_data and orderbook_data["lowest_sell_order"]:
            ask = int(orderbook_data["lowest_sell_order"])
        else:
            ask = None    
        if "sell_order_summary" in orderbook_data and orderbook_data["lowest_sell_order"]:
            listed = int(orderbook_data["sell_order_summary"].split('</span>')[0].split(">")[1])
        else:
            listed = 0          
        mcap = item_info[item]["qty"]*bid
        if "history" in item_info[item]:
            item_info[item]["history"].append({"timestamp":current_time_str,"ask":ask,"bid":bid,"mcap":mcap,"qty":listed})
            if len(item_info[item]["history"]) >= 85:
                item_info[item]["history"].pop(0)
        else:
            item_info[item]["history"] = [{"timestamp":current_time_str,"ask":ask,"bid":bid,"mcap":mcap,"qty":listed}]
        print(f"Updated price data of {item}")
    return item_info

def get_item_nameid(market_hash_name):
    url = f"https://steamcommunity.com/market/listings/590830/{market_hash_name}"
    
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    time.sleep(10)
    if response.status_code != 200:
        return None

    match = re.search(r"Market_LoadOrderSpread\(\s*(\d+)\s*\)", response.text)
    if match:
        return int(match.group(1))

    return None

def populate_nameids(item_data):
    for item in item_data:
        if "id" not in item_data[item]:
            nameid = get_item_nameid(item)
            item_data[item]["id"] = nameid
            print(f"Saved {item} nameid {nameid}")
        else:
            print(f"nameid already saved for {item}")
    return item_data

def write_data_summary(item_data):
    data_summary = {}

    for item in item_data:
        try:
            if "history" in item_data[item]:
                history = item_data[item]["history"]
                week_bid = history[0]["bid"]/100
                try:
                    day_bid = history[-13]["bid"]/100  
                except IndexError:
                    day_bid = history[0]["bid"]/100  
                bid = history[-1]["bid"]/100 
                if history[-1]["ask"]:              
                    ask = history[-1]["ask"]/100
                else:
                    ask = 0
                marketCap = history[-1]["mcap"] / 100
                if day_bid > 0:
                    day_change = (bid - day_bid) / day_bid
                else:
                    day_change = 0
                if week_bid > 0:
                    week_change = (bid - week_bid) / week_bid
                else:
                    week_change = 0
                data_summary[item] = {"bid" : bid,
                                    "ask" : ask,
                                    "marketCap" : marketCap,
                                    "dayChange" : day_change,
                                    "weekChange" : week_change}
            else:
                data_summary[item] = {"bid" : 0,
                                    "ask" : 0,
                                    "marketCap" : 0,
                                    "dayChange" : 0,
                                    "weekChange" : 0}     
        except TypeError: 
                data_summary[item] = {"bid" : 0,
                                    "ask" : 0,
                                    "marketCap" : 0,
                                    "dayChange" : 0,
                                    "weekChange" : 0}         

    output_file = Path("site_info.json")
    output_file.write_text(json.dumps(data_summary, indent=2))

    print("Updated site_info.json")

def get_store_items(driver):
    driver.get("https://sbox.game/itemstore")

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "itemicon"))
    )

    items = driver.find_elements(By.CLASS_NAME, "itemicon")
    print("Found:", len(items))

    store_items_id_dict = {}

    # Get the project root (one level above the script folder)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Path to the assets folder under the project root
    assets_dir = os.path.join(project_root, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    for item in items:
        # Title
        name = item.find_element(By.CLASS_NAME, "title").text.strip()

        # Image (inside .media)
        image_url = item.find_element(
            By.CSS_SELECTOR, ".media img"
        ).get_attribute("src")

        file_path = os.path.join(assets_dir, f"{name}.png")
        if os.path.exists(file_path):
            print(f"Skipped {file_path} (already exists)")
        else:
            response = requests.get(image_url)
            if response.status_code == 200:
                with open(file_path, "wb") as f:
                    f.write(response.content)
                print(f"Saved {file_path}")
            else:
                print(f"Failed to download {item} from {image_url}")            

        # Buy link
        link = item.find_element(
            By.CSS_SELECTOR, ".bottom a"
        ).get_attribute("href")

        # Extract item ID from URL
        item_id = int(link.rstrip("/").split("/")[-1])

        store_items_id_dict[name] = item_id

    return store_items_id_dict


def get_total_sales(driver, asset_id):
    driver.get(f"https://sbox.game/metrics/skins/{asset_id}")

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, "chartrender"))
    )

    # Wait a moment for chart to fully render
    time.sleep(5)

    chart_data = driver.execute_script("""
        var chartEl = document.querySelector('.chartrender');
        if (!chartEl) return null;
        var chart = echarts.getInstanceByDom(chartEl);
        if (!chart) return null;
        return chart.getOption();
    """)

    if not chart_data:
        return 0

    series = chart_data["series"]
    success_series = next((s for s in series if s["name"] == "Success"), None)

    if not success_series:
        return 0

    total_sales = sum(point[1] for point in success_series["data"])
    return total_sales


def main():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)

    try:
        print("Fetching store items...")
        store_items = get_store_items(driver)

        print(f"Found {len(store_items)} items on sale")

        with open("item_info.json", "r", encoding="utf-8") as f:
            item_data = json.load(f)
        
        for item_name, store_id in store_items.items():
            if item_name not in item_data:
                item_data[item_name] = {"store_id":store_id}
            total_sales = get_total_sales(driver, store_id)
            print(f"Collected all current sales for {item_name} (Store ID: {store_id})")
            item_data[item_name]["qty"]=total_sales
        
        item_data = populate_nameids(item_data)
        item_data = update_market_prices(item_data)

        output_file = Path("item_info.json")
        output_file.write_text(json.dumps(item_data, indent=2))
        
        write_data_summary(item_data)

    finally:
        driver.quit()
    
main()
