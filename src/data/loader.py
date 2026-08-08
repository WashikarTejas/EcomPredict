"""
Data Loader Module for E-Commerce Sales Intelligence.
Loads raw transaction CSV data into Pandas DataFrame.
"""

import os
import pandas as pd
from typing import Optional

REQUIRED_COLUMNS = [
    "order_id",
    "order_date",
    "customer_id",
    "product_id",
    "product_name",
    "category",
    "region",
    "quantity",
    "unit_price",
    "discount",
    "cost"
]

def load_raw_data(file_path: str = "data/raw/raw_sales.csv") -> pd.DataFrame:
    """
    Loads raw CSV data from file_path, validates required columns exist,
    and returns a DataFrame.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Raw data file not found at path: {file_path}")
        
    df = pd.read_csv(file_path)
    
    # Check for missing required columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in dataset: {missing_cols}")
        
    return df
