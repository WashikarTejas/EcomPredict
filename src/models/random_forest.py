"""
Random Forest Regressor Forecasting Model Wrapper.
Fits non-linear ensemble random forest on time features, lags, and rolling averages.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

class RandomForestForecaster:
    """
    Random Forest Regressor wrapper for demand forecasting.
    """

    def __init__(self, n_estimators: int = 100, max_depth: int = 8, random_state: int = 42):
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=random_state,
            n_jobs=-1
        )

    def fit(self, X: pd.DataFrame, y: pd.Series):
        """Fits Random Forest Regressor."""
        X_clean = X.fillna(0.0)
        self.model.fit(X_clean, y)
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Generates predictions and ensures non-negative demand outputs."""
        X_clean = X.fillna(0.0)
        preds = self.model.predict(X_clean)
        return np.maximum(preds, 0.0)

    def get_feature_importances(self, feature_names: list[str]) -> pd.DataFrame:
        """Returns sorted DataFrame of feature importances."""
        importances = self.model.feature_importances_
        df_imp = pd.DataFrame({"feature": feature_names, "importance": importances})
        return df_imp.sort_values(by="importance", ascending=False).reset_index(drop=True)
