"""
generate_docs_site.py
Generates an interactive, standalone single-page web application
for Expense Tracker App (Khaata · Expense Intelligence) for GitHub Pages.
"""

import json
import os
import pandas as pd
import numpy as np

# Load CSV data
monthly_df = pd.read_csv("outputs/reports/monthly_summary.csv")
cat_df = pd.read_csv("outputs/reports/category_breakdown.csv")
budget_df = pd.read_csv("outputs/reports/budget_vs_actual.csv")
anomalies_df = pd.read_csv("outputs/reports/anomalies.csv")
cleaned_df = pd.read_csv("data/cleaned_expenses.csv")

# Sort cleaned transactions by date descending
cleaned_df["Date"] = pd.to_datetime(cleaned_df["Date"])
cleaned_df = cleaned_df.sort_values("Date", ascending=False)
sample_txns = cleaned_df.head(100).copy()
sample_txns["Date"] = sample_txns["Date"].dt.strftime("%Y-%m-%d")

# Prepare payment method breakdown
payment_mix = cleaned_df[cleaned_df["Type"] == "Expense"].groupby("Payment_Method")["Amount"].sum().reset_index()
payment_mix["Percentage"] = (payment_mix["Amount"] / payment_mix["Amount"].sum() * 100).round(1)

# Prepare weekday distribution
weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
weekday_spend = cleaned_df[cleaned_df["Type"] == "Expense"].groupby("Weekday")["Amount"].agg(["sum", "count"]).reindex(weekday_order).reset_index()

# Top 10 merchants
top_merchants = cleaned_df[cleaned_df["Type"] == "Expense"].groupby("Merchant")["Amount"].agg(["sum", "count"]).sort_values("sum", ascending=False).head(10).reset_index()

