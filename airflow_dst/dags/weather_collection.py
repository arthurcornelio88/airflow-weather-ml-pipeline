from __future__ import annotations

import json
import os
from datetime import datetime, timedelta

import requests
import pandas as pd
from airflow.decorators import dag, task
from airflow.models.param import Param
from dotenv import load_dotenv

from utils.weather_helpers import _fetch_and_save_weather_data


@dag(
    dag_id='weather_data_collection',
    schedule_interval='*/2 * * * *',  # Toutes les 2 minutes
    start_date=datetime(2025, 9, 4, 16, 0),
    catchup=False,
    max_active_runs=1,  # Une seule exécution à la fois
    dagrun_timeout=timedelta(minutes=1),  # Timeout après 1 minute
    tags=['weather', 'collection', 'datascientest'],
    doc_md="""
    # Weather Data Collection

    This DAG collects weather data every 2 minutes from OpenWeatherMap API.
    Run this for about 15 minutes to collect enough data for ML training.

    ### Variables
    *   `API_KEY`: Your OpenWeatherMap API key.
    *   `cities`: A JSON list of cities to query (e.g., `["paris", "london"]`).
    """
)
def weather_collection_dag():
    """
    ### Weather Data Collection DAG
    Collects weather data every 2 minutes for ML training preparation.
    """

    @task
    def collect_weather_data():
        """
        ### Collect Weather Data

        Fetches current weather data from OpenWeatherMap API and saves it to a timestamped JSON file.
        This task runs every 2 minutes to accumulate training data.
        """
        from airflow.models import Variable
        
        api_key = Variable.get("API_KEY")
        cities = Variable.get("cities", deserialize_json=True)
        
        if not api_key:
            raise ValueError("API_KEY Airflow Variable not set.")
        
        filepath = _fetch_and_save_weather_data(api_key=api_key, cities=cities)
        
        # Count total files for monitoring
        import glob
        raw_files = glob.glob("/app/raw_files/*.json")
        print(f"Total weather files collected: {len(raw_files)}")
        
        return filepath

    # Single task execution
    collect_weather_data()

# Instantiate the DAG
weather_collection_dag()