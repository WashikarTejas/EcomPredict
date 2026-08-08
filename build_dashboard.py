"""
Generates a state-of-the-art interactive BI Dashboard (dashboard.html) matching the exact
"Purse" modern UI layout, with Light & Dark themes, glassmorphism cards, time range pills,
smooth gradient wave charts, category breakdown sidebar, and inventory risk tables.
"""

import json
import pandas as pd

def generate_designer_dashboard():
    # Load Processed Data
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
    cat_df = cleaned_df.groupby("category")[["sales", "profit"]].sum().reset_index().sort_values(by="sales", ascending=False)
    cat_labels = cat_df["category"].tolist()
    cat_sales = cat_df["sales"].round(2).tolist()
    cat_profit = cat_df["profit"].round(2).tolist()

    # Forecast Data
    forecast_df["order_date"] = pd.to_datetime(forecast_df["order_date"])
    recent_hist = forecast_df[forecast_df["is_forecast"] == 0].tail(30)
    future_fcst = forecast_df[forecast_df["is_forecast"] == 1]
    
    fcst_dates = recent_hist["order_date"].dt.strftime("%b %d").tolist() + future_fcst["order_date"].dt.strftime("%b %d").tolist()
    actual_demand = recent_hist["actual_demand"].tolist() + [None]*len(future_fcst)
    pred_demand = [None]*len(recent_hist) + future_fcst["predicted_demand"].tolist()

    # Top Recent Transactions
    recent_tx = cleaned_df.sort_values(by="order_date", ascending=False).head(5).to_dict(orient="records")

    # KPIs
    tot_rev = float(cleaned_df["sales"].sum())
    tot_prof = float(cleaned_df["profit"].sum())
    tot_orders = int(cleaned_df["order_id"].nunique())
    tot_units = int(cleaned_df["quantity"].sum())
    aov = float(tot_rev / tot_orders)
    margin = float(tot_prof / tot_rev * 100)

    recs = rec_df.to_dict(orient="records")

    html_content = f"""<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>E-Commerce Sales Intelligence & Demand Forecasting</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-body: #0f1015;
            --sidebar-bg: #15171e;
            --card-bg: #1a1d26;
            --card-subtle: #222632;
            --border-color: rgba(255, 255, 255, 0.07);
            --text-main: #ffffff;
            --text-muted: #8a8f9d;
            --primary-orange: #ff6b35;
            --primary-orange-hover: #ff8555;
            --accent-purple: #9d4edd;
            --accent-purple-light: #c084fc;
            --accent-pink: #f72585;
            --accent-green: #10b981;
            --accent-blue: #3b82f6;
            --shadow-card: 0 10px 30px rgba(0, 0, 0, 0.3);
            --glass-card: linear-gradient(135deg, rgba(168, 85, 247, 0.75), rgba(249, 115, 22, 0.75));
        }}

        [data-theme="light"] {{
            --bg-body: #f4f5f8;
            --sidebar-bg: #ffffff;
            --card-bg: #ffffff;
            --card-subtle: #f8f9fa;
            --border-color: rgba(0, 0, 0, 0.06);
            --text-main: #18191c;
            --text-muted: #6b7280;
            --primary-orange: #ff6b35;
            --shadow-card: 0 10px 25px rgba(0, 0, 0, 0.04);
            --glass-card: linear-gradient(135deg, rgba(168, 85, 247, 0.85), rgba(249, 115, 22, 0.85));
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; transition: background 0.3s ease, color 0.3s ease; }}
        body {{ background: var(--bg-body); color: var(--text-main); display: flex; min-height: 100vh; overflow-x: hidden; }}

        /* Left Navigation Bar */
        .sidebar {{ width: 80px; background: var(--sidebar-bg); border-right: 1px solid var(--border-color); display: flex; flex-direction: column; align-items: center; padding: 2rem 0; gap: 2rem; z-index: 10; }}
        .sidebar-logo {{ width: 42px; height: 42px; background: var(--primary-orange); border-radius: 12px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.3rem; color: #fff; box-shadow: 0 0 20px rgba(255, 107, 53, 0.4); }}
        .nav-icons {{ display: flex; flex-direction: column; gap: 1.5rem; width: 100%; align-items: center; margin-top: 1rem; }}
        .nav-item {{ width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; color: var(--text-muted); cursor: pointer; transition: all 0.2s ease; }}
        .nav-item:hover, .nav-item.active {{ background: rgba(255, 107, 53, 0.15); color: var(--primary-orange); }}

        /* Main Workspace */
        .main-workspace {{ flex: 1; display: flex; flex-direction: column; padding: 2rem 2.5rem; gap: 2rem; overflow-y: auto; }}

        /* Header / Top Bar */
        .top-header {{ display: flex; justify-content: space-between; align-items: center; width: 100%; }}
        .brand-title {{ font-size: 1.8rem; font-weight: 800; letter-spacing: -0.5px; color: var(--text-main); }}
        
        .time-pills {{ display: flex; background: var(--card-bg); border: 1px solid var(--border-color); padding: 4px; border-radius: 30px; gap: 4px; box-shadow: var(--shadow-card); }}
        .pill {{ padding: 8px 22px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; color: var(--text-muted); cursor: pointer; border: none; background: transparent; transition: all 0.2s ease; }}
        .pill.active {{ background: var(--primary-orange); color: #ffffff; box-shadow: 0 4px 15px rgba(255, 107, 53, 0.4); }}

        .header-actions {{ display: flex; align-items: center; gap: 1.25rem; }}
        .theme-toggle-btn {{ background: var(--card-bg); border: 1px solid var(--border-color); color: var(--text-main); padding: 8px 16px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; box-shadow: var(--shadow-card); }}
        .user-avatar {{ display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 0.9rem; cursor: pointer; }}
        .user-avatar img {{ width: 38px; height: 38px; border-radius: 50%; object-fit: cover; border: 2px solid var(--primary-orange); }}

        /* Dashboard Grid Layout */
        .dashboard-grid {{ display: grid; grid-template-columns: 2.2fr 1fr; gap: 2rem; width: 100%; }}
        .left-panel {{ display: flex; flex-direction: column; gap: 2rem; }}
        .right-panel {{ display: flex; flex-direction: column; gap: 2rem; }}

        /* Card Rows */
        .top-cards-row {{ display: grid; grid-template-columns: 1.2fr 1fr; gap: 1.5rem; }}

        /* Glassmorphic Credit / Performance Card */
        .glass-card {{ background: var(--glass-card); backdrop-filter: blur(20px); border-radius: 24px; padding: 1.75rem; color: #ffffff; display: flex; flex-direction: column; justify-content: space-between; height: 210px; box-shadow: 0 15px 35px rgba(168, 85, 247, 0.3); position: relative; overflow: hidden; }}
        .glass-card::after {{ content: ''; position: absolute; right: -30px; bottom: -30px; width: 150px; height: 150px; background: rgba(255, 255, 255, 0.15); border-radius: 50%; pointer-events: none; }}
        .card-top {{ display: flex; justify-content: space-between; align-items: center; }}
        .card-chip {{ width: 42px; height: 30px; background: rgba(255, 255, 255, 0.3); border-radius: 6px; border: 1px solid rgba(255, 255, 255, 0.4); }}
        .card-number {{ font-size: 1.2rem; font-weight: 700; letter-spacing: 2px; margin: 1rem 0; }}
        .card-bottom {{ display: flex; justify-content: space-between; align-items: flex-end; }}
        .card-label {{ font-size: 0.75rem; opacity: 0.8; text-transform: uppercase; }}
        .card-val {{ font-size: 1.1rem; font-weight: 800; }}

        /* Widget Card container */
        .widget-card {{ background: var(--card-bg); border: 1px solid var(--border-color); border-radius: 24px; padding: 1.75rem; box-shadow: var(--shadow-card); display: flex; flex-direction: column; gap: 1rem; }}
        .widget-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }}
        .widget-title {{ font-size: 1.1rem; font-weight: 700; color: var(--text-main); }}
        .widget-sub {{ font-size: 0.8rem; color: var(--text-muted); }}

        /* Recent Transactions List */
        .tx-list {{ display: flex; flex-direction: column; gap: 1rem; }}
        .tx-item {{ display: flex; align-items: center; justify-content: space-between; padding-bottom: 0.75rem; border-bottom: 1px solid var(--border-color); }}
        .tx-item:last-child {{ border-bottom: none; padding-bottom: 0; }}
        .tx-left {{ display: flex; align-items: center; gap: 12px; }}
        .tx-icon {{ width: 36px; height: 36px; border-radius: 10px; background: var(--card-subtle); display: flex; align-items: center; justify-content: center; font-size: 1.1rem; }}
        .tx-name {{ font-size: 0.9rem; font-weight: 700; color: var(--text-main); }}
        .tx-date {{ font-size: 0.75rem; color: var(--text-muted); }}
        .tx-amount {{ font-size: 0.9rem; font-weight: 700; color: var(--accent-green); }}

        /* Bottom Charts Row */
        .bottom-charts-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }}

        /* Right Panel Widgets */
        .progress-circle-box {{ display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; margin: 1rem 0; }}
        .balance-box {{ text-align: center; margin: 1rem 0; }}
        .balance-amount {{ font-size: 2.2rem; font-weight: 800; color: var(--text-main); letter-spacing: -1px; }}
        .balance-label {{ font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; font-weight: 600; margin-top: 4px; }}

        /* Category Breakdown List */
        .cat-list {{ display: flex; flex-direction: column; gap: 1rem; margin-top: 0.5rem; }}
        .cat-row {{ display: flex; justify-content: space-between; align-items: center; font-size: 0.9rem; font-weight: 600; }}
        .cat-left {{ display: flex; align-items: center; gap: 10px; }}
        .cat-dot {{ width: 10px; height: 10px; border-radius: 50%; }}

        /* Table Styling */
        table {{ width: 100%; border-collapse: collapse; margin-top: 0.5rem; text-align: left; }}
        th, td {{ padding: 0.75rem 1rem; border-bottom: 1px solid var(--border-color); font-size: 0.85rem; }}
        th {{ color: var(--text-muted); font-weight: 700; text-transform: uppercase; font-size: 0.75rem; background: var(--card-subtle); }}
        .badge {{ padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; display: inline-block; }}
        .badge-stockout {{ background: rgba(247, 37, 133, 0.15); color: var(--accent-pink); border: 1px solid var(--accent-pink); }}
        .badge-overstock {{ background: rgba(255, 107, 53, 0.15); color: var(--primary-orange); border: 1px solid var(--primary-orange); }}
        .badge-reorder {{ background: rgba(157, 78, 221, 0.15); color: var(--accent-purple-light); border: 1px solid var(--accent-purple-light); }}
        .badge-healthy {{ background: rgba(16, 185, 129, 0.15); color: var(--accent-green); border: 1px solid var(--accent-green); }}

        @media (max-width: 1200px) {{
            .dashboard-grid {{ grid-template-columns: 1fr; }}
            .top-cards-row, .bottom-charts-row {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>

    <!-- Left Sidebar Navigation -->
    <div class="sidebar">
        <div class="sidebar-logo">P</div>
        <div class="nav-icons">
            <div class="nav-item active" title="Dashboard">⚡</div>
            <div class="nav-item" title="Analytics">📈</div>
            <div class="nav-item" title="Transactions">💳</div>
            <div class="nav-item" title="Inventory">📦</div>
            <div class="nav-item" title="Forecasting">🎯</div>
            <div class="nav-item" title="Settings">⚙️</div>
        </div>
    </div>

    <!-- Main Workspace -->
    <div class="main-workspace">
        
        <!-- Header Bar -->
        <div class="top-header">
            <div class="brand-title">Purse Analytics</div>
            
            <!-- Time Period Pills -->
            <div class="time-pills">
                <button class="pill">Day</button>
                <button class="pill active">Week</button>
                <button class="pill">Month</button>
                <button class="pill">Year</button>
            </div>

            <div class="header-actions">
                <button class="theme-toggle-btn" id="themeBtn" onclick="toggleTheme()">
                    <span id="themeIcon">🌙</span> <span id="themeText">Dark Theme</span>
                </button>
                <div class="user-avatar">
                    <img src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&auto=format&fit=crop&q=80" alt="Avatar">
                    <span>Tejas Washikar</span>
                </div>
            </div>
        </div>

        <!-- Dashboard Grid Layout -->
        <div class="dashboard-grid">
            
            <!-- Left Main Panel -->
            <div class="left-panel">
                
                <!-- Top Row: Glass Card + Recent Activity -->
                <div class="top-cards-row">
                    <!-- Glassmorphic Card -->
                    <div class="glass-card">
                        <div class="card-top">
                            <span style="font-weight: 700; font-size: 1rem;">VISA Executive</span>
                            <div class="card-chip"></div>
                        </div>
                        <div class="card-number">•••• •••• 8702</div>
                        <div class="card-bottom">
                            <div>
                                <div class="card-label">Net Sales Revenue</div>
                                <div class="card-val">${tot_rev:,.2f}</div>
                            </div>
                            <div>
                                <div class="card-label">Profit Margin</div>
                                <div class="card-val">{margin:.1f}%</div>
                            </div>
                            <div style="font-weight: 800; font-size: 1.3rem;">VISA</div>
                        </div>
                    </div>

                    <!-- Recent Sales Activity -->
                    <div class="widget-card">
                        <div class="widget-header">
                            <div class="widget-title">Recent Transactions</div>
                            <div class="widget-sub">Live Orders</div>
                        </div>
                        <div class="tx-list">
                            <div class="tx-item">
                                <div class="tx-left">
                                    <div class="tx-icon">🎧</div>
                                    <div>
                                        <div class="tx-name">Wireless Headphones</div>
                                        <div class="tx-date">ORD-11995 • Electronics</div>
                                    </div>
                                </div>
                                <div class="tx-amount">+$149.99</div>
                            </div>
                            <div class="tx-item">
                                <div class="tx-left">
                                    <div class="tx-icon">🖥️</div>
                                    <div>
                                        <div class="tx-name">4K Gaming Monitor</div>
                                        <div class="tx-date">ORD-11994 • Electronics</div>
                                    </div>
                                </div>
                                <div class="tx-amount">+$499.99</div>
                            </div>
                            <div class="tx-item">
                                <div class="tx-left">
                                    <div class="tx-icon">🪑</div>
                                    <div>
                                        <div class="tx-name">Mesh Office Chair</div>
                                        <div class="tx-date">ORD-11993 • Furniture</div>
                                    </div>
                                </div>
                                <div class="tx-amount">+$229.99</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Bottom Row: Activity Line Wave + Payments Bar Chart -->
                <div class="bottom-charts-row">
                    <!-- Activity Smooth Wave Chart -->
                    <div class="widget-card">
                        <div class="widget-header">
                            <div class="widget-title">Revenue Growth Activity</div>
                            <div class="widget-sub">Monthly Trend</div>
                        </div>
                        <div style="height: 180px;">
                            <canvas id="activityChart"></canvas>
                        </div>
                    </div>

                    <!-- Payments Bar Chart -->
                    <div class="widget-card">
                        <div class="widget-header">
                            <div class="widget-title">Category Revenue Breakdown</div>
                            <div class="widget-sub">Sales Performance</div>
                        </div>
                        <div style="height: 180px;">
                            <canvas id="paymentsChart"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Demand Forecasting & Inventory Engine Table -->
                <div class="widget-card">
                    <div class="widget-header">
                        <div class="widget-title">ML Demand Forecast & Inventory Stockout Engine</div>
                        <div class="widget-sub">30-Day Predictive Actions</div>
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>Product SKU</th>
                                <th>Category</th>
                                <th>Stock</th>
                                <th>Forecast 30D</th>
                                <th>Status</th>
                                <th>Action Recommendation</th>
                            </tr>
                        </thead>
                        <tbody id="inventoryTable"></tbody>
                    </table>
                </div>

            </div>

            <!-- Right Panel: Balance Ring + Category Spent -->
            <div class="right-panel">
                <div class="widget-card" style="align-items: center; text-align: center;">
                    
                    <!-- Circular Donut Ring -->
                    <div class="progress-circle-box" style="width: 170px; height: 170px;">
                        <canvas id="donutRingChart"></canvas>
                        <div style="position: absolute; text-align: center;">
                            <div style="font-size: 1.8rem; font-weight: 800; color: var(--text-main);">{margin:.0f}%</div>
                            <div style="font-size: 0.75rem; color: var(--text-muted); font-weight: 600;">Profit Margin</div>
                        </div>
                    </div>

                    <div class="balance-box">
                        <div class="balance-amount">${tot_rev:,.2f}</div>
                        <div class="balance-label">Total Generated Revenue</div>
                    </div>

                    <hr style="width: 100%; border: none; border-top: 1px solid var(--border-color); margin: 1rem 0;">

                    <!-- Category Spent Breakdown List -->
                    <div style="width: 100%;">
                        <div style="text-align: left; font-size: 0.95rem; font-weight: 700; margin-bottom: 1rem; color: var(--text-main);">Category Revenue</div>
                        <div class="cat-list">
                            <div class="cat-row">
                                <div class="cat-left"><div class="cat-dot" style="background: #9d4edd;"></div> Furniture</div>
                                <div>${cat_sales[0]:,.2f}</div>
                            </div>
                            <div class="cat-row">
                                <div class="cat-left"><div class="cat-dot" style="background: #3b82f6;"></div> Electronics</div>
                                <div>${cat_sales[1]:,.2f}</div>
                            </div>
                            <div class="cat-row">
                                <div class="cat-left"><div class="cat-dot" style="background: #ff6b35;"></div> Home & Kitchen</div>
                                <div>${cat_sales[2]:,.2f}</div>
                            </div>
                            <div class="cat-row">
                                <div class="cat-left"><div class="cat-dot" style="background: #10b981;"></div> Apparel</div>
                                <div>${cat_sales[3]:,.2f}</div>
                            </div>
                            <div class="cat-row">
                                <div class="cat-left"><div class="cat-dot" style="background: #f72585;"></div> Office Supplies</div>
                                <div>${cat_sales[4]:,.2f}</div>
                            </div>
                        </div>
                    </div>

                </div>
            </div>

        </div>

    </div>

    <script>
        // Theme Toggle Handler
        function toggleTheme() {{
            const html = document.documentElement;
            const btnText = document.getElementById('themeText');
            const btnIcon = document.getElementById('themeIcon');
            
            if (html.getAttribute('data-theme') === 'dark') {{
                html.setAttribute('data-theme', 'light');
                btnText.textContent = 'Light Theme';
                btnIcon.textContent = '☀️';
            }} else {{
                html.setAttribute('data-theme', 'dark');
                btnText.textContent = 'Dark Theme';
                btnIcon.textContent = '🌙';
            }}
        }}

        // Smooth Wave Activity Chart
        const actCtx = document.getElementById('activityChart').getContext('2d');
        const gradientPurple = actCtx.createLinearGradient(0, 0, 0, 180);
        gradientPurple.addColorStop(0, 'rgba(157, 78, 221, 0.4)');
        gradientPurple.addColorStop(1, 'rgba(157, 78, 221, 0.0)');

        new Chart(actCtx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(monthly_labels)},
                datasets: [{{
                    label: 'Revenue',
                    data: {json.dumps(monthly_sales)},
                    borderColor: '#9d4edd',
                    borderWidth: 3,
                    backgroundColor: gradientPurple,
                    fill: true,
                    tension: 0.45,
                    pointRadius: 0
                }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ display: false }} }} }}
        }});

        // Payments Bar Chart with Orange Highlight
        const payCtx = document.getElementById('paymentsChart').getContext('2d');
        new Chart(payCtx, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(cat_labels)},
                datasets: [{{
                    data: {json.dumps(cat_sales)},
                    backgroundColor: ['#ff6b35', '#3b82f6', '#9d4edd', '#10b981', '#f72585'],
                    borderRadius: 8
                }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }} }}, scales: {{ x: {{ display: false }}, y: {{ display: false }} }} }}
        }});

        // Donut Ring Chart
        const ringCtx = document.getElementById('donutRingChart').getContext('2d');
        new Chart(ringCtx, {{
            type: 'doughnut',
            data: {{
                datasets: [{{
                    data: [{margin:.0f}, {100 - margin:.0f}],
                    backgroundColor: ['#9d4edd', 'rgba(255,255,255,0.08)'],
                    borderWidth: 0,
                    cutout: '82%'
                }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ display: false }}, tooltip: {{ enabled: false }} }} }}
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
    print("Successfully built Purser-styled Light/Dark theme Dashboard at D:\\E-commerce\\dashboard.html")

if __name__ == "__main__":
    generate_designer_dashboard()
