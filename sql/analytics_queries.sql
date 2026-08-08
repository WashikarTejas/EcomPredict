-- ====================================================================
-- E-COMMERCE BUSINESS ANALYTICS QUERIES
-- Database Schema: Star Schema (fact_sales, dim_customer, dim_product, dim_region, dim_date)
-- ====================================================================

-- 1. Total Revenue
SELECT ROUND(SUM(sales), 2) AS total_revenue
FROM fact_sales;

-- 2. Total Profit
SELECT ROUND(SUM(profit), 2) AS total_profit
FROM fact_sales;

-- 3. Total Orders
SELECT COUNT(DISTINCT order_id) AS total_orders
FROM fact_sales;

-- 4. Total Units Sold
SELECT SUM(quantity) AS total_units_sold
FROM fact_sales;

-- 5. Average Order Value (AOV)
SELECT ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS avg_order_value
FROM fact_sales;

-- 6. Overall Profit Margin %
SELECT ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_pct
FROM fact_sales;

-- 7. Monthly Revenue Trend
SELECT 
    d.year,
    d.month,
    d.month_name,
    ROUND(SUM(f.sales), 2) AS monthly_revenue
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;

-- 8. Monthly Profit Trend
SELECT 
    d.year,
    d.month,
    d.month_name,
    ROUND(SUM(f.profit), 2) AS monthly_profit
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;

-- 9. Revenue Growth Rate Month-over-Month (using Window LAG)
WITH monthly_sales AS (
    SELECT 
        d.year,
        d.month,
        SUM(f.sales) AS revenue
    FROM fact_sales f
    JOIN dim_date d ON f.date_key = d.date_key
    GROUP BY d.year, d.month
)
SELECT 
    year,
    month,
    ROUND(revenue, 2) AS current_month_revenue,
    ROUND(LAG(revenue, 1) OVER (ORDER BY year, month), 2) AS prior_month_revenue,
    ROUND(
        ((revenue - LAG(revenue, 1) OVER (ORDER BY year, month)) / NULLIF(LAG(revenue, 1) OVER (ORDER BY year, month), 0)) * 100.0, 
        2
    ) AS mom_growth_pct
FROM monthly_sales;

-- 10. Revenue by Category
SELECT 
    p.category,
    ROUND(SUM(f.sales), 2) AS total_revenue
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category
ORDER BY total_revenue DESC;

-- 11. Profit by Category
SELECT 
    p.category,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND((SUM(f.profit) / SUM(f.sales)) * 100.0, 2) AS profit_margin_pct
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category
ORDER BY total_profit DESC;

-- 12. Top 10 Best Selling Products by Revenue
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
LIMIT 10;

-- 13. Bottom 10 Performing Products by Revenue
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
LIMIT 10;

-- 14. Top 10 High-Value Customers
SELECT 
    c.customer_id,
    COUNT(DISTINCT f.order_id) AS total_orders,
    SUM(f.quantity) AS total_items_bought,
    ROUND(SUM(f.sales), 2) AS total_spend,
    ROUND(SUM(f.profit), 2) AS profit_generated
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.customer_id
ORDER BY total_spend DESC
LIMIT 10;

-- 15. Revenue by Region
SELECT 
    r.region_name,
    ROUND(SUM(f.sales), 2) AS total_revenue,
    ROUND((SUM(f.sales) * 100.0 / (SELECT SUM(sales) FROM fact_sales)), 2) AS revenue_share_pct
FROM fact_sales f
JOIN dim_region r ON f.region_key = r.region_key
GROUP BY r.region_name
ORDER BY total_revenue DESC;

-- 16. Profit by Region
SELECT 
    r.region_name,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND((SUM(f.profit) / SUM(f.sales)) * 100.0, 2) AS profit_margin_pct
FROM fact_sales f
JOIN dim_region r ON f.region_key = r.region_key
GROUP BY r.region_name
ORDER BY total_profit DESC;

-- 17. Product Sales Growth (H2 vs H1 comparison)
WITH half_year_sales AS (
    SELECT 
        p.product_name,
        CASE WHEN d.month <= 6 THEN 'H1' ELSE 'H2' END AS half_period,
        SUM(f.sales) AS sales
    FROM fact_sales f
    JOIN dim_product p ON f.product_key = p.product_key
    JOIN dim_date d ON f.date_key = d.date_key
    WHERE d.year = (SELECT MAX(year) FROM dim_date)
    GROUP BY p.product_name, half_period
)
SELECT 
    product_name,
    ROUND(MAX(CASE WHEN half_period = 'H1' THEN sales ELSE 0 END), 2) AS h1_sales,
    ROUND(MAX(CASE WHEN half_period = 'H2' THEN sales ELSE 0 END), 2) AS h2_sales,
    ROUND(
        (MAX(CASE WHEN half_period = 'H2' THEN sales ELSE 0 END) - MAX(CASE WHEN half_period = 'H1' THEN sales ELSE 0 END)) /
        NULLIF(MAX(CASE WHEN half_period = 'H1' THEN sales ELSE 0 END), 0) * 100.0,
        2
    ) AS h2_vs_h1_growth_pct
FROM half_year_sales
GROUP BY product_name
ORDER BY h2_vs_h1_growth_pct DESC;

-- 18. Declining Products (Negative MoM Revenue Trend)
WITH recent_months AS (
    SELECT 
        p.product_id,
        p.product_name,
        d.year,
        d.month,
        SUM(f.sales) AS monthly_sales
    FROM fact_sales f
    JOIN dim_product p ON f.product_key = p.product_key
    JOIN dim_date d ON f.date_key = d.date_key
    GROUP BY p.product_id, p.product_name, d.year, d.month
),
monthly_lags AS (
    SELECT 
        product_id,
        product_name,
        year,
        month,
        monthly_sales,
        LAG(monthly_sales, 1) OVER (PARTITION BY product_id ORDER BY year, month) AS prev_month_sales
    FROM recent_months
)
SELECT 
    product_id,
    product_name,
    ROUND(monthly_sales, 2) AS current_sales,
    ROUND(prev_month_sales, 2) AS prev_sales,
    ROUND(((monthly_sales - prev_month_sales) / NULLIF(prev_month_sales, 0)) * 100.0, 2) AS decline_pct
FROM monthly_lags
WHERE prev_month_sales IS NOT NULL AND monthly_sales < prev_month_sales
ORDER BY decline_pct ASC
LIMIT 10;

-- 19. Low Margin / Low Profit Products
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    ROUND(SUM(f.sales), 2) AS total_sales,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND((SUM(f.profit) / SUM(f.sales)) * 100.0, 2) AS profit_margin_pct
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.product_id, p.product_name, p.category
HAVING total_sales > 1000
ORDER BY profit_margin_pct ASC
LIMIT 10;

-- 20. High Volume Products
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    SUM(f.quantity) AS total_quantity_sold,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.sales), 2) AS total_revenue
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_quantity_sold DESC
LIMIT 10;
