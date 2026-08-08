# Power BI Dashboard Setup & User Guide

This directory contains complete step-by-step instructions for connecting Power BI Desktop to the Python/SQLite database or exported CSV analytical tables, building the Star Schema data model, creating DAX measures, and designing the 4-page interactive BI dashboard.

---

## 1. Data Connection Guide

### Option A: Database Connection (Recommended)
1. Open **Microsoft Power BI Desktop**.
2. Click **Get Data** → **SQLite ODBC** or **PostgreSQL / MySQL** database connector.
3. For SQLite: Select file path `data/ecommerce.db`.
4. Load tables:
   - `fact_sales`
   - `dim_date`
   - `dim_product`
   - `dim_customer`
   - `dim_region`

### Option B: Export CSV Connection (Portable)
1. Click **Get Data** → **Text/CSV**.
2. Import from the `exports/` folder:
   - `sales_summary.csv`
   - `product_summary.csv`
   - `customer_summary.csv`
   - `regional_summary.csv`
   - `forecast_results.csv`
   - `inventory_recommendations.csv`

---

## 2. Dashboard Layout (4 Pages)

### PAGE 1 — EXECUTIVE OVERVIEW
- **Top KPI Cards**: Total Revenue ($), Total Profit ($), Total Orders, Units Sold, Average Order Value (AOV), Profit Margin (%).
- **Visual 1**: Monthly Revenue & Profit Trend (Line & Clustered Column Chart).
- **Visual 2**: Revenue by Category (Horizontal Bar Chart).
- **Visual 3**: Revenue Share by Region (Donut / Pie Chart).
- **Slicers**: Date Range Slider, Category Dropdown, Region Multi-select.

### PAGE 2 — SALES & PRODUCT ANALYTICS
- **Visual 1**: Top 10 Best Selling Products by Revenue (Bar Chart).
- **Visual 2**: Bottom 10 Products by Revenue (Bar Chart).
- **Visual 3**: Revenue vs Profit Margin % Matrix by Product.
- **Visual 4**: Category Performance Grid with Drill-down to Product.
- **Slicers**: Category, Product SKU search, Date Range.

### PAGE 3 — CUSTOMER & REGIONAL ANALYTICS
- **Visual 1**: Top 10 High-Value Customers by Total Spend (Bar Chart).
- **Visual 2**: Customer Purchase Frequency Distribution (Histogram).
- **Visual 3**: Regional Revenue & Profit Margin Comparison (Grouped Bar Chart).
- **Visual 4**: Regional Growth MoM % Table.

### PAGE 4 — DEMAND FORECASTING & INVENTORY
- **Visual 1**: Historical Demand vs Forecasted Demand (Line Chart with Confidence Bands).
  - *Legend*: Actual Historical Demand (Solid Blue), Forecasted Demand (Dashed Green), Lower/Upper Bounds (Shaded Gray Area).
- **KPI Cards**: Forecast Model Used, MAE, RMSE, R², Total Forecasted 30D Demand.
- **Visual 2**: Stock Status Summary Cards (Stockout Alert Count, Overstock Count).
- **Visual 3**: Inventory Recommendation Table:
  - Columns: Product Name, Current Stock, Forecasted Demand, Trend Category, Stock Status, Action Recommendation, Explanation text.
- **Interactivity**: Slicer by Demand Category (HIGH DEMAND, INCREASING DEMAND, POTENTIAL STOCKOUT, POTENTIAL OVERSTOCK).
