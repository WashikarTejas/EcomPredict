"""
Linear Regression Forecasting Model Wrapper.
Fits linear regression model on time features, lags, and rolling averages.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

class LinearRegressionForecaster:
    """
    Linear Regression wrapper for daily time-series demand forecasting.
    """

    def __init__(self):
        self.model = LinearRegression()

    def fit(self, X: pd.DataFrame, y: pd.Series):
        """Fits Linear Regression model."""
        # Fill any remaining NaNs in features with 0
        X_clean = X.fillna(0.0)
        self.model.fit(X_clean, y)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Generates predictions and ensures non-negative demand outputs."""
        X_clean = X.fillna(0.0)
        preds = self.model.predict(X_clean)
        return np.maximum(preds, 0.0)
