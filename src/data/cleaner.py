"""
Data Cleaning Module for E-Commerce Sales Intelligence.
Cleans raw sales records, handles missing values, removes duplicates, validates numeric ranges,
calculates derived metric columns (Sales, Profit, Profit Margin), and exports cleaned_sales.csv.
"""

import os
import numpy as np
import pandas as pd

class DataCleaner:
    """
    Cleans raw DataFrame and produces a sanitized, standardized dataset ready for storage & modeling.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def clean(self) -> pd.DataFrame:
        """Executes full cleaning pipeline."""
        df = self.df
        
        # 1. Deduplicate records
        df = df.drop_duplicates()
        
        # 2. Convert order_date to datetime
        df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
        df = df.dropna(subset=["order_date"])
        
        # 3. Clean numeric columns
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
        df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
        df["discount"] = pd.to_numeric(df["discount"], errors="coerce")
        df["cost"] = pd.to_numeric(df["cost"], errors="coerce")
        
        # Filter out invalid quantities (must be > 0)
        df = df[df["quantity"] > 0]
        
        # Impute missing unit_price by median per product_id if available, else median of category
        df["unit_price"] = df.groupby("product_id")["unit_price"].transform(lambda x: x.fillna(x.median()))
        df = df.dropna(subset=["unit_price"])
        df = df[df["unit_price"] > 0]
        
        # Clip invalid discounts to valid range [0.0, 1.0]
        df["discount"] = df["discount"].fillna(0.0)
        df["discount"] = df["discount"].clip(lower=0.0, upper=1.0)
        
        # Fill missing categories and regions with default value
        df["category"] = df["category"].fillna("Unassigned")
        df["region"] = df["region"].fillna("Unassigned")
        df["customer_id"] = df["customer_id"].fillna("CUST-UNKNOWN")
        
        # Standardize strings
        df["category"] = df["category"].str.strip().str.title()
        df["region"] = df["region"].str.strip().str.title()
        
        # 4. Calculate Sales, Profit, and Profit Margin
        # Sales = quantity * unit_price * (1 - discount)
        df["sales"] = df["quantity"] * df["unit_price"] * (1.0 - df["discount"])
        df["sales"] = df["sales"].round(2)
        
        # Profit = sales - (quantity * cost)
        df["profit"] = df["sales"] - (df["quantity"] * df["cost"])
        df["profit"] = df["profit"].round(2)
        
        # Profit Margin = profit / sales (safe division)
        df["profit_margin"] = np.where(df["sales"] > 0, df["profit"] / df["sales"], 0.0)
        df["profit_margin"] = df["profit_margin"].round(4)
        
        # Sort by date
        df = df.sort_values(by="order_date").reset_index(drop=True)
        self.df = df
        return df

    def save_cleaned_data(self, output_path: str = "data/processed/cleaned_sales.csv") -> str:
        """Saves cleaned DataFrame to CSV file."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # Format order_date as string YYYY-MM-DD for clean CSV representation
        export_df = self.df.copy()
        export_df["order_date"] = export_df["order_date"].dt.strftime("%Y-%m-%d")
        export_df.to_csv(output_path, index=False)
        print(f"Cleaned dataset saved to: {output_path} ({len(export_df)} rows)")
        return output_path
