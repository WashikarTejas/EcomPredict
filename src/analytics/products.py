"""
Product Analytics Module.
Calculates Top 10 products, Bottom 10 products, and category-level metrics.
"""

import pandas as pd
from ..database.repository import DatabaseRepository

def get_top_products(repo: DatabaseRepository = None, df: pd.DataFrame = None, limit: int = 10) -> pd.DataFrame:
    """Returns Top N products by total revenue."""
    if repo is not None:
        q = f"""
        SELECT 
            p.product_id,
            p.product_name,
            p.category,
            SUM(f.quantity) AS total_units,
            ROUND(SUM(f.sales), 2) AS total_revenue,
            ROUND(SUM(f.profit), 2) AS total_profit
        FROM fact_sales f
        JOIN dim_product p ON f.product_key = p.product_key
        GROUP BY p.product_id, p.product_name, p.category
        ORDER BY total_revenue DESC
        LIMIT {limit};
        """
        return repo.execute_query(q)
    elif df is not None:
        res = df.groupby(["product_id", "product_name", "category"]).agg(
            total_units=("quantity", "sum"),
            total_revenue=("sales", "sum"),
            total_profit=("profit", "sum")
        ).reset_index()
        res["total_revenue"] = res["total_revenue"].round(2)
        res["total_profit"] = res["total_profit"].round(2)
        return res.sort_values(by="total_revenue", ascending=False).head(limit).reset_index(drop=True)
    else:
        raise ValueError("Either repository or DataFrame must be provided.")

def get_bottom_products(repo: DatabaseRepository = None, df: pd.DataFrame = None, limit: int = 10) -> pd.DataFrame:
    """Returns Bottom N products by total revenue."""
    if repo is not None:
        q = f"""
        SELECT 
            p.product_id,
            p.product_name,
            p.category,
            SUM(f.quantity) AS total_units,
            ROUND(SUM(f.sales), 2) AS total_revenue,
            ROUND(SUM(f.profit), 2) AS total_profit
        FROM fact_sales f
        JOIN dim_product p ON f.product_key = p.product_key
        GROUP BY p.product_id, p.product_name, p.category
        ORDER BY total_revenue ASC
        LIMIT {limit};
        """
        return repo.execute_query(q)
    elif df is not None:
        res = df.groupby(["product_id", "product_name", "category"]).agg(
            total_units=("quantity", "sum"),
            total_revenue=("sales", "sum"),
            total_profit=("profit", "sum")
        ).reset_index()
        res["total_revenue"] = res["total_revenue"].round(2)
        res["total_profit"] = res["total_profit"].round(2)
        return res.sort_values(by="total_revenue", ascending=True).head(limit).reset_index(drop=True)
    else:
        raise ValueError("Either repository or DataFrame must be provided.")

def get_category_performance(repo: DatabaseRepository = None, df: pd.DataFrame = None) -> pd.DataFrame:
    """Returns revenue, profit, units, and margin % aggregated by category."""
    if repo is not None:
        q = """
        SELECT 
            p.category,
            SUM(f.quantity) AS total_units,
            ROUND(SUM(f.sales), 2) AS total_revenue,
            ROUND(SUM(f.profit), 2) AS total_profit,
            ROUND((SUM(f.profit) / SUM(f.sales)) * 100.0, 2) AS profit_margin_pct
        FROM fact_sales f
        JOIN dim_product p ON f.product_key = p.product_key
        GROUP BY p.category
        ORDER BY total_revenue DESC;
        """
        return repo.execute_query(q)
    elif df is not None:
        res = df.groupby("category").agg(
            total_units=("quantity", "sum"),
            total_revenue=("sales", "sum"),
            total_profit=("profit", "sum")
        ).reset_index()
        res["total_revenue"] = res["total_revenue"].round(2)
        res["total_profit"] = res["total_profit"].round(2)
        res["profit_margin_pct"] = ((res["total_profit"] / res["total_revenue"]) * 100.0).round(2)
        return res.sort_values(by="total_revenue", ascending=False).reset_index(drop=True)
    else:
        raise ValueError("Either repository or DataFrame must be provided.")