data_payload = {
    "kpis": {
        "total_income": int(cleaned_df[cleaned_df["Type"] == "Income"]["Amount"].sum()),
        "total_expense": int(cleaned_df[cleaned_df["Type"] == "Expense"]["Amount"].sum()),
        "net_savings": int(cleaned_df[cleaned_df["Type"] == "Income"]["Amount"].sum() - cleaned_df[cleaned_df["Type"] == "Expense"]["Amount"].sum()),
        "savings_rate": round((cleaned_df[cleaned_df["Type"] == "Income"]["Amount"].sum() - cleaned_df[cleaned_df["Type"] == "Expense"]["Amount"].sum()) / cleaned_df[cleaned_df["Type"] == "Income"]["Amount"].sum() * 100, 1),
        "health_score": 53,
        "health_label": "Fair",
        "forecast_next_month": 53242,
        "top_category": "Rent",
        "top_category_amount": 168000,
        "total_txns": len(cleaned_df)
    },
    "monthly": monthly_df.fillna(0).to_dict(orient="records"),
    "categories": cat_df.to_dict(orient="records"),
    "budget": budget_df.to_dict(orient="records"),
    "anomalies": anomalies_df.to_dict(orient="records"),
    "payment_mix": payment_mix.to_dict(orient="records"),
    "weekday_spend": weekday_spend.to_dict(orient="records"),
    "top_merchants": top_merchants.to_dict(orient="records"),
    "transactions": sample_txns[["Date", "Category", "Description", "Merchant", "Amount", "Type", "Payment_Method"]].to_dict(orient="records")
}

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Khaata · Expense Intelligence & Personal Finance Suite</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {{
      --bg-base: #0c0e14;
      --bg-card: rgba(19, 23, 34, 0.75);
      --bg-card-hover: rgba(28, 34, 50, 0.85);
      --border-card: rgba(255, 255, 255, 0.08);
      --border-accent: rgba(143, 164, 194, 0.3);
      --text-main: #f1f5f9;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --primary: #38bdf8;
      --accent: #818cf8;
      --success: #34d399;
      --warning: #fbbf24;
      --danger: #f87171;
      --font-sans: 'Plus Jakarta Sans', sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background-color: var(--bg-base);
      color: var(--text-main);
      font-family: var(--font-sans);
      line-height: 1.6;
      background-image: 
        radial-gradient(circle at 10% 15%, rgba(56, 189, 248, 0.07) 0%, transparent 40%),
        radial-gradient(circle at 90% 80%, rgba(129, 140, 248, 0.07) 0%, transparent 40%);
      background-attachment: fixed;
      min-height: 100vh;
    }}

    header {{
      background: rgba(12, 14, 20, 0.85);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--border-card);
      position: sticky;
      top: 0;
      z-index: 1000;
      padding: 1rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .logo-container {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}

    .logo-badge {{
      background: linear-gradient(135deg, #38bdf8, #818cf8);
      width: 40px;
      height: 40px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 1.3rem;
      color: #0c0e14;
    }}

    .logo-text h1 {{
      font-size: 1.15rem;
      font-weight: 700;
      letter-spacing: -0.02em;
    }}

    .logo-text p {{
      font-size: 0.75rem;
      color: var(--text-muted);
    }}

    nav {{
      display: flex;
      gap: 1.25rem;
    }}

    nav a {{
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.875rem;
      font-weight: 500;
      transition: color 0.2s ease;
      cursor: pointer;
    }}

    nav a:hover, nav a.active {{
      color: var(--primary);
    }}

    .container {{
      max-width: 1400px;
      margin: 0 auto;
      padding: 2rem;
    }}

    .hero {{
      text-align: center;
      padding: 2.5rem 1rem 2rem;
    }}

    .hero-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.35rem 1rem;
      background: rgba(56, 189, 248, 0.1);
      border: 1px solid rgba(56, 189, 248, 0.3);
      border-radius: 9999px;
      font-size: 0.8rem;
      color: var(--primary);
      font-weight: 600;
      margin-bottom: 1rem;
    }}

    .hero h2 {{
      font-size: 2.75rem;
      font-weight: 800;
      letter-spacing: -0.03em;
      margin-bottom: 1rem;
      background: linear-gradient(135deg, #ffffff 30%, #94a3b8 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    .hero p {{
      max-width: 750px;
      margin: 0 auto;
      color: var(--text-muted);
      font-size: 1.05rem;
    }}

    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 1.25rem;
      margin-bottom: 2.5rem;
    }}

    .kpi-card {{
      background: var(--bg-card);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-card);
      border-radius: 14px;
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      transition: all 0.3s ease;
    }}

    .kpi-card:hover {{
      border-color: var(--border-accent);
      transform: translateY(-2px);
    }}

    .kpi-title {{
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-dim);
      font-weight: 600;
      margin-bottom: 0.5rem;
    }}

    .kpi-value {{
      font-size: 1.85rem;
      font-weight: 800;
      color: var(--text-main);
      font-family: var(--font-mono);
      letter-spacing: -0.02em;
    }}

    .kpi-subtext {{
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-top: 0.35rem;
    }}

    .section-title {{
      font-size: 1.5rem;
      font-weight: 700;
      margin-bottom: 1.25rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .grid-2 {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2.5rem;
    }}

    .grid-3 {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2.5rem;
    }}

    .panel {{
      background: var(--bg-card);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-card);
      border-radius: 14px;
      padding: 1.5rem;
    }}

    .chart-container {{
      width: 100%;
      height: 380px;
    }}

    /* Simulator Styles */
    .simulator-box {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 2rem;
    }}

    @media (max-width: 900px) {{
      .simulator-box {{
        grid-template-columns: 1fr;
      }}
      .grid-2 {{
        grid-template-columns: 1fr;
      }}
    }}

    .sim-slider-row {{
      margin-bottom: 1.15rem;
    }}

    .sim-slider-header {{
      display: flex;
      justify-content: space-between;
      font-size: 0.85rem;
      margin-bottom: 0.35rem;
    }}

    .sim-slider-header span:first-child {{
      color: var(--text-muted);
      font-weight: 500;
    }}

    .sim-slider-header span:last-child {{
      font-family: var(--font-mono);
      color: var(--primary);
      font-weight: 600;
    }}

    input[type=range] {{
      width: 100%;
      height: 6px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 6px;
      outline: none;
      -webkit-appearance: none;
      cursor: pointer;
    }}

    input[type=range]::-webkit-slider-thumb {{
      -webkit-appearance: none;
      width: 18px;
      height: 18px;
      border-radius: 50%;
      background: var(--primary);
      box-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
      cursor: pointer;
    }}

    .sim-result-card {{
      background: rgba(12, 14, 20, 0.6);
      border: 1px solid var(--border-accent);
      border-radius: 12px;
      padding: 1.75rem;
      display: flex;
      flex-direction: column;
      gap: 1.25rem;
    }}

    .table-wrapper {{
      overflow-x: auto;
      max-height: 450px;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.85rem;
    }}

    th {{
      background: rgba(12, 14, 20, 0.9);
      color: var(--text-dim);
      font-weight: 600;
      padding: 0.75rem 1rem;
      position: sticky;
      top: 0;
      border-bottom: 1px solid var(--border-card);
    }}

    td {{
      padding: 0.65rem 1rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.04);
      color: var(--text-muted);
    }}

    tr:hover td {{
      background: rgba(255, 255, 255, 0.02);
      color: var(--text-main);
    }}

    .badge-pill {{
      display: inline-block;
      padding: 0.2rem 0.6rem;
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 600;
    }}

    .status-over {{
      background: rgba(248, 113, 113, 0.15);
      color: #f87171;
      border: 1px solid rgba(248, 113, 113, 0.4);
    }}

    .status-under {{
      background: rgba(52, 211, 153, 0.15);
      color: #34d399;
      border: 1px solid rgba(52, 211, 153, 0.4);
    }}

    .status-limit {{
      background: rgba(251, 191, 36, 0.15);
      color: #fbbf24;
      border: 1px solid rgba(251, 191, 36, 0.4);
    }}

    footer {{
      border-top: 1px solid var(--border-card);
      padding: 2rem;
      text-align: center;
      color: var(--text-dim);
      font-size: 0.85rem;
      margin-top: 4rem;
    }}

    footer a {{
      color: var(--primary);
      text-decoration: none;
    }}
  </style>
