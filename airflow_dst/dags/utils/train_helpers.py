from typing import Dict, List
import pandas as pd
from sklearn.model_selection import cross_val_score
from joblib import dump
import os

def compute_model_score(model, X: pd.DataFrame, y: pd.DataFrame) -> float:
    """Computes the model score using cross-validation."""
    # Adapt CV folds to the number of samples
    n_samples = len(X)
    cv_folds = min(3, max(2, n_samples))
    
    print(f"Computing score with {n_samples} samples using {cv_folds}-fold CV")
    
    if n_samples < 2:
        print("Warning: Less than 2 samples, returning dummy score")
        return -999.0  # Very bad score to indicate insufficient data
    
    cross_validation = cross_val_score(
        model,
        X,
        y,
        cv=cv_folds,
        scoring='neg_mean_squared_error'
    )
    return cross_validation.mean()

def train_and_save_model(model, X: pd.DataFrame, y: pd.DataFrame, path_to_model: str):
    """Trains the model and saves it to a file."""
    model.fit(X, y)
    print(f"Saving model {str(model)} to {path_to_model}")
    dump(model, path_to_model)

def prepare_data(path_to_data: str, output_dir: str) -> Dict[str, str]:
    """
    Reads raw data, prepares features and target, and saves them to separate files.
    Returns a dictionary with the paths to the saved files.
    """
    print(f"Preparing data from {path_to_data}")
    df = pd.read_csv(path_to_data)
    df = df.sort_values(['city', 'date'], ascending=True)

    # Check how many observations per city we have
    city_counts = df.groupby('city').size()
    print(f"Observations per city: {city_counts.to_dict()}")
    
    # Adapt the number of lag features to the available data
    min_observations = city_counts.min()
    max_lags = max(1, min_observations - 1)  # At least 1, but not more than available data - 1
    print(f"Using {max_lags} lag features (based on minimum {min_observations} observations per city)")

    dfs = []
    for c in df['city'].unique():
        df_temp = df[df['city'] == c].copy()
        df_temp['target'] = df_temp['temperature'].shift(-1)  # Predict next temperature
        
        # Only create lag features that we can actually use
        for i in range(1, min(max_lags + 1, 4)):  # Limit to maximum 3 lag features
            df_temp[f'temp_lag_{i}'] = df_temp['temperature'].shift(i)
        
        df_temp = df_temp.dropna()
        if len(df_temp) > 0:
            dfs.append(df_temp)

    if len(dfs) == 0:
        # If no data remains, create a simple model without lags
        print("No data with lags available, creating simple features")
        df_final = df.copy()
        df_final['target'] = df_final['temperature']  # Use current temp as both feature and target for demo
        df_final = df_final.drop(['date'], axis=1)
    else:
        df_final = pd.concat(dfs, axis=0, ignore_index=True)
        df_final = df_final.drop(['date'], axis=1)
    
    df_final = pd.get_dummies(df_final, columns=['city'])

    features = df_final.drop(['target'], axis=1)
    target = df_final['target']

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Save features and target to files
    features_path = os.path.join(output_dir, 'features.csv')
    target_path = os.path.join(output_dir, 'target.csv')
    features.to_csv(features_path, index=False)
    target.to_csv(target_path, index=False, header=True)

    print(f"Features saved to {features_path}")
    print(f"Target saved to {target_path}")

    return {'features_path': features_path, 'target_path': target_path}
