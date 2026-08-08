"""
Unit Tests for Business Analytics Modules.
"""

import pandas as pd
import pytest
from src.analytics.sales import get_overall_kpis
from src.analytics.products import get_top_products, get_category_performance
from src.analytics.regions import get_regional_performance

@pytest.fixture
def sample_cleaned_data():
    return pd.DataFrame([
        {
            "order_id": "ORD-1",
            "order_date": "2024-01-10",
            "customer_id": "CUST-A",
            "product_id": "P1",
            "product_name": "Laptop",
            "category": "Electronics",
            "region": "North",
            "quantity": 1,
            "unit_price": 1000.0,
            "discount": 0.0,
            "cost": 600.0,
            "sales": 1000.0,
            "profit": 400.0,
            "profit_margin": 0.40
        },
        {
            "order_id": "ORD-2",
            "order_date": "2024-01-15",
            "customer_id": "CUST-B",
            "product_id": "P2",
            "product_name": "Desk Chair",
            "category": "Furniture",
            "region": "South",
            "quantity": 2,
            "unit_price": 200.0,
            "discount": 0.10,
            "cost": 100.0,
            "sales": 360.0,
            "profit": 160.0,
            "profit_margin": 0.4444
        }
    ])

def test_overall_kpis(sample_cleaned_data):
    kpis = get_overall_kpis(df=sample_cleaned_data)
    assert kpis["total_revenue"] == 1360.0
    assert kpis["total_profit"] == 560.0
    assert kpis["total_orders"] == 2
    assert kpis["total_units_sold"] == 3
    assert kpis["avg_order_value"] == 680.0
    assert kpis["profit_margin_pct"] == 41.18

def test_top_products(sample_cleaned_data):
    top_p = get_top_products(df=sample_cleaned_data, limit=1)
    assert len(top_p) == 1
    assert top_p.iloc[0]["product_name"] == "Laptop"
    assert top_p.iloc[0]["total_revenue"] == 1000.0

def test_regional_performance(sample_cleaned_data):
    reg = get_regional_performance(df=sample_cleaned_data)
    assert len(reg) == 2
    north = reg[reg["region"] == "North"].iloc[0]
    assert north["total_revenue"] == 1000.0
    assert north["revenue_share_pct"] == 73.53
