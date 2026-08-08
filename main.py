"""
Main Orchestration Script for E-Commerce Sales Intelligence & Demand Forecasting Platform.
Runs end-to-end workflow: Data Ingestion -> Quality Validation -> Cleaning -> DB Seeding ->
SQL Analytics -> Export Pipeline -> ML Forecasting -> Inventory Recommendation Engine.
"""

import os
import pandas as pd
from generate_dataset import generate_ecommerce_data
from src.data import load_raw_data, DataValidator, DataCleaner
from src.database import seed_database, DatabaseRepository
from src.analytics import (
    get_overall_kpis, 
    get_monthly_sales_trend, 
    get_top_products, 
    get_category_performance,
    get_customer_summary, 
    get_regional_performance
)
from src.models import ForecastPipeline
from src.recommendations import InventoryRecommendationEngine

def run_pipeline():
    print("==================================================")
    print("  E-COMMERCE SALES INTELLIGENCE & FORECASTING     ")
    print("==================================================")

    # Step 1: Ensure Raw Dataset Exists
    raw_path = "data/raw/raw_sales.csv"
    inv_path = "data/raw/simulated_inventory.csv"
    if not os.path.exists(raw_path) or not os.path.exists(inv_path):
        print("-> Raw data missing. Generating realistic synthetic dataset...")
        generate_ecommerce_data(output_path=raw_path, inventory_path=inv_path)

    # Step 2: Data Ingestion & Quality Validation
    print("\n[PHASE 1] Data Ingestion & Validation...")
    raw_df = load_raw_data(raw_path)
    validator = DataValidator(raw_df)
    validator.run_validation()
    validator.print_summary()

    # Step 3: Data Cleaning & Preprocessing
    print("\n[PHASE 2] Data Cleaning & Metric Calculations...")
    cleaner = DataCleaner(raw_df)
    cleaned_df = cleaner.clean()
    cleaned_path = cleaner.save_cleaned_data("data/processed/cleaned_sales.csv")

    # Step 4: Database Setup & Seeding
    print("\n[PHASE 3] Database Setup & Star Schema Seeding...")
    db_path = "data/ecommerce.db"
    seed_database(cleaned_df, db_path=db_path)
    repo = DatabaseRepository(db_path=db_path)

    # Step 5: SQL & Python Analytics + Automated Exports
    print("\n[PHASE 4] Business Analytics & Generating CSV Exports...")
    os.makedirs("exports", exist_ok=True)
    
    kpis = get_overall_kpis(repo)
    print(f"-> Key Business Metrics: Revenue=${kpis['total_revenue']:,.2f} | Profit=${kpis['total_profit']:,.2f} | Margin={kpis['profit_margin_pct']}%")

    monthly_df = get_monthly_sales_trend(repo)
    monthly_df.to_csv("exports/sales_summary.csv", index=False)

    prod_df = get_category_performance(repo)
    prod_df.to_csv("exports/product_summary.csv", index=False)

    cust_df = get_customer_summary(repo)
    cust_df.to_csv("exports/customer_summary.csv", index=False)

    reg_df = get_regional_performance(repo)
    reg_df.to_csv("exports/regional_summary.csv", index=False)
    print("-> Successfully exported analytical summary CSVs to exports/")

    # Step 6: ML Demand Forecasting Pipeline
    print("\n[PHASE 5] Time-Series Demand Forecasting...")
    forecaster = ForecastPipeline(cleaned_df)
    forecast_results = forecaster.run_forecasting_pipeline(forecast_horizon=30)
    forecaster.save_forecast_results(
        forecast_results["combined_df"], 
        output_path="data/processed/forecast_results.csv",
        export_path="exports/forecast_results.csv"
    )

    # Step 7: Inventory Recommendation Engine
    print("\n[PHASE 6] Inventory Recommendation Engine...")
    inv_df = pd.read_csv(inv_path) if os.path.exists(inv_path) else None
    rec_engine = InventoryRecommendationEngine(cleaned_df, inventory_df=inv_df)
    rec_df = rec_engine.generate_recommendations(forecast_days=30)
    rec_engine.save_recommendations(
        rec_df,
        output_path="data/processed/inventory_recommendations.csv",
        export_path="exports/inventory_recommendations.csv"
    )

    print("\n==================================================")
    print("  END-TO-END PIPELINE COMPLETED SUCCESSFULLY!     ")
    print("==================================================")

if __name__ == "__main__":
    run_pipeline()
