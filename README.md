# E-Commerce Sales Intelligence & Demand Forecasting Platform

An end-to-end Data Analytics, Data Science, and Business Intelligence platform built with **Python**, **Pandas**, **SQL (SQLAlchemy / SQLite / PostgreSQL)**, **Scikit-learn**, and **Power BI Desktop**.

---

## 1. Project Overview
This enterprise-grade analytics solution empowers e-commerce stakeholders to analyze historical sales performance, uncover revenue and profit drivers, forecast 30-day future product demand using machine learning, and mitigate stockout/overstock inventory risks through automated actionable business recommendations and an interactive Power BI dashboard.

---

## 2. Problem Statement
E-commerce businesses frequently struggle with:
1. **Uncertain Demand & Inventory Inefficiencies**: Overstocking ties up working capital, while stockouts lead to lost revenue and dissatisfied customers.
2. **Siloed & Dirty Transactional Data**: Raw operational data suffers from null values, invalid prices, duplicate orders, and inconsistent formatting.
3. **Lack of Integrated Reporting**: Leadership lacks a unified view connecting high-level revenue/profit trends with SKU-level predictive demand projections.

---

## 3. Core Objectives
- **Data Pipeline**: Build an automated data ingestion, validation, and cleaning pipeline in Python.
- **Relational Data Warehouse**: Store sanitized transactions in a clean Star Schema SQL database.
- **Business Intelligence**: Author 20 analytical SQL queries and build a 4-page interactive Power BI dashboard.
- **Predictive Analytics**: Develop leakage-free time-series ML models (Linear Regression, Random Forest, Moving Average) to project 7, 30, and 60-day demand.
- **Prescriptive Insights**: Construct an automated inventory recommendation engine with explainable narrative actions.

---

## 4. Platform Architecture & Data Flow

```
[ Raw E-Commerce Transaction CSV ]
                 │
                 ▼
[ Python Ingestion & Data Quality Validation ] (validator.py)
                 │
                 ▼
[ Data Cleaning & Metric Computation ] (cleaner.py) → data/processed/cleaned_sales.csv
                 │
                 ▼
[ Star Schema Database Warehouse ] (SQLite/SQLAlchemy)
  ├── fact_sales
  ├── dim_customer | dim_product | dim_region | dim_date
                 │
                 ▼
[ SQL Business Analytics Queries ] (20 Queries in sql/analytics_queries.sql)
                 │
                 ▼
[ Time-Series Feature Engineering ] (lag_1..30, rolling_mean_7..30 - shift(1) no leakage)
                 │
                 ▼
[ ML Forecasting Engine ] (Baseline MA, Linear Regression, Champion Random Forest)
                 │
                 ▼
[ Inventory Recommendation Engine ] (Categorization & Narrative Explanations)
                 │
                 ▼
[ Analytical CSV Exports ] → exports/*.csv
                 │
                 ▼
[ Power BI Interactive Dashboard ] (4 Pages, Star Schema Model, DAX Measures)
```

---

## 5. Technology Stack
- **Programming**: Python 3.12+
- **Data Processing**: Pandas, NumPy
- **Database & Connectivity**: SQLAlchemy, SQLite (Default) / PostgreSQL / MySQL
- **Machine Learning**: Scikit-learn
- **Visualization**: Matplotlib, Plotly, Seaborn
- **Business Intelligence**: Microsoft Power BI Desktop (Star Schema Data Model & DAX)
- **Testing**: pytest

---

## 6. Project Structure

