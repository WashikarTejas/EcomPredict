"""
Unit Tests for Machine Learning Demand Forecasting Module.
"""

import numpy as np
import pandas as pd
import pytest
from src.features.feature_engineering import build_daily_demand_series, create_time_series_features
from src.models.evaluator import evaluate_model
from src.models.trainer import chronological_train_test_split

@pytest.fixture
def sample_daily_series():
    dates = pd.date_range("2024-01-01", periods=60, freq="D")
    demand = np.random.randint(10, 100, size=60)
    df = pd.DataFrame({"order_date": dates, "demand": demand})
    return df

def test_feature_engineering_no_leakage(sample_daily_series):
    feat_df = create_time_series_features(sample_daily_series)
    
    # Check that lag_1 at index 1 matches demand at index 0
    assert feat_df.loc[1, "lag_1"] == feat_df.loc[0, "demand"]
    
    # Check that rolling_mean_7 at index 7 equals average of index 0..6
    expected_rolling = feat_df.loc[0:6, "demand"].mean()
    assert round(feat_df.loc[7, "rolling_mean_7"], 4) == round(expected_rolling, 4)

def test_chronological_split(sample_daily_series):
    feat_df = create_time_series_features(sample_daily_series)
    X_train, X_test, y_train, y_test = chronological_train_test_split(feat_df, test_ratio=0.20)
    
    total = len(X_train) + len(X_test)
    assert len(X_test) == pytest.approx(total * 0.20, abs=2)

def test_evaluate_model():
    y_true = np.array([100, 150, 200, 250])
    y_pred = np.array([110, 140, 205, 245])
    
    metrics = evaluate_model(y_true, y_pred, model_name="TestModel")
    assert metrics["mae"] == 7.5
    assert metrics["rmse"] == 7.91
    assert metrics["r2"] > 0.95
