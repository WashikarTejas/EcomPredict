"""
Sales Analytics Module.
Calculates high-level revenue, profit, AOV, profit margin KPIs and monthly sales trends.
"""

import pandas as pd
from ..database.repository import DatabaseRepository

def get_overall_kpis(repo: DatabaseRepository = None, df: pd.DataFrame = None) -> dict:
    """Returns top-level business KPIs dictionary."""
    if repo is not None:
        q = """
        SELECT 
            ROUND(SUM(sales), 2) AS total_revenue,
            ROUND(SUM(profit), 2) AS total_profit,
            COUNT(DISTINCT order_id) AS total_orders,
            SUM(quantity) AS total_units_sold,
            ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS avg_order_value,
            ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_pct
        FROM fact_sales;
        """
        res = repo.execute_query(q).iloc[0].to_dict()
        return res
    elif df is not None:
        tot_rev = float(df["sales"].sum())
        tot_prof = float(df["profit"].sum())
        tot_orders = int(df["order_id"].nunique())
        tot_units = int(df["quantity"].sum())
        aov = round(tot_rev / tot_orders, 2) if tot_orders > 0 else 0.0
        pm = round((tot_prof / tot_rev) * 100.0, 2) if tot_rev > 0 else 0.0
        return {
            "total_revenue": round(tot_rev, 2),
            "total_profit": round(tot_prof, 2),
            "total_orders": tot_orders,
            "total_units_sold": tot_units,
            "avg_order_value": aov,
            "profit_margin_pct": pm
        }
    else:
        raise ValueError("Either repository or DataFrame must be provided.")

def get_monthly_sales_trend(repo: DatabaseRepository = None, df: pd.DataFrame = None) -> pd.DataFrame:
    """Returns Monthly Revenue and Profit breakdown."""
    if repo is not None:
        q = """
        SELECT 
            d.year,
            d.month,
            d.month_name,
            ROUND(SUM(f.sales), 2) AS monthly_revenue,
            ROUND(SUM(f.profit), 2) AS monthly_profit
        FROM fact_sales f
        JOIN dim_date d ON f.date_key = d.date_key
        GROUP BY d.year, d.month, d.month_name
        ORDER BY d.year, d.month;
        """
        return repo.execute_query(q)
    elif df is not None:
        df_copy = df.copy()
        df_copy["order_date"] = pd.to_datetime(df_copy["order_date"])
        df_copy["year"] = df_copy["order_date"].dt.year
        df_copy["month"] = df_copy["order_date"].dt.month
        df_copy["month_name"] = df_copy["order_date"].dt.strftime("%B")
        
        res = df_copy.groupby(["year", "month", "month_name"])[["sales", "profit"]].sum().reset_index()
        res.rename(columns={"sales": "monthly_revenue", "profit": "monthly_profit"}, inplace=True)
        res["monthly_revenue"] = res["monthly_revenue"].round(2)
        res["monthly_profit"] = res["monthly_profit"].round(2)
        return res.sort_values(by=["year", "month"]).reset_index(drop=True)
    else:
        raise ValueError("Either repository or DataFrame must be provided.")