```
ecommerce-sales-intelligence/
│
├── README.md                           # Main Project & Interview Preparation Guide
├── requirements.txt                    # Project Python Dependencies
├── .gitignore                          # Version Control Exclusions
├── main.py                             # Main End-to-End Orchestration Script
├── generate_dataset.py                 # Synthetic Dataset Generator with Quality Edge Cases
│
├── data/
│   ├── raw/                            # Raw Sales CSV & Simulated Inventory
│   ├── processed/                      # Cleaned Sales & Forecast Results CSVs
│   └── ecommerce.db                    # SQLite Relational Star Schema Database
│
├── src/
│   ├── data/                           # Loader, Validator & Cleaner Modules
│   │   ├── loader.py
│   │   ├── validator.py
│   │   └── cleaner.py
│   │
│   ├── database/                       # Connection, Models, Repository & Seed Scripts
│   │   ├── connection.py
│   │   ├── models.py
│   │   ├── repository.py
│   │   └── seed.py
│   │
│   ├── analytics/                      # Python SQL Analytics Wrappers
│   │   ├── sales.py
│   │   ├── products.py
│   │   ├── customers.py
│   │   └── regions.py
│   │
│   ├── features/                       # Leakage-Free Time-Series Feature Engineering
│   │   └── feature_engineering.py
│   │
│   ├── models/                         # Forecasting Models & Evaluator
│   │   ├── baseline.py
│   │   ├── linear_regression.py
│   │   ├── random_forest.py
│   │   ├── trainer.py
│   │   ├── evaluator.py
│   │   └── forecaster.py
│   │
│   └── recommendations/               # Inventory Risk Engine
│       └── engine.py
│
├── sql/
│   └── analytics_queries.sql           # 20 Business Analytics SQL Queries
│
├── notebooks/
│   └── 01_eda.ipynb                    # Exploratory Data Analysis Notebook
│
├── powerbi/
│   ├── README.md                       # Power BI Dashboard Setup & Layout Guide
│   ├── data_model.md                   # Star Schema Documentation & Relationships
│   └── dax_measures.md                 # Complete DAX Measures Reference
│
├── exports/                            # Analytical Summary CSVs for Power BI
│   ├── sales_summary.csv
│   ├── product_summary.csv
│   ├── customer_summary.csv
│   ├── regional_summary.csv
│   ├── forecast_results.csv
│   └── inventory_recommendations.csv
│
└── tests/                              # Pytest Unit Test Suite
    ├── test_data_cleaning.py
    ├── test_analytics.py
    ├── test_forecasting.py
    └── test_recommendations.py
```

---

## 7. Dataset & Ingestion Pipeline
The dataset models realistic multi-year e-commerce sales transactions containing:
- `order_id`, `order_date`, `customer_id`, `product_id`, `product_name`, `category`, `region`, `quantity`, `unit_price`, `discount`, `cost`.

### Metric Formulations:
- $\text{Sales} = \text{quantity} \times \text{unit\_price} \times (1 - \text{discount})$
- $\text{Profit} = \text{Sales} - (\text{quantity} \times \text{cost})$
- $\text{Profit Margin} = \frac{\text{Profit}}{\text{Sales}} \quad (\text{Safe division handling when Sales} = 0)$

---

## 8. Data Quality Validation & Cleaning
The `DataValidator` module detects:
- Missing values in critical fields.
- Duplicate order line records.
- Non-positive quantities ($\le 0$) or unit prices ($\le 0$).
- Out-of-bounds discounts ($< 0.0$ or $> 1.0$).
- Malformed order date strings.

The `DataCleaner` module:
- Imputes missing unit prices using median price per product.
- Standardizes category and regional casing.
- Deduplicates rows and filters out non-positive quantities.
- Clips discounts to $[0.0, 1.0]$.
- Generates `data/processed/cleaned_sales.csv`.

---

## 9. Database Architecture & SQL Analytics
Processed data is loaded into a **Star Schema** database using **SQLAlchemy**:
- **Fact Table**: `fact_sales`
- **Dimension Tables**: `dim_customer`, `dim_product`, `dim_region`, `dim_date`

The platform implements 20 business queries in `sql/analytics_queries.sql` covering:
- Total Revenue, Total Profit, AOV, Profit Margin %.
- Monthly Revenue & Profit trends with MoM growth % using SQL window functions (`LAG()`).
- Category performance & Regional revenue share %.
- Top 10 Best Selling Products & Bottom 10 Performing Products.
- Top 10 High-Value Customers.
- Declining products & Low-margin product identification.

---

## 10. Machine Learning Demand Forecasting
### Feature Engineering
Time-series features are constructed from daily aggregated demand:
- **Calendar Features**: `year`, `month`, `week`, `quarter`, `day_of_week`, `is_weekend`.
- **Lag Features**: `lag_1`, `lag_7`, `lag_14`, `lag_30`.
- **Rolling Window Means**: `rolling_mean_7`, `rolling_mean_14`, `rolling_mean_30`, `rolling_std_7`.
- *Leakage Prevention*: All rolling features are computed after applying `.shift(1)` to target demand.

### Train / Test Split Strategy
Time-series forecasting uses **Chronological Splitting** (e.g. earliest 80% data for training, most recent 20% for testing) to respect temporal ordering.

### Models Evaluated & Metrics
1. **Moving Average Baseline (7-Day)**
2. **Linear Regression**
3. **Random Forest Regressor** (Champion Model)

