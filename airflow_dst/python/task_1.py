import requests
import json
from datetime import datetime
from dotenv import load_dotenv
import os

def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}")

def save_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)

if __name__ == "__main__":

    load_dotenv()
    api_key = os.getenv("API_KEY")

    cities = os.getenv("CITIES").strip("[]").replace("'", "").split(", ")
    print("Cities to fetch data for: ", cities)

    cities_json = {}

    for city in cities:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        data = fetch_data(url)
        # print("Fetched data from API: ", data)
        cities_json[city] = data
    
    now = datetime.now()
    filename = now.strftime("%Y-%m-%d %H:%M.json")
    os.makedirs("raw_files", exist_ok=True)
    save_to_file(cities_json, f"raw_files/{filename}")
    print(f"Data saved to raw_files/{filename}")
    