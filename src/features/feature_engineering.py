"""
Feature Engineering Module for Time-Series Demand Forecasting.
Aggregates sales into daily/weekly demand time-series, creates calendar features,
and generates historical lag and rolling window features while strictly avoiding data leakage.
"""

import numpy as np
import pandas as pd

def build_daily_demand_series(df: pd.DataFrame, entity_col: str = None) -> pd.DataFrame:
    """
    Aggregates cleaned sales DataFrame into a daily time series of total demand (quantity sold).
    If entity_col (e.g. 'category' or 'product_id') is specified, aggregates per entity per day.
    Fills missing dates in the sequence with 0 quantity demand.
    """
    df_copy = df.copy()
    df_copy["order_date"] = pd.to_datetime(df_copy["order_date"])
    
    group_cols = ["order_date"]
    if entity_col and entity_col in df_copy.columns:
        group_cols.append(entity_col)
        
    daily = df_copy.groupby(group_cols).agg(
        demand=("quantity", "sum"),
        sales=("sales", "sum"),
        avg_price=("unit_price", "mean")
    ).reset_index()

    if entity_col and entity_col in df_copy.columns:
        # Reindex complete date range per entity
        entities = daily[entity_col].unique()
        min_date = daily["order_date"].min()
        max_date = daily["order_date"].max()
        full_idx = pd.MultiIndex.from_product(
            [pd.date_range(min_date, max_date, freq="D"), entities],
            names=["order_date", entity_col]
        )
        daily = daily.set_index(["order_date", entity_col]).reindex(full_idx, fill_value=0).reset_index()
    else:
        min_date = daily["order_date"].min()
        max_date = daily["order_date"].max()
        full_dates = pd.date_range(min_date, max_date, freq="D")
        daily = daily.set_index("order_date").reindex(full_dates, fill_value=0).reset_index()
        daily.rename(columns={"index": "order_date"}, inplace=True)
        
    return daily

def create_time_series_features(daily_df: pd.DataFrame, target_col: str = "demand") -> pd.DataFrame:
    """
    Generates time features, lag features, and rolling statistics.
    Uses shift(1) prior to rolling calculations to ensure strictly historical data (no leakage).
    """
    df_feat = daily_df.copy().sort_values(by="order_date").reset_index(drop=True)
    
    # 1. Calendar Features
    df_feat["year"] = df_feat["order_date"].dt.year
    df_feat["month"] = df_feat["order_date"].dt.month
    df_feat["week"] = df_feat["order_date"].dt.isocalendar().week.astype(int)
    df_feat["quarter"] = df_feat["order_date"].dt.quarter
    df_feat["day_of_week"] = df_feat["order_date"].dt.dayofweek
    df_feat["is_weekend"] = df_feat["day_of_week"].isin([5, 6]).astype(int)

    # 2. Historical Demand Lag Features (Shifted by 1 or more to prevent leakage)
    df_feat["lag_1"] = df_feat[target_col].shift(1)
    df_feat["lag_7"] = df_feat[target_col].shift(7)
    df_feat["lag_14"] = df_feat[target_col].shift(14)
    df_feat["lag_30"] = df_feat[target_col].shift(30)

    # 3. Rolling Window Means (Computed on shift(1) to avoid leaking current target)
    shifted_target = df_feat[target_col].shift(1)
    df_feat["rolling_mean_7"] = shifted_target.rolling(window=7, min_periods=1).mean()
    df_feat["rolling_mean_14"] = shifted_target.rolling(window=14, min_periods=1).mean()
    df_feat["rolling_mean_30"] = shifted_target.rolling(window=30, min_periods=1).mean()
    df_feat["rolling_std_7"] = shifted_target.rolling(window=7, min_periods=1).std().fillna(0)

    return df_feat

def get_feature_columns() -> list[str]:
    """Returns list of feature column names used by ML models."""
    return [
        "year", "month", "week", "quarter", "day_of_week", "is_weekend",
        "lag_1", "lag_7", "lag_14", "lag_30",
        "rolling_mean_7", "rolling_mean_14", "rolling_mean_30", "rolling_std_7"
    ]