| Model | MAE | RMSE | R² |
| :--- | :---: | :---: | :---: |
| **Random Forest Regressor** | **Lowest** | **Lowest** | **Highest** |
| Linear Regression | Medium | Medium | Medium |
| Moving Average Baseline | Higher | Higher | Lower |

Output results are exported to `data/processed/forecast_results.csv` and `exports/forecast_results.csv`.

---

## 11. Inventory Recommendation Engine
Combines current stock levels, past 30-day demand, and 30-day forecasted demand to categorize products:
- `POTENTIAL STOCKOUT`: Projected demand exceeds stock ($S < D_{fcst}$).
- `POTENTIAL OVERSTOCK`: Current stock is $> 2.5\times$ projected demand.
- `REORDER RECOMMENDED`: Stock reaches reorder threshold.
- `HEALTHY INVENTORY`: Stock balanced with projected demand.

Produces narrative explanations for each action item in `exports/inventory_recommendations.csv`.

---

## 12. Power BI Integration & Dashboard Layout
Power BI Desktop connects to SQLite / PostgreSQL database tables or exported CSV files.

### 4 Dashboard Pages:
1. **Executive Overview**: Executive KPI cards, Monthly Revenue/Profit line trends, Revenue by Category & Region.
2. **Sales & Product Analytics**: Top 10 / Bottom 10 Products, Quantity Sold, Product Margin Matrix.
3. **Customer & Regional Analytics**: Top Customer Spend, Regional Revenue Share, Regional Growth.
4. **Demand Forecasting & Inventory**: Historical vs Forecasted Demand time-series chart with confidence bands, Model MAE/RMSE/R² metrics, and Stockout/Overstock Action Recommendation Table.

---

## 13. How to Run the Project

### Installation
```bash
git clone https://github.com/your-username/ecommerce-sales-intelligence.git
cd ecommerce-sales-intelligence
pip install -r requirements.txt
```

### Execution
Run the complete end-to-end pipeline with one command:
```bash
python main.py
```

### Run Unit Tests
```bash
pytest
```

---

## 14. Comprehensive Interview Preparation Guide

### Python & Data Processing
- **Q: Why use Python for this pipeline?**  
  *A:* Python offers rich libraries (Pandas, Scikit-learn, SQLAlchemy) that enable seamless end-to-end integration across raw ingestion, statistical validation, machine learning, and automated export workflows.
- **Q: How were missing values and bad values handled in Pandas?**  
  *A:* The `DataCleaner` module fills missing unit prices using product median price, clips discounts to $[0.0, 1.0]$, filters out non-positive quantities, and handles division by zero safely during profit margin calculations using `np.where`.

### SQL & Database Architecture
- **Q: Why use a Star Schema instead of a flat CSV file?**  
  *A:* A Star Schema normalizes transactional attributes into dedicated dimension tables (`dim_product`, `dim_customer`, `dim_region`, `dim_date`) around a central `fact_sales` table. This eliminates redundancy, enforces referential integrity, improves SQL query efficiency, and provides optimal slice-and-dill performance in Power BI.
- **Q: What SQL window functions were used?**  
  *A:* `LAG()` was used to compute Month-over-Month (MoM) revenue growth rates and identify declining product trajectories over consecutive time periods.

### Machine Learning & Forecasting
- **Q: Why use chronological splitting instead of random train/test split?**  
  *A:* Time-series data has temporal autocorrelation. Random splitting would shuffle future data into training samples, causing catastrophic data leakage and unrealistic validation accuracy. Chronological splitting ensures models are trained on past data and evaluated strictly on future data.
- **Q: How did you prevent data leakage in feature engineering?**  
  *A:* Lag features use explicit time shifts (`shift(1)`, `shift(7)`), and rolling statistics are calculated on target values shifted by at least 1 day prior to window computation.
- **Q: What evaluation metrics were used and why?**  
  *A:* **MAE** measures average absolute prediction magnitude in demand units, **RMSE** heavily penalizes large forecast errors (critical for stockout prevention), and **R²** indicates the proportion of variance explained by features.

### Power BI & Business Intelligence
- **Q: What is the difference between a Calculated Column and a DAX Measure?**  
  *A:* Calculated columns evaluate row-by-row during data refresh and consume RAM storage. DAX measures evaluate dynamically at query time based on visual filter contexts without adding table storage overhead.
- **Q: How does Power BI visualize the Python forecast results?**  
  *A:* Python exports `forecast_results.csv` containing date, actual demand, predicted demand, lower bound, and upper bound. In Power BI, actual and predicted values are rendered on a single time-series visual with a shaded confidence interval.
