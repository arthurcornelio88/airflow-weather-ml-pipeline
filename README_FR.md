# Weather ML Pipeline - Projet Airflow

🌤️ **Pipeline complet de données météorologiques avec Machine Learning**

Ce projet implémente un pipeline end-to-end utilisant Apache Airflow pour :
- Collecter des données météo depuis l'API OpenWeatherMap
- Transformer les données JSON en CSV
- Entraîner des modèles ML en parallèle
- Sélectionner automatiquement le meilleur modèle

## 🚀 Architecture

**2 DAGs Airflow complémentaires :**
- 🔄 **`weather_data_collection`** : Collecte automatique toutes les 2 minutes
- 🤖 **`weather_training_pipeline`** : Pipeline ML complet avec vérification des données

**Technologies :** Apache Airflow 2.8.1, Docker Compose, Scikit-learn, OpenWeatherMap API

## 📖 Documentation

### 📋 [Instructions de développement](docs/instructions.md)
Suivi complet du projet avec toutes les étapes cochées et détails d'implémentation.

### 📊 [Résultats et analyse technique](docs/results.md)
Analyse approfondie de l'architecture, résultats d'exécution, et commentaires sur les choix techniques :
- TaskGroup et parallélisation
- XCom implicite avec les décorateurs
- Configuration Docker avec volumes
- Feature engineering adaptatif
- Comparaison des modèles ML

## 🏗️ Structure du projet

```
airflow_dst/
├── dags/                          # 🎯 Code source principal
│   ├── weather_collection.py     # DAG de collecte automatique
│   ├── weather_training_pipeline.py  # DAG ML principal  
│   └── utils/                     # Fonctions utilitaires
├── docker-compose.yaml           # Configuration Docker Airflow
├── check_weather_data.sh         # Script de vérification des données
└── .env.example                  # Variables d'environnement exemple

docs/
├── instructions.md               # 📝 Suivi du développement
└── results.md                   # 📊 Analyse des résultats

```

## 🎯 Résultats

**136 observations météo** collectées automatiquement  
**3 modèles ML** entraînés en parallèle  
**Linear Regression** sélectionné comme meilleur modèle (score: -3.55)  
**Pipeline complet** exécuté en ~5 minutes  

---

*Projet développé dans le cadre du cours Apache Airflow - DataScientest*