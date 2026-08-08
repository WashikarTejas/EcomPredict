"""
Unit Tests for Inventory Recommendation Engine.
"""

import pandas as pd
import pytest
from src.recommendations.engine import InventoryRecommendationEngine

@pytest.fixture
def sample_data():
    sales_df = pd.DataFrame([
        {
            "order_id": "ORD-1",
            "order_date": "2024-05-01",
            "customer_id": "C1",
            "product_id": "P101",
            "product_name": "High Demand Widget",
            "category": "Electronics",
            "quantity": 10,
            "unit_price": 50.0,
            "discount": 0.0,
            "cost": 25.0,
            "sales": 500.0,
            "profit": 250.0,
            "profit_margin": 0.50
        }
    ])
    
    inv_df = pd.DataFrame([
        {
            "product_id": "P101",
            "product_name": "High Demand Widget",
            "category": "Electronics",
            "current_stock": 20,
            "reorder_point": 100,
            "lead_time_days": 7
        }
    ])
    return sales_df, inv_df

def test_recommendation_stockout_classification(sample_data):
    sales_df, inv_df = sample_data
    engine = InventoryRecommendationEngine(sales_df, inventory_df=inv_df)
    recs = engine.generate_recommendations(forecast_days=30)
    
    assert len(recs) == 1
    row = recs.iloc[0]
    assert row["product_id"] == "P101"
    assert "explanation" in row and len(row["explanation"]) > 0
    assert "action_recommendation" in row and len(row["action_recommendation"]) > 0
