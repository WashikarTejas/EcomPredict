"""
Generates an interactive, high-aesthetic HTML/JS Business Intelligence Dashboard (dashboard.html)
reading real data from processed CSVs and SQLite database.
"""

import json
import pandas as pd

def generate_interactive_dashboard():
    # Load Data
    cleaned_df = pd.read_csv("data/processed/cleaned_sales.csv")
    forecast_df = pd.read_csv("exports/forecast_results.csv")
    rec_df = pd.read_csv("exports/inventory_recommendations.csv")

    # Aggregate Monthly
    cleaned_df["order_date"] = pd.to_datetime(cleaned_df["order_date"])
    cleaned_df["year_month"] = cleaned_df["order_date"].dt.to_period("M").astype(str)
    
    monthly = cleaned_df.groupby("year_month")[["sales", "profit"]].sum().reset_index()
    monthly_labels = monthly["year_month"].tolist()
    monthly_sales = monthly["sales"].round(2).tolist()
    monthly_profit = monthly["profit"].round(2).tolist()

    # Aggregate Category
    cat_df = cleaned_df.groupby("category")[["sales", "profit"]].sum().reset_index()
    cat_labels = cat_df["category"].tolist()
    cat_sales = cat_df["sales"].round(2).tolist()
    cat_profit = cat_df["profit"].round(2).tolist()

    # Aggregate Region
    reg_df = cleaned_df.groupby("region")[["sales"]].sum().reset_index()
    reg_labels = reg_df["region"].tolist()
    reg_sales = reg_df["sales"].round(2).tolist()

    # Top 10 Products
    top_p = cleaned_df.groupby("product_name")[["sales", "profit"]].sum().reset_index().sort_values(by="sales", ascending=False).head(10)
    top_p_labels = top_p["product_name"].tolist()
    top_p_sales = top_p["sales"].round(2).tolist()

    # Forecast Data
    forecast_df["order_date"] = pd.to_datetime(forecast_df["order_date"])
    recent_hist = forecast_df[forecast_df["is_forecast"] == 0].tail(60)
    future_fcst = forecast_df[forecast_df["is_forecast"] == 1]
    
    fcst_dates = recent_hist["order_date"].dt.strftime("%Y-%m-%d").tolist() + future_fcst["order_date"].dt.strftime("%Y-%m-%d").tolist()
    actual_demand = recent_hist["actual_demand"].tolist() + [None]*len(future_fcst)
    pred_demand = [None]*len(recent_hist) + future_fcst["predicted_demand"].tolist()
    lower_bound = [None]*len(recent_hist) + future_fcst["lower_bound"].tolist()
    upper_bound = [None]*len(recent_hist) + future_fcst["upper_bound"].tolist()

    # KPIs
    tot_rev = float(cleaned_df["sales"].sum())
    tot_prof = float(cleaned_df["profit"].sum())
    tot_orders = int(cleaned_df["order_id"].nunique())
    tot_units = int(cleaned_df["quantity"].sum())
    aov = float(tot_rev / tot_orders)
    margin = float(tot_prof / tot_rev * 100)

    # Inventory Table Data
    recs = rec_df.to_dict(orient="records")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Commerce Sales Intelligence & Demand Forecasting Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-dark: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.7);
            --border-color: rgba(255, 255, 255, 0.1);
            --accent-blue: #38bdf8;
            --accent-green: #34d399;
            --accent-purple: #c084fc;
            --accent-amber: #fbbf24;
            --accent-rose: #f43f5e;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Outfit', sans-serif; }}
        body {{ background: var(--bg-dark); color: var(--text-main); min-height: 100vh; padding: 2rem; }}

        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem; }}
        .header h1 {{ font-size: 1.8rem; font-weight: 700; background: linear-gradient(90deg, var(--accent-blue), var(--accent-purple)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .header p {{ color: var(--text-muted); font-size: 0.95rem; margin-top: 0.25rem; }}

        .tabs {{ display: flex; gap: 0.75rem; margin-bottom: 1.5rem; }}
        .tab-btn {{ background: rgba(255, 255, 255, 0.05); border: 1px solid var(--border-color); color: var(--text-muted); padding: 0.6rem 1.25rem; border-radius: 8px; font-weight: 500; cursor: pointer; transition: all 0.3s ease; }}
        .tab-btn:hover, .tab-btn.active {{ background: var(--accent-blue); color: #0f172a; font-weight: 600; border-color: var(--accent-blue); box-shadow: 0 0 15px rgba(56, 189, 248, 0.3); }}

        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}

        .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1.25rem; margin-bottom: 2rem; }}
        .kpi-card {{ background: var(--card-bg); backdrop-filter: blur(12px); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.25rem; transition: transform 0.2s ease; }}
        .kpi-card:hover {{ transform: translateY(-3px); border-color: var(--accent-blue); }}
        .kpi-title {{ color: var(--text-muted); font-size: 0.85rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }}
        .kpi-value {{ font-size: 1.6rem; font-weight: 700; margin-top: 0.5rem; color: var(--text-main); }}

        .chart-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.5rem; margin-bottom: 2rem; }}
        .full-width {{ grid-column: span 2; }}
        .chart-card {{ background: var(--card-bg); backdrop-filter: blur(12px); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.5rem; }}
        .chart-card h3 {{ font-size: 1.1rem; margin-bottom: 1rem; color: var(--accent-blue); }}

        table {{ width: 100%; border-collapse: collapse; margin-top: 1rem; text-align: left; }}
        th, td {{ padding: 0.75rem 1rem; border-bottom: 1px solid var(--border-color); font-size: 0.9rem; }}
        th {{ color: var(--accent-blue); font-weight: 600; text-transform: uppercase; font-size: 0.8rem; background: rgba(255, 255, 255, 0.02); }}
        tr:hover {{ background: rgba(255, 255, 255, 0.03); }}

        .badge {{ padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; display: inline-block; }}
        .badge-stockout {{ background: rgba(244, 63, 94, 0.2); color: var(--accent-rose); border: 1px solid var(--accent-rose); }}
        .badge-overstock {{ background: rgba(251, 191, 36, 0.2); color: var(--accent-amber); border: 1px solid var(--accent-amber); }}
        .badge-reorder {{ background: rgba(192, 132, 252, 0.2); color: var(--accent-purple); border: 1px solid var(--accent-purple); }}
        .badge-healthy {{ background: rgba(52, 211, 153, 0.2); color: var(--accent-green); border: 1px solid var(--accent-green); }}

        @media (max-width: 900px) {{ .chart-grid {{ grid-template-columns: 1fr; }} .full-width {{ grid-column: span 1; }} }}
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h1>E-Commerce Sales Intelligence & Demand Forecasting Dashboard</h1>
            <p>Live Business Analytics, Star Schema SQL Insights & Machine Learning Demand Predictions</p>
        </div>
    </div>

    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('exec')">Executive Overview</button>
        <button class="tab-btn" onclick="switchTab('products')">Sales & Products</button>
        <button class="tab-btn" onclick="switchTab('forecast')">Demand Forecasting & Inventory</button>
    </div>

    <!-- TAB 1: EXECUTIVE OVERVIEW -->
    <div id="tab-exec" class="tab-content active">
        <div class="kpi-grid">
            <div class="kpi-card"><div class="kpi-title">Total Revenue</div><div class="kpi-value" style="color:var(--accent-blue);">${tot_rev:,.2f}</div></div>
            <div class="kpi-card"><div class="kpi-title">Total Profit</div><div class="kpi-value" style="color:var(--accent-green);">${tot_prof:,.2f}</div></div>
            <div class="kpi-card"><div class="kpi-title">Profit Margin</div><div class="kpi-value" style="color:var(--accent-purple);">{margin:.2f}%</div></div>
            <div class="kpi-card"><div class="kpi-title">Total Orders</div><div class="kpi-value">{tot_orders:,}</div></div>
            <div class="kpi-card"><div class="kpi-title">Units Sold</div><div class="kpi-value">{tot_units:,}</div></div>
            <div class="kpi-card"><div class="kpi-title">Avg Order Value</div><div class="kpi-value">${aov:.2f}</div></div>
        </div>

        <div class="chart-grid">
            <div class="chart-card full-width">
                <h3>Monthly Revenue & Profit Growth Trends</h3>
                <canvas id="monthlyChart" height="90"></canvas>
            </div>
            <div class="chart-card">
                <h3>Revenue by Product Category</h3>
                <canvas id="catChart" height="200"></canvas>
            </div>
            <div class="chart-card">
                <h3>Regional Revenue Share</h3>
                <canvas id="regionChart" height="200"></canvas>
            </div>
        </div>
    </div>

    <!-- TAB 2: SALES & PRODUCTS -->
    <div id="tab-products" class="tab-content">
        <div class="chart-grid">
            <div class="chart-card full-width">
                <h3>Top 10 Best Selling Products by Revenue</h3>
                <canvas id="topProdChart" height="110"></canvas>
            </div>
        </div>
    </div>

    <!-- TAB 3: DEMAND FORECASTING & INVENTORY -->
    <div id="tab-forecast" class="tab-content">
        <div class="chart-grid">
            <div class="chart-card full-width">
                <h3>30-Day Time-Series Demand Forecast (Linear Regression Champion Model)</h3>
                <canvas id="forecastChart" height="100"></canvas>
            </div>
        </div>

        <div class="chart-card">
            <h3>Inventory Recommendations & Stockout Risk Engine</h3>
            <table>
                <thead>
                    <tr>
                        <th>Product Name</th>
                        <th>Category</th>
                        <th>Current Stock</th>
                        <th>Forecast 30D Demand</th>
                        <th>Demand Category</th>
                        <th>Stock Status</th>
                        <th>Action Recommendation</th>
                    </tr>
                </thead>
                <tbody id="inventoryTable">
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function switchTab(tabId) {{
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            document.getElementById('tab-' + tabId).classList.add('active');
            event.target.classList.add('active');
        }}

        // Monthly Chart
        new Chart(document.getElementById('monthlyChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps(monthly_labels)},
                datasets: [
                    {{ label: 'Revenue ($)', data: {json.dumps(monthly_sales)}, borderColor: '#38bdf8', backgroundColor: 'rgba(56, 189, 248, 0.1)', fill: true, tension: 0.3 }},
                    {{ label: 'Profit ($)', data: {json.dumps(monthly_profit)}, borderColor: '#34d399', backgroundColor: 'rgba(52, 211, 153, 0.1)', fill: true, tension: 0.3 }}
                ]
            }},
            options: {{ responsive: true, plugins: {{ legend: {{ labels: {{ color: '#f8fafc' }} }} }}, scales: {{ x: {{ ticks: {{ color: '#94a3b8' }} }}, y: {{ ticks: {{ color: '#94a3b8' }} }} }} }}
        }});

        // Category Chart
        new Chart(document.getElementById('catChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(cat_labels)},
                datasets: [{{ label: 'Revenue ($)', data: {json.dumps(cat_sales)}, backgroundColor: '#c084fc' }}]
            }},
            options: {{ responsive: true, plugins: {{ legend: {{ labels: {{ color: '#f8fafc' }} }} }}, scales: {{ x: {{ ticks: {{ color: '#94a3b8' }} }}, y: {{ ticks: {{ color: '#94a3b8' }} }} }} }}
        }});

        // Regional Chart
        new Chart(document.getElementById('regionChart'), {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(reg_labels)},
                datasets: [{{ data: {json.dumps(reg_sales)}, backgroundColor: ['#38bdf8', '#34d399', '#c084fc', '#fbbf24', '#f43f5e'] }}]
            }},
            options: {{ responsive: true, plugins: {{ legend: {{ labels: {{ color: '#f8fafc' }} }} }} }}
        }});

        // Top Products Chart
        new Chart(document.getElementById('topProdChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(top_p_labels)},
                datasets: [{{ label: 'Revenue ($)', data: {json.dumps(top_p_sales)}, backgroundColor: '#38bdf8' }}]
            }},
            options: {{ indexAxis: 'y', responsive: true, plugins: {{ legend: {{ labels: {{ color: '#f8fafc' }} }} }}, scales: {{ x: {{ ticks: {{ color: '#94a3b8' }} }}, y: {{ ticks: {{ color: '#94a3b8' }} }} }} }}
        }});

        // Forecast Chart
        new Chart(document.getElementById('forecastChart'), {{
            type: 'line',
            data: {{
                labels: {json.dumps(fcst_dates)},
                datasets: [
                    {{ label: 'Actual Demand', data: {json.dumps(actual_demand)}, borderColor: '#38bdf8', backgroundColor: '#38bdf8', pointRadius: 2 }},
                    {{ label: 'Predicted Demand (30D)', data: {json.dumps(pred_demand)}, borderColor: '#34d399', borderDash: [5, 5], backgroundColor: '#34d399', pointRadius: 3 }},
                    {{ label: 'Upper Bound (95%)', data: {json.dumps(upper_bound)}, borderColor: 'rgba(251, 191, 36, 0.4)', fill: '+1', backgroundColor: 'rgba(251, 191, 36, 0.1)', pointRadius: 0 }},
                    {{ label: 'Lower Bound (95%)', data: {json.dumps(lower_bound)}, borderColor: 'rgba(251, 191, 36, 0.4)', fill: false, pointRadius: 0 }}
                ]
            }},
            options: {{ responsive: true, plugins: {{ legend: {{ labels: {{ color: '#f8fafc' }} }} }}, scales: {{ x: {{ ticks: {{ color: '#94a3b8' }} }}, y: {{ ticks: {{ color: '#94a3b8' }} }} }} }}
        }});

        // Populate Inventory Table
        const recData = {json.dumps(recs)};
        const tbody = document.getElementById('inventoryTable');
        recData.forEach(row => {{
            let badgeClass = 'badge-healthy';
            if (row.stock_status.includes('STOCKOUT')) badgeClass = 'badge-stockout';
            else if (row.stock_status.includes('OVERSTOCK')) badgeClass = 'badge-overstock';
            else if (row.stock_status.includes('REORDER')) badgeClass = 'badge-reorder';

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${{row.product_name}}</strong></td>
                <td>${{row.category}}</td>
                <td>${{row.current_stock}}</td>
                <td>${{row.forecasted_30d_demand}}</td>
                <td>${{row.demand_category}}</td>
                <td><span class="badge ${{badgeClass}}">${{row.stock_status}}</span></td>
                <td>${{row.action_recommendation}}</td>
            `;
            tbody.appendChild(tr);
        }});
    </script>
</body>
</html>
"""

    with open("dashboard.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Successfully built interactive HTML Dashboard at D:\\E-commerce\\dashboard.html")

if __name__ == "__main__":
    generate_interactive_dashboard()