</head>
<body>

  <header>
    <div class="logo-container">
      <div class="logo-badge">₹</div>
      <div class="logo-text">
        <h1>Khaata · Expense Intelligence</h1>
        <p>Personal Finance Analytics, Anomaly Radar & Predictive Cashflow</p>
      </div>
    </div>
    <nav>
      <a href="#overview" class="active">Overview</a>
      <a href="#cashflow">Cash Flow</a>
      <a href="#budget">Budget vs Actual</a>
      <a href="#simulator">What-If Planner</a>
      <a href="#transactions">Ledger</a>
      <a href="https://github.com/rohitsingh83/Expense-Tracker-App" target="_blank">GitHub Repo ↗</a>
    </nav>
  </header>

  <div class="container">
    <section class="hero" id="overview">
      <div class="hero-badge">✦ Complete Personal Finance Intelligence Suite</div>
      <h2>Take Absolute Control of Personal Wealth & Cash Burn</h2>
      <p>Automated cleaning, 10 analytical visualizations, budget adherence auditing, outlier detection (Modified Z-score &ge; 2.5), next-month expenditure forecasting, and an interactive what-if savings simulator.</p>
    </section>

    <!-- KPI Summary Cards -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-title">Total Inflows (12M)</div>
        <div class="kpi-value">₹{data_payload["kpis"]["total_income"]:,}</div>
        <div class="kpi-subtext">Salary + freelancing + dividends</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Total Outflows (12M)</div>
        <div class="kpi-value">₹{data_payload["kpis"]["total_expense"]:,}</div>
        <div class="kpi-subtext">Across 671 ledger transactions</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Net Accumulated Savings</div>
        <div class="kpi-value">₹{data_payload["kpis"]["net_savings"]:,}</div>
        <div class="kpi-subtext">Savings rate: {data_payload["kpis"]["savings_rate"]}%</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Financial Health Score</div>
        <div class="kpi-value">{data_payload["kpis"]["health_score"]}/100</div>
        <div class="kpi-subtext">Status: {data_payload["kpis"]["health_label"]} (Emergency fund buffer low)</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-title">Next Month Forecast</div>
        <div class="kpi-value">₹{data_payload["kpis"]["forecast_next_month"]:,}</div>
        <div class="kpi-subtext">Linear regression + 3M weighted average</div>
      </div>
    </div>

    <!-- Charts Section 1: Cash Flow & Trends -->
    <div class="section-title" id="cashflow">📈 Monthly Inflow vs Outflow Velocity</div>
    <div class="grid-2">
      <div class="panel">
        <h3 style="font-size: 1.1rem; margin-bottom: 1rem;">Income vs Expense Trend (Monthly)</h3>
        <div id="chart-monthly" class="chart-container"></div>
      </div>
      <div class="panel">
        <h3 style="font-size: 1.1rem; margin-bottom: 1rem;">Net Monthly Savings & Accumulation</h3>
        <div id="chart-savings" class="chart-container"></div>
      </div>
    </div>

    <!-- Charts Section 2: Category Breakdown & Payment Mix -->
    <div class="section-title" id="budget">🍕 Category Outflow Breakdown & Budget Adherence</div>
    <div class="grid-2">
      <div class="panel">
        <h3 style="font-size: 1.1rem; margin-bottom: 1rem;">Expense Distribution by Category</h3>
        <div id="chart-categories" class="chart-container"></div>
      </div>
      <div class="panel">
        <h3 style="font-size: 1.1rem; margin-bottom: 1rem;">Payment Method Mix</h3>
        <div id="chart-payments" class="chart-container"></div>
      </div>
    </div>

    <!-- Budget vs Actual Table -->
    <div class="panel" style="margin-bottom: 2.5rem;">
      <h3 style="font-size: 1.1rem; margin-bottom: 1rem;">Monthly Budget vs Actual Burn by Category</h3>
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Category</th>
              <th>Monthly Budget</th>
              <th>Avg Monthly Actual</th>
              <th>Variance</th>
              <th>Variance %</th>
              <th>Budget Status</th>
            </tr>
          </thead>
          <tbody id="budget-table-body">
            <!-- populated by JS -->
          </tbody>
        </table>
      </div>
    </div>

    <!-- Interactive What-If Budget Simulator -->
    <div class="section-title" id="simulator">⚡ Interactive What-If Budget Optimizer</div>
    <div class="panel" style="margin-bottom: 2.5rem;">
      <p style="color: var(--text-muted); margin-bottom: 1.5rem; font-size: 0.95rem;">
        Simulate budget discipline adjustments below to see how optimizing discretionary leaks immediately boosts your annual savings and Financial Health Score.
      </p>

      <div class="simulator-box">
        <div>
          <div class="sim-slider-row">
            <div class="sim-slider-header">
              <span>Food & Dining Reduction:</span>
              <span id="lbl-food">0% (₹0 saved/mo)</span>
            </div>
            <input type="range" id="sim-food" min="0" max="50" step="5" value="0" oninput="updateBudgetSim()">
          </div>

          <div class="sim-slider-row">
            <div class="sim-slider-header">
              <span>Shopping Discretionary Trim:</span>
              <span id="lbl-shopping">0% (₹0 saved/mo)</span>
            </div>
            <input type="range" id="sim-shopping" min="0" max="60" step="5" value="0" oninput="updateBudgetSim()">
          </div>

          <div class="sim-slider-row">
            <div class="sim-slider-header">
              <span>Entertainment & Outings Trim:</span>
              <span id="lbl-ent">0% (₹0 saved/mo)</span>
            </div>
            <input type="range" id="sim-ent" min="0" max="50" step="5" value="0" oninput="updateBudgetSim()">
          </div>

          <div class="sim-slider-row">
            <div class="sim-slider-header">
              <span>Unused Subscriptions Cancelled:</span>
              <span id="lbl-sub">₹0 / month</span>
            </div>
            <input type="range" id="sim-sub" min="0" max="1000" step="100" value="0" oninput="updateBudgetSim()">
          </div>
        </div>

        <div class="sim-result-card">
          <div>
            <div style="font-size: 0.8rem; color: var(--text-dim); text-transform: uppercase; font-weight: 700;">Simulated Monthly Savings</div>
            <div id="sim-monthly-savings" style="font-size: 2rem; font-weight: 800; font-family: var(--font-mono); color: #34d399; margin-top: 0.35rem;">₹4,514 / mo</div>
            <div id="sim-annual-savings" style="font-size: 0.85rem; color: var(--text-muted); margin-top: 0.2rem;">+₹0 extra wealth accumulated per year</div>
          </div>

          <div>
            <div style="font-size: 0.8rem; color: var(--text-dim); text-transform: uppercase; font-weight: 700; margin-bottom: 0.5rem;">Projected Savings Rate</div>
            <div style="font-size: 1.5rem; font-weight: 800; font-family: var(--font-mono); color: #38bdf8;" id="sim-savings-rate">7.7%</div>
          </div>

          <div>
            <div style="font-size: 0.8rem; color: var(--text-dim); text-transform: uppercase; font-weight: 700; margin-bottom: 0.5rem;">Simulated Health Score</div>
            <div style="font-size: 1.5rem; font-weight: 800; font-family: var(--font-mono); color: #fbbf24;" id="sim-health-score">53 / 100</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Transaction Ledger -->
    <div class="section-title" id="transactions">📋 Cleaned Transaction Ledger (Latest 100 Entries)</div>
    <div class="panel">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 1rem;">
        <p style="font-size: 0.85rem; color: var(--text-muted);">
          Audited and cleaned transaction records with standardized merchants, amount bands, and normalized categories.
        </p>
        <input type="text" id="search-txn" placeholder="Search merchant, description, category..." style="background: rgba(12,14,20,0.8); border: 1px solid var(--border-card); color: white; padding: 0.4rem 0.8rem; border-radius: 6px; font-size: 0.85rem; width: 280px;" oninput="filterTxns()">
      </div>
      <div class="table-wrapper">
        <table id="txn-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Category</th>
              <th>Description</th>
              <th>Merchant</th>
              <th>Payment</th>
              <th>Type</th>
              <th>Amount</th>
            </tr>
          </thead>
          <tbody id="txn-body">
            <!-- populated by JS -->
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <footer>
    <p>Khaata · Expense Intelligence Suite &copy; 2026 Rohit Singh &bull; Powered by Python, Pandas & Plotly.js &bull; Hosted on GitHub Pages</p>
  </footer>

  <script>
    const DATA = {json.dumps(data_payload)};

    // Plot Monthly Income vs Expense
    const months = DATA.monthly.map(m => m.YearMonth);
    const income = DATA.monthly.map(m => m.Income);
    const expense = DATA.monthly.map(m => m.Expense);
    const net = DATA.monthly.map(m => m.Net);

    Plotly.newPlot('chart-monthly', [
      {{ x: months, y: income, name: 'Inflow (Income)', type: 'bar', marker: {{ color: '#34d399' }} }},
      {{ x: months, y: expense, name: 'Outflow (Expense)', type: 'bar', marker: {{ color: '#f87171' }} }}
    ], {{
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: {{ color: '#94a3b8', family: 'Plus Jakarta Sans' }},
      margin: {{ l: 50, r: 20, t: 20, b: 60 }},
      barmode: 'group',
      yaxis: {{ title: 'Amount (INR)', gridcolor: 'rgba(255,255,255,0.05)' }},
      legend: {{ orientation: 'h', y: 1.1 }}
    }}, {{ responsive: true, displayModeBar: false }});

    // Plot Net Savings
    Plotly.newPlot('chart-savings', [{{
      x: months,
      y: net,
      type: 'scatter',
      mode: 'lines+markers',
      line: {{ color: '#38bdf8', width: 3 }},
      marker: {{ size: 7, color: net.map(v => v >= 0 ? '#34d399' : '#f87171') }},
      name: 'Net Savings'
    }}], {{
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: {{ color: '#94a3b8', family: 'Plus Jakarta Sans' }},
      margin: {{ l: 50, r: 20, t: 20, b: 60 }},
      yaxis: {{ title: 'Net Savings (INR)', gridcolor: 'rgba(255,255,255,0.05)' }}
    }}, {{ responsive: true, displayModeBar: false }});

    // Plot Categories Donut
    const catLabels = DATA.categories.map(c => c.Category);
    const catValues = DATA.categories.map(c => c.Total_Amount);

    Plotly.newPlot('chart-categories', [{{
      labels: catLabels,
      values: catValues,
      type: 'pie',
      hole: 0.45,
      marker: {{
        colors: ['#38bdf8', '#818cf8', '#34d399', '#fbbf24', '#f87171', '#c084fc', '#f472b6', '#38bdf8', '#2dd4bf']
      }}
    }}], {{
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: {{ color: '#94a3b8', family: 'Plus Jakarta Sans' }},
      margin: {{ l: 20, r: 20, t: 20, b: 20 }}
    }}, {{ responsive: true, displayModeBar: false }});

    // Plot Payment Mix
    const payLabels = DATA.payment_mix.map(p => p.Payment_Method);
    const payValues = DATA.payment_mix.map(p => p.Amount);

    Plotly.newPlot('chart-payments', [{{
      x: payLabels,
      y: payValues,
      type: 'bar',
      marker: {{
        color: ['#38bdf8', '#818cf8', '#34d399', '#fbbf24', '#f87171']
      }}
    }}], {{
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: {{ color: '#94a3b8', family: 'Plus Jakarta Sans' }},
      margin: {{ l: 50, r: 20, t: 20, b: 40 }},
      yaxis: {{ title: 'Total Spend (INR)', gridcolor: 'rgba(255,255,255,0.05)' }}
    }}, {{ responsive: true, displayModeBar: false }});

    // Populate Budget vs Actual
    const budgetTbody = document.getElementById('budget-table-body');
    DATA.budget.forEach(row => {{
      const tr = document.createElement('tr');
      let statusClass = 'status-under';
      if (row.Status === 'Over budget') statusClass = 'status-over';
      else if (row.Status === 'Near limit') statusClass = 'status-limit';

      tr.innerHTML = `
        <td style="font-weight:600; color:white;">${{row.Category}}</td>
        <td>₹${{Math.round(row.Budget).toLocaleString()}}</td>
        <td>₹${{Math.round(row.Avg_Monthly_Actual).toLocaleString()}}</td>
        <td style="color:${{row.Variance < 0 ? '#f87171' : '#34d399'}}">₹${{Math.round(row.Variance).toLocaleString()}}</td>
        <td>${{row.Variance_%.toFixed(1)}}%</td>
        <td><span class="badge-pill ${{statusClass}}">${{row.Status}}</span></td>
      `;
      budgetTbody.appendChild(tr);
    }});

    // Populate Transactions Table
    const txnBody = document.getElementById('txn-body');
    function renderTxns(items) {{
      txnBody.innerHTML = '';
      items.forEach(t => {{
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td style="font-family:var(--font-mono);">${{t.Date}}</td>
          <td><span class="badge-pill" style="background:rgba(255,255,255,0.06); color:white;">${{t.Category}}</span></td>
          <td>${{t.Description}}</td>
          <td>${{t.Merchant}}</td>
          <td>${{t.Payment_Method}}</td>
          <td style="color:${{t.Type === 'Income' ? '#34d399' : '#f87171'}}">${{t.Type}}</td>
          <td style="font-family:var(--font-mono); font-weight:600; color:${{t.Type === 'Income' ? '#34d399' : 'white'}}">₹${{t.Amount.toLocaleString()}}</td>
        `;
        txnBody.appendChild(tr);
      }});
    }}
    renderTxns(DATA.transactions);

    function filterTxns() {{
      const q = document.getElementById('search-txn').value.toLowerCase();
      const filtered = DATA.transactions.filter(t => 
        t.Merchant.toLowerCase().includes(q) ||
        t.Category.toLowerCase().includes(q) ||
        t.Description.toLowerCase().includes(q)
      );
      renderTxns(filtered);
    }}

    // Budget What-If Simulator Logic
    function updateBudgetSim() {{
      const foodTrim = parseInt(document.getElementById('sim-food').value);
      const shopTrim = parseInt(document.getElementById('sim-shopping').value);
      const entTrim = parseInt(document.getElementById('sim-ent').value);
      const subTrim = parseInt(document.getElementById('sim-sub').value);

      const foodBase = 7078;
      const shopBase = 6335;
      const entBase = 3200;

      const foodSave = Math.round(foodBase * (foodTrim / 100));
      const shopSave = Math.round(shopBase * (shopTrim / 100));
      const entSave = Math.round(entBase * (entTrim / 100));

      document.getElementById('lbl-food').innerText = `${{foodTrim}}% (₹${{foodSave.toLocaleString()}} saved/mo)`;
      document.getElementById('lbl-shopping').innerText = `${{shopTrim}}% (₹${{shopSave.toLocaleString()}} saved/mo)`;
      document.getElementById('lbl-ent').innerText = `${{entTrim}}% (₹${{entSave.toLocaleString()}} saved/mo)`;
      document.getElementById('lbl-sub').innerText = `₹${{subTrim.toLocaleString()}} / month`;

      const monthlyExtra = foodSave + shopSave + entSave + subTrim;
      const baseMonthlySavings = 4514;
      const newMonthlySavings = baseMonthlySavings + monthlyExtra;
      const annualExtra = monthlyExtra * 12;

      const avgMonthlyIncome = 58870;
      const newSavingsRate = ((newMonthlySavings / avgMonthlyIncome) * 100).toFixed(1);
      const newHealthScore = Math.min(95, Math.round(53 + (monthlyExtra / 280)));

      document.getElementById('sim-monthly-savings').innerText = `₹${{newMonthlySavings.toLocaleString()}} / mo`;
      document.getElementById('sim-annual-savings').innerText = `+₹${{annualExtra.toLocaleString()}} extra wealth accumulated per year`;
      document.getElementById('sim-savings-rate').innerText = `${{newSavingsRate}}% (vs 7.7% baseline)`;
      document.getElementById('sim-health-score').innerText = `${{newHealthScore}} / 100`;
    }}

    updateBudgetSim();
  </script>
</body>
</html>
"""

os.makedirs("docs", exist_ok=True)
with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated docs/index.html ({len(html_content)} bytes)")
