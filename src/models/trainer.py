"""
Model Training and Comparison Module.
Performs chronological train/test split on time-series feature DataFrame,
trains baseline, linear regression, and random forest models, evaluates performance,
and selects the champion model.
"""

import pandas as pd
from typing import Tuple, Dict, Any
from .baseline import MovingAverageBaseline
from .linear_regression import LinearRegressionForecaster
from .random_forest import RandomForestForecaster
from .evaluator import evaluate_model, generate_comparison_table
from ..features.feature_engineering import get_feature_columns

def chronological_train_test_split(
    df_features: pd.DataFrame, 
    test_ratio: float = 0.20,
    target_col: str = "demand"
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Performs time-ordered split (no shuffle) into train and test sets.
    """
    # Filter out initial rows where long lags (e.g. lag_30) are NaN
    df_clean = df_features.dropna(subset=get_feature_columns()).reset_index(drop=True)
    
    n_records = len(df_clean)
    split_idx = int(n_records * (1.0 - test_ratio))
    
    feature_cols = get_feature_columns()
    X_train = df_clean.iloc[:split_idx][feature_cols]
    y_train = df_clean.iloc[:split_idx][target_col]
    
    X_test = df_clean.iloc[split_idx:][feature_cols]
    y_test = df_clean.iloc[split_idx:][target_col]
    
    return X_train, X_test, y_train, y_test

def train_and_compare_models(
    df_features: pd.DataFrame, 
    test_ratio: float = 0.20,
    target_col: str = "demand"
) -> Dict[str, Any]:
    """
    Trains all models, evaluates performance on test split, and returns models & evaluation summary.
    """
    X_train, X_test, y_train, y_test = chronological_train_test_split(df_features, test_ratio, target_col)
    
    models = {
        "Moving Average (7D)": MovingAverageBaseline(window_size=7),
        "Linear Regression": LinearRegressionForecaster(),
        "Random Forest Regressor": RandomForestForecaster(n_estimators=100, max_depth=8, random_state=42)
    }
    
    results = []
    trained_models = {}
    
    for name, m in models.items():
        m.fit(X_train, y_train)
        preds = m.predict(X_test)
        metrics = evaluate_model(y_test, preds, model_name=name)
        results.append(metrics)
        trained_models[name] = m

    df_comparison = generate_comparison_table(results)
    best_model_name = df_comparison.iloc[0]["model"]
    champion_model = trained_models[best_model_name]

    print("==================================================")
    print("             MODEL EVALUATION SUMMARY             ")
    print("==================================================")
    for _, row in df_comparison.iterrows():
        print(f"Model: {row['model']:25s} | MAE: {row['mae']:6.2f} | RMSE: {row['rmse']:6.2f} | R²: {row['r2']:6.4f}")
    print(f"-> Selected Champion Model: {best_model_name}")
    print("==================================================")

    return {
        "comparison_table": df_comparison,
        "best_model_name": best_model_name,
        "champion_model": champion_model,
        "all_models": trained_models,
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test
    }
