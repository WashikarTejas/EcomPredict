"""
Database Seeding Module for E-Commerce Sales Intelligence.
Populates Star Schema tables (dim_customer, dim_product, dim_region, dim_date, fact_sales) from cleaned DataFrame.
"""

import pandas as pd
from sqlalchemy.orm import Session
from .connection import get_db_engine, get_db_session
from .models import Base, DimCustomer, DimProduct, DimRegion, DimDate, FactSales

def seed_database(cleaned_df: pd.DataFrame, db_path: str = "data/ecommerce.db"):
    """
    Creates DB tables and seeds dimension & fact tables using bulk inserts.
    """
    engine = get_db_engine(db_path)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    session = get_db_session(db_path)
    try:
        df = cleaned_df.copy()
        df["order_date"] = pd.to_datetime(df["order_date"])

        # 1. Seed DimCustomer
        unique_customers = df["customer_id"].unique()
        cust_map = {}
        for cid in unique_customers:
            cust_obj = DimCustomer(customer_id=cid)
            session.add(cust_obj)
        session.flush()
        
        all_custs = session.query(DimCustomer).all()
        cust_map = {c.customer_id: c.customer_key for c in all_custs}

        # 2. Seed DimProduct
        prod_df = df[["product_id", "product_name", "category", "cost"]].drop_duplicates(subset=["product_id"])
        prod_map = {}
        for _, row in prod_df.iterrows():
            p_obj = DimProduct(
                product_id=row["product_id"],
                product_name=row["product_name"],
                category=row["category"],
                cost=float(row["cost"])
            )
            session.add(p_obj)
        session.flush()
        
        all_prods = session.query(DimProduct).all()
        prod_map = {p.product_id: p.product_key for p in all_prods}

        # 3. Seed DimRegion
        unique_regions = df["region"].unique()
        reg_map = {}
        for rname in unique_regions:
            r_obj = DimRegion(region_name=rname)
            session.add(r_obj)
        session.flush()
        
        all_regs = session.query(DimRegion).all()
        reg_map = {r.region_name: r.region_key for r in all_regs}

        # 4. Seed DimDate
        min_date = df["order_date"].min()
        max_date = df["order_date"].max()
        date_range = pd.date_range(start=min_date, end=max_date, freq="D")
        
        for dt in date_range:
            d_key = int(dt.strftime("%Y%m%d"))
            d_obj = DimDate(
                date_key=d_key,
                full_date=dt.date(),
                year=dt.year,
                quarter=dt.quarter,
                month=dt.month,
                month_name=dt.strftime("%B"),
                week_of_year=int(dt.isocalendar().week),
                day_of_week=dt.dayofweek,
                day_name=dt.strftime("%A")
            )
            session.add(d_obj)
        session.flush()

        # 5. Seed FactSales
        fact_records = []
        for _, row in df.iterrows():
            d_key = int(row["order_date"].strftime("%Y%m%d"))
            fact = FactSales(
                order_id=row["order_id"],
                date_key=d_key,
                customer_key=cust_map[row["customer_id"]],
                product_key=prod_map[row["product_id"]],
                region_key=reg_map[row["region"]],
                quantity=int(row["quantity"]),
                unit_price=float(row["unit_price"]),
                discount=float(row["discount"]),
                cost=float(row["cost"]),
                sales=float(row["sales"]),
                profit=float(row["profit"]),
                profit_margin=float(row["profit_margin"])
            )
            fact_records.append(fact)
            
        session.bulk_save_objects(fact_records)
        session.commit()
        print(f"Database successfully seeded at {db_path} with {len(fact_records)} fact records.")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
