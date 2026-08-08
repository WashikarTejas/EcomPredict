# Power BI DAX Measures Reference Guide

This document specifies all explicit DAX (Data Analysis Expressions) measures created for the **E-Commerce Sales Intelligence & Demand Forecasting** dashboard.

---

## 1. Core Financial & Sales Measures

### Total Revenue
```dax
Total Revenue = 
SUM(fact_sales[sales])
```

### Total Profit
```dax
Total Profit = 
SUM(fact_sales[profit])
```

### Total Orders
```dax
Total Orders = 
DISTINCTCOUNT(fact_sales[order_id])
```

### Total Units Sold
```dax
Total Units Sold = 
SUM(fact_sales[quantity])
```

### Average Order Value (AOV)
```dax
Average Order Value = 
DIVIDE([Total Revenue], [Total Orders], 0.0)
```

### Profit Margin %
```dax
Profit Margin % = 
DIVIDE([Total Profit], [Total Revenue], 0.0) * 100
```

### Average Selling Price (ASP)
```dax
Average Selling Price = 
DIVIDE([Total Revenue], [Total Units Sold], 0.0)
```

---

## 2. Growth & Time Intelligence Measures

### Prior Year Revenue
```dax
Prior Year Revenue = 
CALCULATE(
    [Total Revenue],
    SAMEPERIODLASTYEAR(dim_date[full_date])
)
```

### YoY Revenue Growth %
```dax
YoY Revenue Growth % = 
VAR CurrentRevenue = [Total Revenue]
VAR PYRevenue = [Prior Year Revenue]
RETURN
DIVIDE(CurrentRevenue - PYRevenue, PYRevenue, 0.0) * 100
```

### Prior Month Revenue
```dax
Prior Month Revenue = 
CALCULATE(
    [Total Revenue],
    DATEADD(dim_date[full_date], -1, MONTH)
)
```

### MoM Revenue Growth %
```dax
MoM Revenue Growth % = 
VAR CurrentRevenue = [Total Revenue]
VAR PMRevenue = [Prior Month Revenue]
RETURN
DIVIDE(CurrentRevenue - PMRevenue, PMRevenue, 0.0) * 100
```

---

## 3. Demand Forecasting & Inventory Measures

### Historical Demand
```dax
Historical Demand = 
CALCULATE(
    SUM(forecast_results[actual_demand]),
    forecast_results[is_forecast] = 0
)
```

### Forecasted Demand
```dax
Forecasted Demand = 
CALCULATE(
    SUM(forecast_results[predicted_demand]),
    forecast_results[is_forecast] = 1
)
```

### Total Projected Demand (30D)
```dax
Projected 30D Demand = 
SUM(inventory_recommendations[forecasted_30d_demand])
```

### Total Current Stock
```dax
Total Current Stock = 
SUM(inventory_recommendations[current_stock])
```

### Stockout Risk Count
```dax
Stockout Risk Count = 
CALCULATE(
    COUNTROWS(inventory_recommendations),
    inventory_recommendations[stock_status] = "POTENTIAL STOCKOUT"
)
```

### Overstock Risk Count
```dax
Overstock Risk Count = 
CALCULATE(
    COUNTROWS(inventory_recommendations),
    inventory_recommendations[stock_status] = "POTENTIAL OVERSTOCK"
)
```
