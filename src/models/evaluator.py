"""
Model Evaluation Metrics Module.
Computes MAE, RMSE, R², and safe MAPE for time-series forecasting.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def evaluate_model(y_true: np.ndarray, y_pred: np.ndarray, model_name: str = "Model") -> dict:
    """
    Evaluates predictions against true demand values and returns a dict of performance metrics.
    Handles zero values safely for MAPE calculations.
    """
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = float(r2_score(y_true, y_pred))
    
    # Safe MAPE calculation (ignoring y_true == 0 to prevent div by zero)
    non_zero_mask = y_true > 0
    if np.any(non_zero_mask):
        mape = float(np.mean(np.abs((y_true[non_zero_mask] - y_pred[non_zero_mask]) / y_true[non_zero_mask])) * 100.0)
    else:
        mape = 0.0

    return {
        "model": model_name,
        "mae": round(mae, 2),
        "rmse": round(rmse, 2),
        "r2": round(r2, 4),
        "mape_pct": round(mape, 2)
    }

def generate_comparison_table(metrics_list: list[dict]) -> pd.DataFrame:
    """Combines metrics dicts into a sorted model comparison DataFrame."""
    df_metrics = pd.DataFrame(metrics_list)
    # Sort by lowest RMSE then highest R2
    df_metrics = df_metrics.sort_values(by=["rmse", "r2"], ascending=[True, False]).reset_index(drop=True)
    return df_metrics
