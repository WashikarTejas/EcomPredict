"""
Unit Tests for Data Validation & Data Cleaning Modules.
"""

import pandas as pd
import pytest
from src.data.validator import DataValidator
from src.data.cleaner import DataCleaner

@pytest.fixture
def sample_raw_data():
    return pd.DataFrame([
        {
            "order_id": "ORD-001",
            "order_date": "2024-05-01",
            "customer_id": "CUST-101",
            "product_id": "PROD-1",
            "product_name": "Test Item",
            "category": "Electronics",
            "region": "North",
            "quantity": 2,
            "unit_price": 100.0,
            "discount": 0.10,
            "cost": 50.0
        },
        # Duplicate row
        {
            "order_id": "ORD-001",
            "order_date": "2024-05-01",
            "customer_id": "CUST-101",
            "product_id": "PROD-1",
            "product_name": "Test Item",
            "category": "Electronics",
            "region": "North",
            "quantity": 2,
            "unit_price": 100.0,
            "discount": 0.10,
            "cost": 50.0
        },
        # Invalid quantity row
        {
            "order_id": "ORD-002",
            "order_date": "2024-05-02",
            "customer_id": "CUST-102",
            "product_id": "PROD-2",
            "product_name": "Bad Qty Item",
            "category": "Apparel",
            "region": "South",
            "quantity": -1,
            "unit_price": 40.0,
            "discount": 0.0,
            "cost": 20.0
        },
        # Invalid discount row
        {
            "order_id": "ORD-003",
            "order_date": "2024-05-03",
            "customer_id": "CUST-103",
            "product_id": "PROD-3",
            "product_name": "High Disc Item",
            "category": "Furniture",
            "region": "East",
            "quantity": 1,
            "unit_price": 200.0,
            "discount": 1.5,
            "cost": 80.0
        }
    ])

def test_data_validator(sample_raw_data):
    validator = DataValidator(sample_raw_data)
    rep = validator.run_validation()
    assert rep["duplicate_records"] == 1
    assert rep["invalid_quantities"] == 1
    assert rep["invalid_discounts"] == 1

def test_data_cleaner(sample_raw_data):
    cleaner = DataCleaner(sample_raw_data)
    cleaned_df = cleaner.clean()
    
    # Check deduplication and negative quantity removal
    assert len(cleaned_df) == 2  # ORD-001 (1 copy) and ORD-003
    
    # Check discount clipping
    ord3 = cleaned_df[cleaned_df["order_id"] == "ORD-003"].iloc[0]
    assert ord3["discount"] == 1.0
    
    # Check metric calculations for ORD-001:
    # sales = 2 * 100 * (1 - 0.10) = 180.0
    # profit = 180 - (2 * 50) = 80.0
    # profit_margin = 80 / 180 = 0.4444
    ord1 = cleaned_df[cleaned_df["order_id"] == "ORD-001"].iloc[0]
    assert ord1["sales"] == 180.0
    assert ord1["profit"] == 80.0
    assert ord1["profit_margin"] == 0.4444
