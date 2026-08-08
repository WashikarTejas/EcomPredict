"""
Dataset Generator for E-Commerce Sales Intelligence Platform.
Generates realistic multi-year transaction data with seasonal trends, product categories,
regions, discounts, costs, and intentional data quality edge cases for validation testing.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_ecommerce_data(
    num_orders=12000,
    start_date="2023-01-01",
    end_date="2025-12-31",
    seed=42,
    output_path="data/raw/raw_sales.csv",
    inventory_path="data/raw/simulated_inventory.csv"
):
    np.random.seed(seed)
    random.seed(seed)

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    total_days = (end_dt - start_dt).days

    # Categories and products definitions
    categories_products = {
        "Electronics": [
            ("Wireless Noise-Canceling Headphones", 149.99, 85.00),
            ("Ultra-Wide 4K Gaming Monitor", 499.99, 290.00),
            ("Ergonomic Mechanical Keyboard", 89.99, 45.00),
            ("High-Speed USB-C Hub 8-in-1", 45.00, 20.00),
            ("Portable Bluetooth Speaker", 65.00, 30.00),
            ("Smart Watch Fitness Tracker", 129.99, 70.00)
        ],
        "Office Supplies": [
            ("Premium Leather Journal", 24.99, 9.00),
            ("Gel Pen Set 12-Pack", 14.99, 4.50),
            ("Adjustable Laptop Stand", 39.99, 18.00),
            ("Shredder Cross-Cut Heavy Duty", 119.99, 65.00),
            ("Desk Organizer Mesh Drawer", 19.99, 8.00)
        ],
        "Furniture": [
            ("Ergonomic Mesh Office Chair", 229.99, 120.00),
            ("Electric Standing Desk 55 inch", 389.99, 210.00),
            ("Bookshelf 5-Tier Industrial", 149.99, 75.00),
            ("Executive High-Back Chair", 279.99, 145.00)
        ],
        "Apparel": [
            ("Waterproof Breathable Rain Jacket", 79.99, 35.00),
            ("Cotton Pullover Hoodie", 44.99, 18.00),
            ("Performance Running Shoes", 110.00, 50.00),
            ("Merino Wool Thermal Socks 3-Pack", 22.50, 8.00)
        ],
        "Home & Kitchen": [
            ("Stainless Steel French Press", 34.99, 14.00),
            ("Air Fryer XL 5.8 Quart", 99.99, 52.00),
            ("Cast Iron Dutch Oven 6 Qt", 79.99, 38.00),
            ("Robotic Vacuum Cleaner", 219.99, 115.00)
        ]
    }

    regions = ["North", "South", "East", "West", "Central"]
    customers = [f"CUST-{i:05d}" for i in range(1001, 1501)]

    records = []
    product_catalog = []

    # Flatten product catalog for inventory simulation
    prod_id_counter = 100
    p_info_map = {}
    for cat, prods in categories_products.items():
        for name, price, cost in prods:
            pid = f"PROD-{prod_id_counter}"
            prod_id_counter += 1
            p_info_map[name] = {
                "product_id": pid,
                "category": cat,
                "unit_price": price,
                "cost": cost
            }
            product_catalog.append((pid, name, cat, price, cost))

    all_names = list(p_info_map.keys())

    # Generate daily timestamps with seasonal demand weighting (Nov/Dec holiday peaks, Q3 boost)
    dates = []
    for _ in range(num_orders):
        day_offset = random.randint(0, total_days)
        d = start_dt + timedelta(days=day_offset)
        
        # Seasonality probability filter
        month = d.month
        prob = 0.7
        if month in [11, 12]:
            prob = 0.95  # Holiday sales boost
        elif month in [7, 8]:
            prob = 0.8   # Summer boost
        elif month in [1, 2]:
            prob = 0.55  # Post-holiday dip
            
        if random.random() < prob:
            dates.append(d)
        else:
            dates.append(start_dt + timedelta(days=random.randint(0, total_days)))

    dates.sort()

    for idx, order_dt in enumerate(dates):
        order_id = f"ORD-{idx + 10001}"
        cust_id = random.choice(customers)
        p_name = random.choice(all_names)
        info = p_info_map[p_name]
        pid = info["product_id"]
        cat = info["category"]
        reg = random.choice(regions)
        
        # Quantity distribution (mostly 1-4, occasionally higher for office supplies)
        qty = random.choices([1, 2, 3, 4, 5, 8, 10], weights=[50, 25, 12, 6, 4, 2, 1])[0]
        
        # Unit price variation (±5%)
        unit_price = round(info["unit_price"] * random.uniform(0.95, 1.05), 2)
        cost = round(info["cost"], 2)
        
        # Discount logic (0%, 5%, 10%, 15%, 20%, 30%)
        discount = random.choices([0.0, 0.05, 0.10, 0.15, 0.20, 0.30], weights=[50, 20, 15, 8, 5, 2])[0]
        
        records.append({
            "order_id": order_id,
            "order_date": order_dt.strftime("%Y-%m-%d"),
            "customer_id": cust_id,
            "product_id": pid,
            "product_name": p_name,
            "category": cat,
            "region": reg,
            "quantity": qty,
            "unit_price": unit_price,
            "discount": discount,
            "cost": cost
        })

    df = pd.DataFrame(records)

    # Inject deliberate data quality edge cases to test validation and cleaning pipelines
    # 1. Duplicate rows (~15 rows)
    dups = df.sample(n=15, random_state=42)
    df = pd.concat([df, dups], ignore_index=True)

    # 2. Missing values (~20 missing values in category/region/unit_price)
    missing_indices = np.random.choice(df.index, size=20, replace=False)
    for i in missing_indices[:7]:
        df.loc[i, "category"] = None
    for i in missing_indices[7:14]:
        df.loc[i, "region"] = None
    for i in missing_indices[14:]:
        df.loc[i, "unit_price"] = np.nan

    # 3. Invalid discounts (> 1.0 or < 0.0) (~5 rows)
    invalid_disc_idx = np.random.choice(df.index, size=5, replace=False)
    for i in invalid_disc_idx:
        df.loc[i, "discount"] = random.choice([1.25, -0.15, 2.0])

    # 4. Invalid quantities (<= 0) (~5 rows)
    invalid_qty_idx = np.random.choice(df.index, size=5, replace=False)
    for i in invalid_qty_idx:
        df.loc[i, "quantity"] = random.choice([0, -2])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated raw sales dataset: {output_path} ({len(df)} rows)")

    # Generate simulated inventory dataset
    inv_records = []
    for pid, name, cat, price, cost in product_catalog:
        # Stock between 50 and 800 units
        curr_stock = random.randint(50, 800)
        lead_days = random.randint(3, 14)
        reorder_point = random.randint(100, 300)
        inv_records.append({
            "product_id": pid,
            "product_name": name,
            "category": cat,
            "current_stock": curr_stock,
            "reorder_point": reorder_point,
            "lead_time_days": lead_days
        })
        
    inv_df = pd.DataFrame(inv_records)
    inv_df.to_csv(inventory_path, index=False)
    print(f"Generated simulated inventory dataset: {inventory_path} ({len(inv_df)} products)")

    return df, inv_df

if __name__ == "__main__":
    generate_ecommerce_data()
