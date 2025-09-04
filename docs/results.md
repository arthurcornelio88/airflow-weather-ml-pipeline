# Pipeline Weather ML - Résultats d'exécution

## 🏗️ Architecture du projet

### Choix de conception : Deux DAGs complémentaires

**Pourquoi deux DAGs séparés ?**

1. **`weather_data_collection`** (Collection automatique)
   - **Schedule** : `*/2 * * * *` - Collecte toutes les 2 minutes
   - **Rôle** : Alimenter continuellement la base de données météo
   - **Durée recommandée** : 15+ minutes pour accumuler ≥15 observations

2. **`weather_training_pipeline`** (Pipeline ML)
   - **Schedule** : `None` - Exécution manuelle sur demande
   - **Rôle** : Traitement des données et entraînement ML quand suffisamment de données
   - **Avantage** : Évite les exécutions inutiles sans données suffisantes

### Technologies clés utilisées

#### 🎯 Décorateurs Airflow 2.0+
```python
@dag(dag_id='weather_training_pipeline', schedule_interval=None, ...)
def weather_training_pipeline():
    
    @task
    def check_data_availability():
        # Logique de vérification
        return {"total_observations": count}
```

**Avantages des décorateurs :**
- Code plus propre et pythonique
- XCom implicite automatique
- Gestion native des types Python
- Debugging facilité

#### 🐳 Configuration Docker Compose
```yaml
volumes:
  - ./raw_files:/app/raw_files      # Données brutes
  - ./clean_data:/app/clean_data    # Données transformées
```

**Pourquoi `/app/...` au lieu de `/opt/airflow/...` ?**
- **Isolation** : Séparation des données Airflow et des données métier
- **Partage host-container** : Accès direct aux fichiers depuis l'hôte
- **Persistance** : Les données survivent aux redémarrages de containers

## 🚦 Résultats d'exécution

### Vérification des données (Gate condition)

### Vérification des données (Gate condition)

```
[2025-09-04, 17:55:31 UTC] {logging_mixin.py:188} INFO - Found 34 weather data files
[2025-09-04, 17:55:31 UTC] {logging_mixin.py:188} INFO - Total observations available: 136
[2025-09-04, 17:55:31 UTC] {logging_mixin.py:188} INFO - ✅ Data check PASSED: 136 observations from 34 files
[2025-09-04, 17:55:31 UTC] {logging_mixin.py:188} INFO - 🚀 Proceeding with data pipeline and ML training...
[2025-09-04, 17:55:31 UTC] {python.py:201} INFO - Done. Returned value was: {'total_files': 34, 'total_observations': 136}
```

**🔧 Mécanisme de protection :**
- **Condition d'arrêt** : `raise ValueError(f"❌ Insufficient data:")` si < 15 observations
- **Gate pattern** : Le pipeline ne démarre que si les conditions sont remplies
- **Feedback utilisateur** : Messages clairs sur l'état des données

### Transformation des données (Tasks 2-3)

**🔄 Pipeline de transformation :**

```
# Exemple de données transformées (data.csv / fulldata.csv)
      temperature          city  pression                 date
0       293.02           Paris      1013  2025-09-04 17-52-03
1       292.01          London      1009  2025-09-04 17-52-03
2       307.40      Washington      1011  2025-09-04 17-52-03
3       297.41  Belo Horizonte      1020  2025-09-04 17-52-03
4       293.02           Paris      1013  2025-09-04 17-50-03
5       292.01          London      1009  2025-09-04 17-50-03
6       307.40      Washington      1011  2025-09-04 17-50-03
7       298.05  Belo Horizonte      1020  2025-09-04 17-50-03
8       293.31           Paris      1013  2025-09-04 17-48-03
9       292.01          London      1009  2025-09-04 17-48-03

[2025-09-04, 17:55:34 UTC] {logging_mixin.py:188} INFO - Data saved to /app/clean_data/data.csv # si task_2
[2025-09-04, 18:10:02 UTC] {logging_mixin.py:188} INFO - Data saved to /app/clean_data/fulldata.csv # si task_3
```

**🛠️ Fonctionnalités de transformation :**
- **Task 2** : 20 fichiers les plus récents → `data.csv` (dashboard temps réel)
- **Task 3** : Tous les fichiers → `fulldata.csv` (entraînement ML)
- **Extraction intelligente** : JSON vers CSV avec colonnes standardisées
- **Tri temporel** : Données organisées par date et ville

### Entraînement ML parallèle (Task 4 - TaskGroup)

**🔧 Architecture TaskGroup :**
```python
with TaskGroup("task_4_model_scoring", tooltip="Parallel model training") as model_scoring_group:
    lr_score = task_4_score_linear_regression(prepared_data_paths)
    dt_score = task_4_score_decision_tree(prepared_data_paths)
    rf_score = task_4_score_random_forest(prepared_data_paths)
```

**Avantages du TaskGroup :**
- **Parallélisation** : Les 3 modèles s'entraînent simultanément
- **Organisation visuelle** : Groupement logique dans l'UI Airflow
- **Performance** : Réduction du temps total d'exécution
- **Isolation** : Chaque modèle dans son propre contexte

#### 🤖 Résultats d'entraînement

**Linear Regression :**
```
[2025-09-04, 18:10:09 UTC] {logging_mixin.py:188} INFO - Computing score with 120 samples using 3-fold CV
[2025-09-04, 18:10:09 UTC] {python.py:201} INFO - Done. Returned value was: -3.5513024605404553
[2025-09-04, 18:10:09 UTC] {taskinstance.py:1138} INFO - Marking task as SUCCESS.
```

