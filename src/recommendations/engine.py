"""
Inventory Recommendation Engine for E-Commerce Sales Intelligence.
Analyzes product historical sales, forecasted demand, current stock, and lead time to produce
classified inventory categories (HIGH DEMAND, POTENTIAL STOCKOUT, POTENTIAL OVERSTOCK, etc.)
with clear, human-readable narrative explanations.
"""

import os
import numpy as np
import pandas as pd

class InventoryRecommendationEngine:
    """
    Generates data-driven inventory replenishment & risk recommendations.
    """

    def __init__(self, cleaned_sales_df: pd.DataFrame, inventory_df: pd.DataFrame = None):
        self.sales_df = cleaned_sales_df.copy()
        if inventory_df is not None:
            self.inv_df = inventory_df.copy()
        else:
            self.inv_df = self._generate_simulated_inventory()

    def _generate_simulated_inventory(self) -> pd.DataFrame:
        """Generates simulated stock levels if external inventory CSV is not provided."""
        prods = self.sales_df[["product_id", "product_name", "category"]].drop_duplicates(subset=["product_id"])
        inv_records = []
        for _, row in prods.iterrows():
            inv_records.append({
                "product_id": row["product_id"],
                "product_name": row["product_name"],
                "category": row["category"],
                "current_stock": np.random.randint(50, 600),
                "reorder_point": np.random.randint(100, 250),
                "lead_time_days": np.random.randint(5, 14)
            })
        return pd.DataFrame(inv_records)

    def generate_recommendations(self, forecast_days: int = 30) -> pd.DataFrame:
        """
        Calculates recent 30-day historical demand vs forecasted 30-day demand per product,
        compares against current stock, assigns demand category, stock status, and narrative explanation.
        """
        sales = self.sales_df.copy()
        sales["order_date"] = pd.to_datetime(sales["order_date"])
        
        # Calculate recent 30-day demand per product
        max_date = sales["order_date"].max()
        cutoff_30d = max_date - pd.Timedelta(days=30)
        recent_sales = sales[sales["order_date"] > cutoff_30d]
        
        hist_demand = recent_sales.groupby("product_id")["quantity"].sum().reset_index()
        hist_demand.rename(columns={"quantity": "past_30d_demand"}, inplace=True)
        
        # Merge with product catalog / inventory table
        inv = pd.merge(self.inv_df, hist_demand, on="product_id", how="left")
        inv["past_30d_demand"] = inv["past_30d_demand"].fillna(0)
        
        # Simple product demand forecasting (ratio/trend multiplier)
        # Forecasted 30d demand = past 30d demand * random trend factor between 0.85 and 1.25
        np.random.seed(42)
        inv["demand_trend_multiplier"] = np.random.uniform(0.85, 1.30, size=len(inv)).round(2)
        inv["forecasted_30d_demand"] = (inv["past_30d_demand"] * inv["demand_trend_multiplier"]).round().astype(int)

        recommendations = []
        for _, row in inv.iterrows():
            pid = row["product_id"]
            pname = row["product_name"]
            cat = row["category"]
            stock = int(row["current_stock"])
            reorder_pt = int(row.get("reorder_point", 150))
            past_d = int(row["past_30d_demand"])
            fcst_d = int(row["forecasted_30d_demand"])
            multiplier = float(row["demand_trend_multiplier"])
            lead_days = int(row.get("lead_time_days", 7))

            # Classification logic
            if multiplier >= 1.15:
                trend_cat = "INCREASING DEMAND"
            elif multiplier <= 0.90:
                trend_cat = "DECLINING DEMAND"
            elif past_d > 200:
                trend_cat = "HIGH DEMAND"
            elif past_d < 50:
                trend_cat = "LOW DEMAND"
            else:
                trend_cat = "STABLE DEMAND"

            # Stock status & action recommendation
            if stock < fcst_d:
                status = "POTENTIAL STOCKOUT"
                shortage = fcst_d - stock
                action = f"Replenish urgently. Projected 30-day demand ({fcst_d}) exceeds current stock ({stock}) by {shortage} units."
                explanation = f"Current stock ({stock}) is below forecasted demand ({fcst_d}). Lead time is {lead_days} days."
            elif stock > fcst_d * 2.5 and stock > reorder_pt:
                status = "POTENTIAL OVERSTOCK"
                excess = stock - fcst_d
                action = "Halt immediate replenishment & consider promotional discount."
                explanation = f"Current stock ({stock}) is more than 2.5x projected 30-day demand ({fcst_d}). Excess inventory: {excess} units."
            elif stock <= reorder_pt:
                status = "REORDER RECOMMENDED"
                action = f"Place purchase order within {lead_days} days to maintain buffer stock."
                explanation = f"Stock level ({stock}) has reached or dropped below reorder point ({reorder_pt})."
            else:
                status = "HEALTHY INVENTORY"
                action = "Maintain current replenishment schedule."
                explanation = f"Stock level ({stock}) is well-balanced to cover projected demand ({fcst_d})."

            recommendations.append({
                "product_id": pid,
                "product_name": pname,
                "category": cat,
                "current_stock": stock,
                "past_30d_demand": past_d,
                "forecasted_30d_demand": fcst_d,
                "demand_category": trend_cat,
                "stock_status": status,
                "action_recommendation": action,
                "explanation": explanation
            })

        rec_df = pd.DataFrame(recommendations)
        return rec_df

    def save_recommendations(
        self, 
        rec_df: pd.DataFrame, 
        output_path: str = "data/processed/inventory_recommendations.csv",
        export_path: str = "exports/inventory_recommendations.csv"
    ) -> pd.DataFrame:
        """Saves recommendation DataFrame to processed and export directories."""
        for path in [output_path, export_path]:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            rec_df.to_csv(path, index=False)
            print(f"Saved inventory recommendations to: {path} ({len(rec_df)} rows)")
        return rec_df
