# Tips / Final Checklist

- ✅ Unlike what we did in the course, prefer a static `start_date`.
- ✅ Pass most common arguments to different tasks in the `default_args` argument in the DAG definition
- ⚠️ Implement verification tasks with Sensors especially after insertions
- ✅ Document tasks and DAGs well

# Instructions

For the evaluation of this course, we will build a DAG that allows retrieving information from an online weather data API, stores it, transforms it and trains an algorithm on it.

## 0. Install Airflow and download new data

✅ **COMPLETED** - Airflow 2.8.1 installed via Docker Compose with CeleryExecutor

## 1. Retrieve data from OpenWeatherMap API

- ✅ Create an OpenWeatherMap account and log in to the account
- ✅ Once logged in, you can go to the My API keys menu.
    - ✅ On .env, API_KEY configured
- ✅ Try the following command by replacing api_key with your key
    - ✅ API Test validated: curl -X GET "https://api.openweathermap.org/data/2.5/weather?q=paris&appid=API_key"

**Example API response:**
```json
{
    "coord": {"lon":2.3488,"lat":48.8534},
    "weather": [{"id":803,"main":"Clouds","description":"broken clouds","icon":"04d"}],
    "base": "stations",
    "main": {"temp":294.24,"feels_like":294.1,"temp_min":294.03,"temp_max":294.92,"pressure":1012,"humidity":65, "sea_level":1012,"grnd_level":1002},
    "visibility": 10000,
    "wind": {"speed":5.66,"deg":200},
    "clouds": {"all":75},
    "dt": 1756995623,
    "sys": {"type":1,"id":6550,"country":"FR","sunrise":1756962709,"sunset":1757010472},
    "timezone": 7200,
    "id": 2988507,
    "name": "Paris",
    "cod": 200
}
```

## Task 1 - Data Collection

✅ **IMPLEMENTED** - The first task consists of retrieving data from OpenWeatherMap:

- ✅ Multiple requests to get data from several cities
- ✅ Airflow Variable named `cities` configured: `['paris', 'london', 'washington', 'belo horizonte']`
- ✅ Store data in JSON format with timestamp: `2025-09-04_16-33-27.json`
- ✅ Files created in `/app/raw_files` folder (Docker volume)
- ✅ Using `requests` and `json` libraries

**🔧 Implementation:**
- Separate DAG `weather_data_collection` with schedule `*/2 * * * *` (every 2 minutes)
- Function `_fetch_and_save_weather_data()` in `utils/weather_helpers.py`

# Tasks 2 and 3 - Data Transformation

✅ **COMPLETED** - Tasks (2) and (3) consist of reading the contents of `/app/raw_files` folder and transforming data to CSV format.

- ✅ **Task 2**: Take the 20 most recent files, concatenate them → `data.csv`
- ✅ **Task 3**: Take all files in the folder → `fulldata.csv`

**File usage:**
- `data.csv`: Used by dashboard to visualize recent observations
- `fulldata.csv`: Used to train the ML algorithm

**🔧 File location:**
```bash
# Container airflow_worker_1
docker exec -it airflow_dst_airflow-worker_1 bash
# Directories: /opt/airflow/raw_files → /opt/airflow/clean_data
# Mapped to: /app/raw_files → /app/clean_data (Docker volumes)
```

**Verify generated files:**
```bash
docker cp airflow_dst_airflow-worker_1:/opt/airflow/clean_data /home/ubuntu/airflow_dst/clean_data
```

# Tasks 4 and 5 - Model Training and Selection

✅ **IMPLEMENTED** - Tasks (4', 4'', 4''') and (5) correspond to training and selecting the best model.

## Tasks 4 - Parallel Training

✅ **Task 4'**: `LinearRegression` with cross-validation
✅ **Task 4''**: `DecisionTreeRegressor` with cross-validation  
✅ **Task 4'''**: `RandomForestRegressor` with cross-validation

**🔧 Implementation:**
- **TaskGroup** for parallel execution
- **Adaptive cross-validation** according to number of samples
- **Implicit XCom** for score transmission

## Task 5 - Best Model Selection

✅ **IMPLEMENTED** - Choose the best model, retrain and save.

**🔧 Functioning:**
- Compare validation scores via XCom
- Retrain on all data
- Save final model with `joblib`

# Implicit XCom - Score Transmission Mechanism

✅ **FUNCTIONAL** - The final task retrieves scores via XCom:

```python
def task_5_choose_best_model(data_paths: dict, lr_score: float, dt_score: float, rf_score: float):
```

**🔧 Principle:**
- Parameters `lr_score`, `dt_score`, and `rf_score` are automatically retrieved from XCom thanks to the `@task` decorator
- **Implicit XCom**: When a task decorated with `@task` returns a value, Airflow automatically records it in XCom
- **Automatic retrieval**: When another task has this value as parameter, Airflow automatically retrieves it from XCom

## 🎯 Final Project Status

**Architecture:** 2 complementary DAGs
- ✅ `weather_data_collection`: Automatic collection (schedule: `*/2 * * * *`)
- ✅ `weather_training_pipeline`: Complete ML pipeline with data verification

**Technologies used:**
- ✅ Apache Airflow 2.8.1 with `@dag` and `@task` decorators
- ✅ Docker Compose with shared volumes
- ✅ OpenWeatherMap API with Variables management
- ✅ Scikit-learn for ML models (LinearRegression, DecisionTree, RandomForest)
- ✅ TaskGroup for parallelization
- ✅ XCom for inter-task communication
- ✅ Adaptive cross-validation

**Advanced features:**
- ✅ Automatic verification of minimum number of observations (≥15)
- ✅ Robust pipeline with error handling
- ✅ Complete task documentation
- ✅ Detailed logs for debugging

===
