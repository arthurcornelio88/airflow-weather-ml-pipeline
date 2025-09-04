# Weather ML Pipeline with Apache Airflow

🌤️ **Complete weather data pipeline with machine learning model training using Apache Airflow 2.8.1**

## 🎯 Project Overview

This project implements a comprehensive data pipeline that:
- **Collects** weather data from OpenWeatherMap API
- **Transforms** raw JSON data into structured CSV datasets  
- **Trains** multiple ML regression models in parallel
- **Selects** the best performing model automatically
- **Saves** the final trained model for production use

## 🏗️ Architecture

### Two complementary DAGs:

1. **`weather_data_collection`** - Automated data collection
   - Schedule: Every 2 minutes (`*/2 * * * *`)
   - Continuously feeds weather data for training

2. **`weather_training_pipeline`** - ML training pipeline  
   - Schedule: Manual execution
   - Complete data processing and model training workflow

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenWeatherMap API key
- Python 3.8+

### Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd airflow-weather-ml-pipeline

# Copy environment template
cp .env.example .env
# Edit .env with your OpenWeatherMap API_KEY

# Start Airflow
cd airflow_dst
docker-compose up -d

# Access Airflow UI
# http://localhost:8080 (admin/admin)
```

### Usage
1. **Configure Variables** in Airflow UI:
   - `API_KEY`: Your OpenWeatherMap API key
   - `cities`: JSON array like `["paris", "london", "washington", "belo horizonte"]`

2. **Start Data Collection**:
   - Enable `weather_data_collection` DAG
   - Let it run for ~15 minutes to collect sufficient data

3. **Train Models**:
   - Manually trigger `weather_training_pipeline` DAG
   - Watch the complete ML pipeline execute

## 🔧 Technical Features

- **🎯 Task Decorators**: Modern Airflow 2.0+ syntax with `@dag` and `@task`
- **📦 TaskGroup**: Parallel model training for efficiency
- **🔄 XCom Integration**: Implicit parameter passing between tasks
- **🐳 Docker Volumes**: Clean data separation with `/app/` mounting
- **🛡️ Robust Pipeline**: Data validation, error handling, adaptive CV
- **📊 Model Selection**: Automatic best model selection based on cross-validation scores

## 📚 Documentation

Detailed documentation available in `/docs`:

- **[📋 Instructions](docs/instructions.md)** - Complete project walkthrough
- **[📈 Results](docs/results.md)** - Execution logs and technical analysis

## 🤖 ML Models Supported

- Linear Regression
- Decision Tree Regressor  
- Random Forest Regressor

Models are trained in parallel using TaskGroup and the best performer is automatically selected based on cross-validation scores.

## 📊 Project Structure

```
airflow_dst/
├── dags/
│   ├── weather_collection.py     # Data collection DAG
│   ├── weather_training_pipeline.py # ML training DAG
│   └── utils/
│       ├── weather_helpers.py    # API & transformation functions
│       └── train_helpers.py      # ML training functions
├── docker-compose.yaml           # Airflow infrastructure
├── raw_files/                    # Weather data (JSON)
├── clean_data/                   # Processed data (CSV) + models
└── logs/                         # Airflow logs
```

## 🏆 Results

With 136+ weather observations, the pipeline successfully:
- ✅ Collected and transformed weather data from 4 cities
- ✅ Trained 3 ML models in parallel using TaskGroup
- ✅ Selected Linear Regression as best performer (score: -3.55)
- ✅ Saved final model for production use

## 📄 License

This project is for educational purposes as part of an Apache Airflow course evaluation.
