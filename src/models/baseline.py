"""
Moving Average Baseline Forecasting Model.
Uses simple trailing rolling mean as baseline demand forecast.
"""

import numpy as np
import pandas as pd

class MovingAverageBaseline:
    """
    Baseline model that predicts future demand using a simple N-day moving average.
    """

    def __init__(self, window_size: int = 7):
        self.window_size = window_size
        self.last_mean_ = 0.0

    def fit(self, X: pd.DataFrame, y: pd.Series):
        """Calculates baseline mean from historical training target."""
        if len(y) > 0:
            self.last_mean_ = float(y.tail(self.window_size).mean())
        else:
            self.last_mean_ = 0.0
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predicts constant moving average value or uses lag_1 if available."""
        if "rolling_mean_7" in X.columns and not X["rolling_mean_7"].isnull().all():
            preds = X["rolling_mean_7"].fillna(self.last_mean_).values
        elif "lag_1" in X.columns:
            preds = X["lag_1"].fillna(self.last_mean_).values
        else:
            preds = np.full(shape=(len(X),), fill_value=self.last_mean_)
        return np.maximum(preds, 0.0)
