import json
import os
from datetime import datetime

import pandas as pd
import requests
from typing import List, Optional


def _fetch_and_save_weather_data(api_key: str, cities: List[str]) -> str:
    """
    Fetches weather data for a list of cities and saves it to a timestamped JSON file.
    """
    print(f"Fetching data for cities: {cities}")

    cities_json = {}
    for city in cities:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
            cities_json[city] = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Could not fetch data for {city}: {e}")
            continue  # Continue to the next city

    if not cities_json:
        raise ValueError("No data was fetched. Please check city names and API key.")

    now = datetime.now()
    filename = now.strftime("%Y-%m-%d_%H-%M-%S.json")

    # NOTE: This path is a mounted volume in the container
    save_dir = "/app/raw_files"
    os.makedirs(save_dir, exist_ok=True)

    filepath = os.path.join(save_dir, filename)
    with open(filepath, "w") as f:
        json.dump(cities_json, f, indent=4)

    print(f"Data successfully saved to {filepath}")
    return filepath



def _transform_data_into_csv(input_dir: str, output_dir: str, output_filename: str, n_files: Optional[int] = None):
    """
    Reads JSON files from an input directory, transforms the data,
    and saves it as a CSV file in the output directory.
    """
    # Find the most recent JSON files
    try:
        files = sorted(
            [f for f in os.listdir(input_dir) if f.endswith('.json')],
            reverse=True
        )
    except FileNotFoundError:
        print(f"Input directory not found: {input_dir}. Skipping transformation.")
        return

    if n_files:
        files = files[:n_files]

    if not files:
        print(f"No JSON files found in {input_dir}. Skipping transformation.")
        return

    print(f"Processing files: {files}")

    dfs = []
    for f in files:
        filepath = os.path.join(input_dir, f)
        with open(filepath, 'r') as file:
            data_temp = json.load(file)
        # The JSON contains city names as keys
        for city_name, data_city in data_temp.items():
            dfs.append({
                'temperature': data_city['main']['temp'],
                'city': data_city['name'],
                'pression': data_city['main']['pressure'],
                'date': f.split('.')[0].replace('_', ' ') # Reformat date from filename
            })

    df = pd.DataFrame(dfs)
    print('\\nTransformed DataFrame (head):')
    print(df.head(10))

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)
    df.to_csv(output_path, index=False)
    print(f"Data saved to {output_path}")
