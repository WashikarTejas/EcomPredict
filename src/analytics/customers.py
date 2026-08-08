"""
Customer Analytics Module.
Calculates Top high-value customers and overall customer purchasing metrics.
"""

import pandas as pd
from ..database.repository import DatabaseRepository

def get_top_customers(repo: DatabaseRepository = None, df: pd.DataFrame = None, limit: int = 10) -> pd.DataFrame:
    """Returns Top N customers by total spend."""
    if repo is not None:
        q = f"""
        SELECT 
            c.customer_id,
            COUNT(DISTINCT f.order_id) AS total_orders,
            SUM(f.quantity) AS total_items,
            ROUND(SUM(f.sales), 2) AS total_spend,
            ROUND(SUM(f.profit), 2) AS profit_generated
        FROM fact_sales f
        JOIN dim_customer c ON f.customer_key = c.customer_key
        GROUP BY c.customer_id
        ORDER BY total_spend DESC
        LIMIT {limit};
        """
        return repo.execute_query(q)
    elif df is not None:
        res = df.groupby("customer_id").agg(
            total_orders=("order_id", "nunique"),
            total_items=("quantity", "sum"),
            total_spend=("sales", "sum"),
            profit_generated=("profit", "sum")
        ).reset_index()
        res["total_spend"] = res["total_spend"].round(2)
        res["profit_generated"] = res["profit_generated"].round(2)
        return res.sort_values(by="total_spend", ascending=False).head(limit).reset_index(drop=True)
    else:
        raise ValueError("Either repository or DataFrame must be provided.")

def get_customer_summary(repo: DatabaseRepository = None, df: pd.DataFrame = None) -> pd.DataFrame:
    """Returns aggregated summary for all customers."""
    if repo is not None:
        q = """
        SELECT 
            c.customer_id,
            COUNT(DISTINCT f.order_id) AS total_orders,
            SUM(f.quantity) AS total_items,
            ROUND(SUM(f.sales), 2) AS total_spend,
            ROUND(SUM(f.profit), 2) AS total_profit
        FROM fact_sales f
        JOIN dim_customer c ON f.customer_key = c.customer_key
        GROUP BY c.customer_id
        ORDER BY total_spend DESC;
        """
        return repo.execute_query(q)
    elif df is not None:
        res = df.groupby("customer_id").agg(
            total_orders=("order_id", "nunique"),
            total_items=("quantity", "sum"),
            total_spend=("sales", "sum"),
            total_profit=("profit", "sum")
        ).reset_index()
        res["total_spend"] = res["total_spend"].round(2)
        res["total_profit"] = res["total_profit"].round(2)
        return res.sort_values(by="total_spend", ascending=False).reset_index(drop=True)
    else:
        raise ValueError("Either repository or DataFrame must be provided.")
