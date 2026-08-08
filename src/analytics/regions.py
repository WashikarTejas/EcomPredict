"""
Regional Analytics Module.
Calculates revenue, profit, revenue share %, and profit margin % by region.
"""

import pandas as pd
from ..database.repository import DatabaseRepository

def get_regional_performance(repo: DatabaseRepository = None, df: pd.DataFrame = None) -> pd.DataFrame:
    """Returns regional performance summary."""
    if repo is not None:
        q = """
        SELECT 
            r.region_name AS region,
            COUNT(DISTINCT f.order_id) AS total_orders,
            SUM(f.quantity) AS total_units,
            ROUND(SUM(f.sales), 2) AS total_revenue,
            ROUND(SUM(f.profit), 2) AS total_profit,
            ROUND((SUM(f.profit) / SUM(f.sales)) * 100.0, 2) AS profit_margin_pct
        FROM fact_sales f
        JOIN dim_region r ON f.region_key = r.region_key
        GROUP BY r.region_name
        ORDER BY total_revenue DESC;
        """
        res = repo.execute_query(q)
        tot_rev = res["total_revenue"].sum()
        res["revenue_share_pct"] = ((res["total_revenue"] / tot_rev) * 100.0).round(2) if tot_rev > 0 else 0.0
        return res
    elif df is not None:
        res = df.groupby("region").agg(
            total_orders=("order_id", "nunique"),
            total_units=("quantity", "sum"),
            total_revenue=("sales", "sum"),
            total_profit=("profit", "sum")
        ).reset_index()
        res["total_revenue"] = res["total_revenue"].round(2)
        res["total_profit"] = res["total_profit"].round(2)
        tot_rev = res["total_revenue"].sum()
        res["revenue_share_pct"] = ((res["total_revenue"] / tot_rev) * 100.0).round(2) if tot_rev > 0 else 0.0
        res["profit_margin_pct"] = ((res["total_profit"] / res["total_revenue"]) * 100.0).round(2)
        return res.sort_values(by="total_revenue", ascending=False).reset_index(drop=True)
    else:
        raise ValueError("Either repository or DataFrame must be provided.")
