from __future__ import annotations

import json
import os
from datetime import datetime

import requests
import pandas as pd
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.utils.task_group import TaskGroup
from dotenv import load_dotenv

from utils.weather_helpers import _fetch_and_save_weather_data, _transform_data_into_csv
from utils.train_helpers import prepare_data, compute_model_score, train_and_save_model
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor


@dag(
    dag_id='weather_training_pipeline',
    schedule_interval=None,  # Déclenché manuellement
    start_date=datetime(2025, 9, 4, 16, 0),
    catchup=False,
    max_active_runs=1,  # Une seule exécution à la fois
    tags=['training', 'ml', 'datascientest'],
    doc_md="""
    # Weather Training Pipeline

    This DAG processes collected weather data and trains ML models.
    It automatically checks if enough data is available before starting.

    ### Structure:
    1. **Data Check**: Verifies at least 15 observations exist
    2. **Data Pipeline**: Transform raw JSON to CSV (tasks 2-3)  
    3. **ML Training**: Prepare data, train models, select best (tasks 4-5)

    ### Prerequisites:
    Run the 'weather_data_collection' DAG first to collect sufficient data.
    """
)
def weather_training_pipeline():
    """
    ### Weather Training Pipeline
    Complete pipeline from data verification to model training.
    """

    @task
    def check_data_availability():
        """
        ### Data Check: Verify Sufficient Data

        Checks if we have enough weather data for meaningful ML training.
        Requires at least 15 observations. If not enough data, the DAG stops here.
        """
        import glob
        
        raw_files = glob.glob("/app/raw_files/*.json")
        total_files = len(raw_files)
        
        print(f"Found {total_files} weather data files")
        
        # Count total observations by reading the files
        total_observations = 0
        for file in raw_files:
            with open(file, 'r') as f:
                data = json.load(f)
                total_observations += len(data)
        
        print(f"Total observations available: {total_observations}")
        
        if total_observations < 15:
            raise ValueError(f"❌ Insufficient data: only {total_observations} observations found. "
                           f"Need at least 15. Run 'weather_data_collection' DAG longer.")
        
        print(f"✅ Data check PASSED: {total_observations} observations from {total_files} files")
        print(f"🚀 Proceeding with data pipeline and ML training...")
        return {"total_files": total_files, "total_observations": total_observations}

    @task
    def task_2_transform_recent_data():
        """
        ### Task 2: Transform Recent Data (Data Pipeline)

        Reads the **20 most recent** JSON files from raw data,
        extracts key weather information, and creates `data.csv`.
        """
        _transform_data_into_csv(
            input_dir="/app/raw_files",
            output_dir="/app/clean_data",
            output_filename="data.csv",
            n_files=20
        )

    @task
    def task_3_transform_all_data():
        """
        ### Task 3: Transform All Data (Data Pipeline)

        Reads **all** available JSON files from raw data,
        creates the complete dataset `fulldata.csv` for ML training.
        """
        _transform_data_into_csv(
            input_dir="/app/raw_files",
            output_dir="/app/clean_data",
            output_filename="fulldata.csv"
            # n_files is omitted to process all files
        )

    @task
    def task_4_prepare_training():
        """
        ### Task 4: Prepare Training Data (ML Training)

        Prepares features and target from `fulldata.csv`.
        Creates engineered features and saves datasets for model training.
        """
        return prepare_data(
            path_to_data="/app/clean_data/fulldata.csv",
            output_dir="/app/clean_data"
        )

    @task
    def task_4_score_linear_regression(data_paths: dict):
        """
        ### Task 4': Score Linear Regression (ML Training)

        Trains and evaluates Linear Regression model using cross-validation.
        """
        X = pd.read_csv(data_paths['features_path'])
        y = pd.read_csv(data_paths['target_path']).iloc[:, 0]
        return compute_model_score(LinearRegression(), X, y)

    @task
    def task_4_score_decision_tree(data_paths: dict):
        """
        ### Task 4'': Score Decision Tree (ML Training)

        Trains and evaluates Decision Tree model using cross-validation.
        """
        X = pd.read_csv(data_paths['features_path'])
        y = pd.read_csv(data_paths['target_path']).iloc[:, 0]
        return compute_model_score(DecisionTreeRegressor(), X, y)

    @task
    def task_4_score_random_forest(data_paths: dict):
        """
        ### Task 4''': Score Random Forest (ML Training)

        Trains and evaluates Random Forest model using cross-validation.
        """
        X = pd.read_csv(data_paths['features_path'])
        y = pd.read_csv(data_paths['target_path']).iloc[:, 0]
        return compute_model_score(RandomForestRegressor(), X, y)

    @task
    def task_5_choose_best_model(data_paths: dict, lr_score: float, dt_score: float, rf_score: float):
        """
        ### Task 5: Choose and Train Best Model (ML Training)

        Compares model scores, selects the best performer,
        retrains it on full dataset, and saves the final model.
        """
        models = {
            'linear_regression': (LinearRegression(), lr_score),
            'decision_tree': (DecisionTreeRegressor(), dt_score),
            'random_forest': (RandomForestRegressor(), rf_score),
        }

        # The best score is the one closest to 0 for neg_mean_squared_error
        best_model_name = max(models, key=lambda name: models[name][1])
        best_model, best_score = models[best_model_name]

        print(f"🏆 Best model: {best_model_name} with score: {best_score}")

        X = pd.read_csv(data_paths['features_path'])
        y = pd.read_csv(data_paths['target_path']).iloc[:, 0]
        
        model_path = f"/app/clean_data/best_model.joblib"
        train_and_save_model(best_model, X, y, model_path)
        print(f"✅ Final model saved to: {model_path}")
        return model_path

    # === PIPELINE EXECUTION ===
    
    # 1. Data Check (Gate condition)
    data_check = check_data_availability()
    
    # 2. Data Pipeline (Tasks 2-3)
    task2_instance = task_2_transform_recent_data()
    task3_instance = task_3_transform_all_data()
    data_check >> [task2_instance, task3_instance]

    # 3. ML Training Pipeline (Tasks 4-5)
    # Task 4: Prepare training data
    prepared_data_paths = task_4_prepare_training()
    task3_instance >> prepared_data_paths
    
    # Task 4': Model scoring in parallel
    with TaskGroup("task_4_model_scoring", tooltip="Parallel model training and scoring") as model_scoring_group:
        lr_score = task_4_score_linear_regression(prepared_data_paths)
        dt_score = task_4_score_decision_tree(prepared_data_paths)
        rf_score = task_4_score_random_forest(prepared_data_paths)

    # Task 5: Final model selection and training
    best_model = task_5_choose_best_model(
        data_paths=prepared_data_paths,
        lr_score=lr_score,
        dt_score=dt_score,
        rf_score=rf_score
    )

    # Set final dependencies
    prepared_data_paths >> model_scoring_group >> best_model

# Instantiate the DAG
weather_training_pipeline()