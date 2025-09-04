# Astuces / a vérifier à la fin

- ✅ contrairement à ce que nous avons fait dans le cours, préférer un `start_date` statique.
- ✅ passer la plupart des arguments communs aux différentes tâches dans l'argument `default_args` dans la définition du DAG
- ⚠️ implémenter des tâches de vérifications avec des Sensors notamment après des insertions
- ✅ bien documenter les tâches et les DAG

# Instruction

Pour l'évaluation de ce cours, nous allons construire un DAG qui permet de récupérer des informations depuis une API de données météo disponible en ligne, les stocke, les transforme et entraîne un algorithme dessus.

## 0. Installation Airflow et téléchargement des nouvelles données

✅ **TERMINÉ** - Airflow 2.8.1 installé via Docker Compose avec CeleryExecutor

## 1. Récupération de données depuis l'API OpenWeatherMap

- ✅ Créez un compte sur OpenWeatherMap et connectez vous au compte
- ✅ Une fois connecté, on peut se rendre dans le menu My API keys.
    - ✅ Sur .env, API_KEY configurée
- ✅ Essayez la commande suivante en remplaçant api_key par votre clef
    - ✅ Test API validé : curl -X GET "https://api.openweathermap.org/data/2.5/weather?q=paris&appid=API_key"

**Réponse API exemple :**
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

## Tâche 1 - Collection de données

✅ **IMPLÉMENTÉE** - La première tâche consiste en la récupération des données depuis OpenWeatherMap: 

- ✅ Plusieurs requêtes pour avoir les données sur plusieurs villes
- ✅ Variable Airflow nommée `cities` configurée : `['paris', 'london', 'washington', 'belo horizonte']`
- ✅ Stockage des données au format JSON avec timestamp : `2025-09-04_16-33-27.json`
- ✅ Fichiers créés dans le dossier `/app/raw_files` (volume Docker)
- ✅ Utilisation des librairies `requests` et `json`

**🔧 Implémentation :** 
- DAG séparé `weather_data_collection` avec schedule `*/2 * * * *` (toutes les 2 minutes)
- Fonction `_fetch_and_save_weather_data()` dans `utils/weather_helpers.py`

# Tâches 2 et 3 - Transformation des données

✅ **TERMINÉES** - Les tâches (2) et (3) consistent à lire le contenu du dossier `/app/raw_files` et transformer les données au format CSV.

- ✅ **Tâche 2** : Prendre les 20 derniers fichiers, les concaténer → `data.csv`
- ✅ **Tâche 3** : Prendre tous les fichiers du dossier → `fulldata.csv`

**Usage des fichiers :**
- `data.csv` : Utilisé par le dashboard pour visualiser les dernières observations
- `fulldata.csv` : Utilisé pour entraîner l'algorithme ML

**🔧 Localisation des fichiers :** 
```bash
# Conteneur airflow_worker_1
docker exec -it airflow_dst_airflow-worker_1 bash
# Répertoires : /opt/airflow/raw_files → /opt/airflow/clean_data
# Mappés vers : /app/raw_files → /app/clean_data (volumes Docker)
```

**Vérification des fichiers générés :**
```bash
docker cp airflow_dst_airflow-worker_1:/opt/airflow/clean_data /home/ubuntu/airflow_dst/clean_data
```

# Tâches 4 et 5 - Entraînement et sélection de modèles

✅ **IMPLÉMENTÉES** - Les tâches (4', 4'', 4''') et (5) correspondent à l'entraînement et la sélection du meilleur modèle.

## Tâches 4 - Entraînement en parallèle

- ✅ **Tâche 4** : `LinearRegression` avec validation croisée
- ✅ **Tâche 4'** : `DecisionTreeRegressor` avec validation croisée
- ✅ **Tâche 4''** : `RandomForestRegressor` avec validation croisée

**🔧 Implémentation :**
- **TaskGroup** pour exécution en parallèle
- **Cross-validation** adaptative selon le nombre d'échantillons
- **XCom implicite** pour transmission des scores

## Tâche 5 - Sélection du meilleur modèle

✅ **IMPLÉMENTÉE** - Choix du meilleur modèle, réentraînement et sauvegarde.

**🔧 Fonctionnement :**
- Comparaison des scores de validation via XCom
- Réentraînement sur toutes les données
- Sauvegarde du modèle final avec `joblib`

# XCom implicite - Mécanisme de transmission des scores

✅ **FONCTIONNEL** - La tâche finale récupère les scores via XCom :

```python
def task_5_choose_best_model(data_paths: dict, lr_score: float, dt_score: float, rf_score: float):
```

**🔧 Principe :**
- Les paramètres `lr_score`, `dt_score`, et `rf_score` sont automatiquement récupérés depuis XCom grâce au décorateur `@task`
- **XCom implicite** : Quand une tâche décorée avec `@task` retourne une valeur, Airflow l'enregistre automatiquement dans XCom
- **Récupération automatique** : Quand une autre tâche a cette valeur en paramètre, Airflow la récupère automatiquement depuis XCom

## 🎯 Status Final du Projet

**Architecture :** 2 DAGs complémentaires
- ✅ `weather_data_collection` : Collection automatique (schedule: `*/2 * * * *`)
- ✅ `weather_training_pipeline` : Pipeline ML complet avec vérification de données

**Technologies utilisées :**
- ✅ Apache Airflow 2.8.1 avec décorateurs `@dag` et `@task`
- ✅ Docker Compose avec volumes partagés
- ✅ OpenWeatherMap API avec gestion des Variables
- ✅ Scikit-learn pour les modèles ML (LinearRegression, DecisionTree, RandomForest)
- ✅ TaskGroup pour parallélisation
- ✅ XCom pour communication entre tâches
- ✅ Validation croisée adaptative

**Fonctionnalités avancées :**
- ✅ Vérification automatique du nombre minimum d'observations (≥15)
- ✅ Pipeline robuste avec gestion d'erreurs
- ✅ Documentation complète des tâches
- ✅ Logs détaillés pour debugging

===

