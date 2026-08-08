"""
Forecast Pipeline Module for E-Commerce Sales Intelligence.
Generates multi-step out-of-sample future demand forecasts across configurable horizons (7, 30, 60 days),
computes upper/lower confidence bounds, and exports forecast_results.csv.
"""

import os
import numpy as np
import pandas as pd
from datetime import timedelta
from typing import Dict, Any
from .trainer import train_and_compare_models
from ..features.feature_engineering import build_daily_demand_series, create_time_series_features, get_feature_columns

class ForecastPipeline:
    """
    Handles out-of-sample future forecasting using trained champion ML model.
    """

    def __init__(self, cleaned_df: pd.DataFrame):
        self.cleaned_df = cleaned_df
        self.daily_demand = build_daily_demand_series(cleaned_df)
        self.featured_df = create_time_series_features(self.daily_demand)

    def run_forecasting_pipeline(self, forecast_horizon: int = 30) -> Dict[str, Any]:
        """
        Trains models on historical data, selects champion model,
        and projects future demand for N days ahead.
        """
        train_results = train_and_compare_models(self.featured_df)
        champion_model = train_results["champion_model"]
        best_name = train_results["best_model_name"]
        best_metrics = train_results["comparison_table"].iloc[0]
        rmse = float(best_metrics["rmse"])

        # Determine last historical date
        last_date = self.featured_df["order_date"].max()
        future_dates = [last_date + timedelta(days=i) for i in range(1, forecast_horizon + 1)]

        # Multi-step autoregressive projection
        df_history = self.featured_df.copy()
        future_records = []

        for f_date in future_dates:
            # Recompute time and lag features on current history including latest predictions
            temp_feats = create_time_series_features(df_history)
            
            # Extract last row features for prediction
            last_feat_row = temp_feats.iloc[[-1]][get_feature_columns()]
            pred_demand = float(champion_model.predict(last_feat_row)[0])
            pred_demand = max(0.0, round(pred_demand, 2))

            # Confidence bounds (95% confidence interval using model RMSE)
            lower_bound = max(0.0, round(pred_demand - 1.96 * rmse, 2))
            upper_bound = round(pred_demand + 1.96 * rmse, 2)

            future_records.append({
                "order_date": f_date,
                "demand": pred_demand,
                "actual_demand": np.nan,
                "predicted_demand": pred_demand,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "is_forecast": 1,
                "model_used": best_name,
                "forecast_horizon": forecast_horizon
            })

            # Append predicted row back to history to calculate next lags
            new_hist_row = pd.DataFrame([{
                "order_date": f_date,
                "demand": pred_demand,
                "sales": np.nan,
                "avg_price": np.nan
            }])
            df_history = pd.concat([df_history[["order_date", "demand", "sales", "avg_price"]], new_hist_row], ignore_index=True)

        # Build Historical DataFrame format
        hist_df = self.featured_df[["order_date", "demand"]].copy()
        hist_df["actual_demand"] = hist_df["demand"]
        hist_df["predicted_demand"] = np.nan
        hist_df["lower_bound"] = np.nan
        hist_df["upper_bound"] = np.nan
        hist_df["is_forecast"] = 0
        hist_df["model_used"] = best_name
        hist_df["forecast_horizon"] = forecast_horizon

        forecast_df = pd.DataFrame(future_records)
        combined_df = pd.concat([hist_df, forecast_df], ignore_index=True)

        return {
            "historical_df": hist_df,
            "forecast_df": forecast_df,
            "combined_df": combined_df,
            "best_model_name": best_name,
            "metrics": best_metrics.to_dict(),
            "champion_model": champion_model
        }

    def save_forecast_results(
        self, 
        combined_df: pd.DataFrame, 
        output_path: str = "data/processed/forecast_results.csv",
        export_path: str = "exports/forecast_results.csv"
    ) -> pd.DataFrame:
        """Saves forecast results to processed and exports folders."""
        for path in [output_path, export_path]:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            export_df = combined_df.copy()
            export_df["order_date"] = pd.to_datetime(export_df["order_date"]).dt.strftime("%Y-%m-%d")
            export_df.to_csv(path, index=False)
            print(f"Saved forecast results to: {path} ({len(export_df)} rows)")
        return combined_df