**Decision Tree :**
```
[2025-09-04, 18:10:09 UTC] {logging_mixin.py:188} INFO - Computing score with 120 samples using 3-fold CV
[2025-09-04, 18:10:09 UTC] {python.py:201} INFO - Done. Returned value was: -19.811159999999894
[2025-09-04, 18:10:09 UTC] {taskinstance.py:1138} INFO - Marking task as SUCCESS.
```

**Random Forest :**
```
[2025-09-04, 18:10:09 UTC] {logging_mixin.py:188} INFO - Computing score with 120 samples using 3-fold CV
[2025-09-04, 18:10:10 UTC] {python.py:201} INFO - Done. Returned value was: -24.848305572050123
[2025-09-04, 18:10:10 UTC] {taskinstance.py:1138} INFO - Marking task as SUCCESS.
```

#### 📊 Tableau comparatif des performances

| Modèle | Score (neg_mean_squared_error) | Rang | Temps |
|--------|-------------------------------|------|-------|
| **Linear Regression** | **-3.55** | 🥇 1er | ~1s |
| Decision Tree | -19.81 | 🥈 2ème | ~1s |
| Random Forest | -24.85 | 🥉 3ème | ~2s |

**🎯 Analyse :**
- **Vainqueur** : Linear Regression (score le plus proche de 0)
- **Métrique** : `neg_mean_squared_error` - Plus proche de 0 = meilleur
- **Validation croisée adaptative** : 3-fold CV avec 120 échantillons
- **Feature engineering** : Variables dummy pour les villes

### XCom - Communication entre tâches

**🔄 Mécanisme XCom implicite avec les décorateurs :**

```python
# Les scores sont automatiquement transmis via XCom
def task_5_choose_best_model(data_paths: dict, lr_score: float, dt_score: float, rf_score: float):
    # lr_score = -3.55 (récupéré automatiquement depuis XCom)
    # dt_score = -19.81 (récupéré automatiquement depuis XCom) 
    # rf_score = -24.85 (récupéré automatiquement depuis XCom)
```

**Avantages de XCom implicite :**
- **Transparence** : Pas de `ti.xcom_pull()` explicite nécessaire
- **Type safety** : Les types Python sont préservés (float, dict, etc.)
- **Debugging facilité** : Valeurs visibles dans l'UI Airflow XCom
- **Code propre** : Focus sur la logique métier, pas la plomberie Airflow

*[Screenshot Airflow UI XCom à insérer ici montrant les valeurs transmises]*

### Sélection finale du modèle (Task 5)

```
[2025-09-04, 18:10:13 UTC] {logging_mixin.py:188} INFO - 🏆 Best model: linear_regression with score: -3.5513024605404553
[2025-09-04, 18:10:13 UTC] {logging_mixin.py:188} INFO - Saving model LinearRegression() to /app/clean_data/best_model.joblib
[2025-09-04, 18:10:13 UTC] {logging_mixin.py:188} INFO - ✅ Final model saved to: /app/clean_data/best_model.joblib
[2025-09-04, 18:10:13 UTC] {python.py:201} INFO - Done. Returned value was: /app/clean_data/best_model.joblib
```

**🧠 Logique de sélection :**
```python
# Comparaison automatique des scores XCom
models = {
    'linear_regression': (LinearRegression(), lr_score),    # -3.55
    'decision_tree': (DecisionTreeRegressor(), dt_score),  # -19.81
    'random_forest': (RandomForestRegressor(), rf_score),  # -24.85
}

# Le meilleur = score le plus proche de 0 (neg_mean_squared_error)
best_model_name = max(models, key=lambda name: models[name][1])
```

**🔧 Pipeline final :**
1. **Comparaison** : Analyse des 3 scores via XCom
2. **Sélection** : Linear Regression identifié comme meilleur (-3.55)
3. **Réentraînement** : Modèle retrained sur toutes les données (120 samples)
4. **Sauvegarde** : Persistance avec `joblib` dans `/app/clean_data/`

*[Screenshot XCom UI + Screenshot VS Code avec model sauvegardé à insérer]*

## 🎯 Points techniques remarquables

### Gestion de la robustesse
```python
# Adaptation dynamique de la validation croisée
def compute_model_score(model, X, y):
    n_samples = len(X)
    cv_folds = min(3, max(2, n_samples))  # Entre 2 et 3 folds selon les données
```

### Configuration Docker optimisée
- **Volumes persistants** : `/app/` pour données métier vs `/opt/airflow/` pour Airflow
- **Séparation des responsabilités** : raw_files (input) / clean_data (output)
- **Accès host** : Possibilité d'inspecter les fichiers directement

## 📈 Bilan du projet

**✅ Objectifs atteints :**
- Pipeline ML complet de A à Z
- Collecte automatique de données météo
- Entraînement de modèles en parallèle
- Sélection automatique du meilleur modèle
- Sauvegarde et persistance du modèle final

**🚀 Technologies maîtrisées :**
- Airflow 2.0+ avec décorateurs
- TaskGroup pour parallélisation
- XCom implicite pour communication
- Docker Compose avec volumes
- Scikit-learn pour ML
- API REST (OpenWeatherMap)
- Feature engineering automatique

**📊 Résultats quantitatifs :**
- 136 observations météo collectées
- 3 modèles entraînés simultanément  
- 120 échantillons pour l'entraînement final
- Linear Regression sélectionné (score: -3.55)
- Pipeline exécuté en ~5 minutes


