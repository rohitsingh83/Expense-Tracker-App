"""
generate_docs_site.py
Generates a Swiss Modern Minimalist / Monospaced Editorial Dark UI
for Expense-Tracker-App (Khaata · Expense Intelligence).
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

cleaned_df["Date"] = pd.to_datetime(cleaned_df["Date"])
cleaned_df = cleaned_df.sort_values("Date", ascending=False)
sample_txns = cleaned_df.head(60).copy()
sample_txns["Date"] = sample_txns["Date"].dt.strftime("%d %b %Y")

data_payload = {
    "kpis": {
        "total_income": int(cleaned_df[cleaned_df["Type"] == "Income"]["Amount"].sum()),
        "total_expense": int(cleaned_df[cleaned_df["Type"] == "Expense"]["Amount"].sum()),
        "net_savings": int(cleaned_df[cleaned_df["Type"] == "Income"]["Amount"].sum() - cleaned_df[cleaned_df["Type"] == "Expense"]["Amount"].sum()),
        "savings_rate": round((cleaned_df[cleaned_df["Type"] == "Income"]["Amount"].sum() - cleaned_df[cleaned_df["Type"] == "Expense"]["Amount"].sum()) / cleaned_df[cleaned_df["Type"] == "Income"]["Amount"].sum() * 100, 1),
        "health_score": 53,
        "health_label": "Fair",
        "forecast_next_month": 53242,
        "total_txns": len(cleaned_df)
    },
    "monthly": monthly_df.fillna(0).to_dict(orient="records"),
    "categories": cat_df.to_dict(orient="records"),
    "budget": budget_df.to_dict(orient="records"),
    "anomalies": anomalies_df.to_dict(orient="records"),
    "transactions": sample_txns[["Date", "Category", "Description", "Merchant", "Amount", "Type", "Payment_Method"]].to_dict(orient="records")
}

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>KHAATA — Personal Spend Intelligence & Capital Ledger</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=Space+Mono:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    :root {{
      --paper: #131312;
      --card: #1a1a18;
      --card-subtle: #161614;
      --line: #292926;
      --line-subtle: #21211e;
      --ink: #ecece6;
      --ink-muted: #9c9c94;
      --ink-dim: #6e6e66;
      --accent: #8fa4c2;
      --accent-dim: rgba(143, 164, 194, 0.12);
      --green: #88aa80;
      --amber: #d4a373;
      --red: #c97a7e;
      --font-body: 'DM Sans', -apple-system, sans-serif;
      --font-mono: 'Space Mono', monospace;
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      background: var(--paper);
      color: var(--ink);
      font-family: var(--font-body);
      font-size: 14px;
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
    }}

    /* Editorial Masthead */
    .masthead {{
      border-bottom: 1px solid var(--line);
      padding: 1.25rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: var(--paper);
      position: sticky;
      top: 0;
      z-index: 40;
    }}

    .mast-brand {{
      display: flex;
      align-items: baseline;
      gap: 1rem;
    }}

    .mast-title {{
      font-family: var(--font-mono);
      font-size: 0.9375rem;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--ink);
    }}

    .mast-edition {{
      font-family: var(--font-mono);
      font-size: 0.6875rem;
      color: var(--ink-dim);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .mast-links a {{
      font-family: var(--font-mono);
      font-size: 0.75rem;
      color: var(--ink-muted);
      text-decoration: none;
      margin-left: 1.5rem;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }}

    .mast-links a:hover {{ color: var(--ink); }}

    .wrap {{
      max-width: 1280px;
      margin: 0 auto;
      padding: 2.5rem 2rem 5rem;
    }}

    /* Editorial Headline Block */
    .hero-lead {{
      border-bottom: 1px solid var(--line);
      padding-bottom: 2rem;
      margin-bottom: 2.5rem;
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 3rem;
      align-items: end;
    }}

    @media (max-width: 850px) {{
      .hero-lead {{ grid-template-columns: 1fr; gap: 1.5rem; }}
    }}

    .hero-lead h1 {{
      font-size: 2.1rem;
      font-weight: 400;
      letter-spacing: -0.02em;
      color: var(--ink);
      line-height: 1.25;
    }}

    .hero-lead h1 strong {{
      font-weight: 600;
      color: #ffffff;
    }}

    .hero-meta-panel {{
      font-family: var(--font-mono);
      font-size: 0.75rem;
      color: var(--ink-muted);
      border-left: 1px solid var(--line);
      padding-left: 1.5rem;
      line-height: 1.8;
    }}

    /* Key Numbers Grid */
    .stats-row {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      border-top: 1px solid var(--line);
      border-bottom: 1px solid var(--line);
      margin-bottom: 3rem;
    }}

    @media (max-width: 850px) {{
      .stats-row {{ grid-template-columns: repeat(2, 1fr); }}
    }}

    .stat-cell {{
      padding: 1.25rem 1.5rem;
      border-right: 1px solid var(--line);
    }}

    .stat-cell:last-child {{ border-right: none; }}

    .stat-label {{
      font-family: var(--font-mono);
      font-size: 0.6875rem;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--ink-dim);
      margin-bottom: 0.35rem;
    }}

    .stat-val {{
      font-family: var(--font-mono);
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--ink);
      letter-spacing: -0.02em;
    }}

    .stat-sub {{
      font-size: 0.75rem;
      color: var(--ink-muted);
      margin-top: 0.2rem;
    }}

    /* Main Two-Column Layout */
    .col-split {{
      display: grid;
      grid-template-columns: 1fr 1.35fr;
      gap: 3rem;
      margin-bottom: 3.5rem;
    }}

    @media (max-width: 950px) {{
      .col-split {{ grid-template-columns: 1fr; gap: 2rem; }}
    }}

    .section-tag {{
      font-family: var(--font-mono);
      font-size: 0.6875rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--ink-dim);
      margin-bottom: 0.5rem;
      display: block;
    }}

    .panel-header {{
      font-size: 1.05rem;
      font-weight: 600;
      margin-bottom: 1.25rem;
      padding-bottom: 0.5rem;
      border-bottom: 1px solid var(--line);
      display: flex;
      justify-content: space-between;
      align-items: baseline;
    }}

    /* Minimal Lever Adjuster */
    .lever-card {{
      background: var(--card-subtle);
      border: 1px solid var(--line);
      padding: 1.5rem;
      margin-bottom: 2rem;
    }}

    .lever-row {{
      margin-bottom: 1.25rem;
    }}

    .lever-label-row {{
      display: flex;
      justify-content: space-between;
      font-family: var(--font-mono);
      font-size: 0.75rem;
      margin-bottom: 0.4rem;
    }}

    .lever-label-row span:first-child {{ color: var(--ink-muted); }}
    .lever-label-row span:last-child {{ color: var(--ink); }}

    input[type=range] {{
      -webkit-appearance: none;
      width: 100%;
      height: 2px;
      background: var(--line);
      outline: none;
    }}

    input[type=range]::-webkit-slider-thumb {{
      -webkit-appearance: none;
      width: 12px;
      height: 12px;
      border-radius: 0;
      background: var(--ink);
      cursor: pointer;
    }}

    .lever-output {{
      border-top: 1px dashed var(--line);
      padding-top: 1rem;
      margin-top: 1.25rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .output-num {{
      font-family: var(--font-mono);
      font-size: 1.35rem;
      font-weight: 700;
      color: var(--green);
    }}

    /* Category Meters */
    .cat-item {{
      margin-bottom: 0.85rem;
    }}

    .cat-header {{
      display: flex;
      justify-content: space-between;
      font-size: 0.8125rem;
      margin-bottom: 0.25rem;
    }}

    .cat-bar {{
      height: 4px;
      background: var(--card);
      border-radius: 2px;
      overflow: hidden;
    }}

    .cat-fill {{
      height: 100%;
      background: var(--accent);
    }}

    /* Ledger Table */
    .ledger-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.8125rem;
    }}

    .ledger-table th {{
      font-family: var(--font-mono);
      font-size: 0.6875rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--ink-dim);
      font-weight: 400;
      padding: 0.6rem 0.5rem;
      border-bottom: 1px solid var(--line);
      text-align: left;
    }}

    .ledger-table td {{
      padding: 0.65rem 0.5rem;
      border-bottom: 1px solid var(--line-subtle);
      color: var(--ink-muted);
    }}

    .ledger-table tr:hover td {{
      color: var(--ink);
      background: rgba(255,255,255,0.015);
    }}

    .amount-debit {{
      font-family: var(--font-mono);
      color: var(--ink);
      text-align: right;
    }}

    .amount-credit {{
      font-family: var(--font-mono);
      color: var(--green);
      text-align: right;
    }}

    footer {{
      border-top: 1px solid var(--line);
      padding-top: 2rem;
      font-family: var(--font-mono);
      font-size: 0.6875rem;
      color: var(--ink-dim);
      display: flex;
      justify-content: space-between;
    }}
  </style>
</head>
<body>

  <header class="masthead">
    <div class="mast-brand">
      <span class="mast-title">Khaata</span>
      <span class="mast-edition">Issue 04 &bull; Spend Intelligence & Surplus Ledger</span>
    </div>
    <div class="mast-links">
      <a href="#cashflow">Flow</a>
      <a href="#planner">Planner</a>
      <a href="#ledger">Transactions</a>
      <a href="https://github.com/rohitsingh83/Expense-Tracker-App" target="_blank">Repository ↗</a>
    </div>
  </header>

  <div class="wrap">
    <div class="hero-lead">
      <div>
        <span class="section-tag">Audit Period: 01 Nov 2025 → 15 Oct 2026</span>
        <h1>Personal wealth isn't made in gross earnings — it's preserved in <strong>outflow discipline</strong> and <strong>leak detection</strong>.</h1>
      </div>
      <div class="hero-meta-panel">
        <div>SUBJECT: Arjun Rao</div>
        <div>ROLE: Junior Data Analyst, Hyderabad</div>
        <div>LEDGER ENTRIES: {data_payload["kpis"]["total_txns"]} audited</div>
        <div>INTELLIGENCE: Anomaly radar + 30d forecast</div>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="stats-row">
      <div class="stat-cell">
        <div class="stat-label">Total Inflows (12m)</div>
        <div class="stat-val">₹{data_payload["kpis"]["total_income"]:,}</div>
        <div class="stat-sub">Across 12 cycles & salary credits</div>
      </div>
      <div class="stat-cell">
        <div class="stat-label">Total Outflows (12m)</div>
        <div class="stat-val">₹{data_payload["kpis"]["total_expense"]:,}</div>
        <div class="stat-sub">Across 9 spending categories</div>
      </div>
      <div class="stat-cell">
        <div class="stat-label">Net Surplus Capital</div>
        <div class="stat-val" style="color: var(--green);">₹{data_payload["kpis"]["net_savings"]:,}</div>
        <div class="stat-sub">Effective savings rate: {data_payload["kpis"]["savings_rate"]}%</div>
      </div>
      <div class="stat-cell">
        <div class="stat-label">Health Score</div>
        <div class="stat-val" style="color: var(--amber);">{data_payload["kpis"]["health_score"]}<span style="font-size:0.9rem; font-weight:400; color:var(--ink-dim);">/100</span></div>
        <div class="stat-sub">Rating: Fair (Emergency buffer &lt; 2 mo)</div>
      </div>
    </div>

    <!-- Editorial Two Column Split -->
    <div class="col-split">
      <!-- Left Column: What-If Levers & Category Weightings -->
      <div>
        <span class="section-tag">Interactive Optimisation</span>
        <div class="panel-header">
          <span>What-If Budget Balancer</span>
          <span style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--ink-dim);">SIMULATOR</span>
        </div>

        <div class="lever-card" id="planner">
          <div class="lever-row">
            <div class="lever-label-row">
              <span>Food & Delivery Outflow Cut:</span>
              <span id="txt-food">0%</span>
            </div>
            <input type="range" id="rng-food" min="0" max="50" step="5" value="0" oninput="runLever()">
          </div>

          <div class="lever-row">
            <div class="lever-label-row">
              <span>Shopping Discretionary Trim:</span>
              <span id="txt-shop">0%</span>
            </div>
            <input type="range" id="rng-shop" min="0" max="60" step="5" value="0" oninput="runLever()">
          </div>

          <div class="lever-row">
            <div class="lever-label-row">
              <span>Entertainment & Movies:</span>
              <span id="txt-ent">0%</span>
            </div>
            <input type="range" id="rng-ent" min="0" max="50" step="5" value="0" oninput="runLever()">
          </div>

          <div class="lever-row">
            <div class="lever-label-row">
              <span>Unused Subscriptions Cancelled:</span>
              <span id="txt-sub">₹0</span>
            </div>
            <input type="range" id="rng-sub" min="0" max="1000" step="100" value="0" oninput="runLever()">
          </div>

          <div class="lever-output">
            <div>
              <div style="font-family: var(--font-mono); font-size: 0.6875rem; text-transform: uppercase; color: var(--ink-dim);">Extra Annual Wealth</div>
              <div class="output-num" id="out-wealth">+₹0 / yr</div>
            </div>
            <div style="text-align: right;">
              <div style="font-family: var(--font-mono); font-size: 0.6875rem; text-transform: uppercase; color: var(--ink-dim);">Projected Savings Rate</div>
              <div style="font-family: var(--font-mono); font-size: 1.15rem; color: var(--accent); font-weight: 700;" id="out-rate">7.7%</div>
            </div>
          </div>
        </div>

        <span class="section-tag">Category Outflow Volume</span>
        <div class="panel-header">
          <span>Major Expense Concentrations</span>
          <span style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--ink-dim);">TOP 5</span>
        </div>
        <div id="cat-meters-box">
          <!-- populated by JS -->
        </div>
      </div>

      <!-- Right Column: Flow Chart & Ledger -->
      <div>
        <span class="section-tag" id="cashflow">Velocity & Trends</span>
        <div class="panel-header">
          <span>Monthly Cash Flow Velocity</span>
          <span style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--ink-dim);">INR</span>
        </div>
        <div id="plot-flow" style="width: 100%; height: 280px; margin-bottom: 2rem;"></div>

        <span class="section-tag" id="ledger">Chronological Ledger</span>
        <div class="panel-header">
          <span>Latest Transactions</span>
          <input type="text" id="srch-ledger" placeholder="Search merchant..." style="background: transparent; border: 1px solid var(--line); color: var(--ink); font-family: var(--font-mono); font-size: 0.6875rem; padding: 0.2rem 0.5rem; width: 150px;" oninput="filterLedger()">
        </div>
        <div style="overflow-x: auto; max-height: 400px;">
          <table class="ledger-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Category</th>
                <th>Description</th>
                <th>Merchant</th>
                <th style="text-align: right;">Amount</th>
              </tr>
            </thead>
            <tbody id="tbl-ledger"></tbody>
          </table>
        </div>
      </div>
    </div>

    <footer>
      <span>KHAATA // Personal Spend Intelligence Suite &bull; Rohit Singh</span>
      <span>Hosted on GitHub Pages &bull; DM Sans + Space Mono</span>
    </footer>
  </div>

  <script>
    const DATA = {json.dumps(data_payload)};

    // Plot Flow
    const months = DATA.monthly.map(m => m.YearMonth.replace('2025-', "'25-").replace('2026-', "'26-"));
    const inc = DATA.monthly.map(m => m.Income);
    const exp = DATA.monthly.map(m => m.Expense);

    Plotly.newPlot('plot-flow', [
      {{ x: months, y: inc, name: 'Inflow', type: 'bar', marker: {{ color: '#88aa80' }} }},
      {{ x: months, y: exp, name: 'Outflow', type: 'bar', marker: {{ color: '#c97a7e' }} }}
    ], {{
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: {{ color: '#9c9c94', family: 'Space Mono', size: 10 }},
      margin: {{ l: 40, r: 10, t: 10, b: 35 }},
      barmode: 'group',
      bargap: 0.25,
      yaxis: {{ gridcolor: '#21211e', zerolinecolor: '#292926' }},
      xaxis: {{ gridcolor: 'transparent' }},
      legend: {{ orientation: 'h', y: 1.15 }}
    }}, {{ responsive: true, displayModeBar: false }});

    // Populate Category Meters
    const catBox = document.getElementById('cat-meters-box');
    const totExpense = DATA.kpis.total_expense;
    DATA.categories.slice(0, 5).forEach(c => {{
      const pct = (c.Total_Amount / totExpense * 100).toFixed(1);
      const div = document.createElement('div');
      div.className = 'cat-item';
      div.innerHTML = `
        <div class="cat-header">
          <span style="font-weight:500;">${{c.Category}}</span>
          <span style="font-family:var(--font-mono); color:var(--ink-muted);">₹${{c.Total_Amount.toLocaleString()}} (${{pct}}%)</span>
        </div>
        <div class="cat-bar">
          <div class="cat-fill" style="width: ${{pct}}%;"></div>
        </div>
      `;
      catBox.appendChild(div);
    }});

    // Populate Ledger
    const tbLedger = document.getElementById('tbl-ledger');
    function renderLedger(items) {{
      tbLedger.innerHTML = '';
      items.forEach(t => {{
        const tr = document.createElement('tr');
        const isInc = t.Type === 'Income';
        tr.innerHTML = `
          <td style="font-family:var(--font-mono); font-size:0.75rem;">${{t.Date}}</td>
          <td><span style="font-family:var(--font-mono); font-size:0.6875rem; text-transform:uppercase; color:var(--ink-dim);">${{t.Category}}</span></td>
          <td>${{t.Description}}</td>
          <td>${{t.Merchant}}</td>
          <td class="${{isInc ? 'amount-credit' : 'amount-debit'}}">${{isInc ? '+' : '-'}}₹${{t.Amount.toLocaleString()}}</td>
        `;
        tbLedger.appendChild(tr);
      }});
    }}
    renderLedger(DATA.transactions);

    function filterLedger() {{
      const q = document.getElementById('srch-ledger').value.toLowerCase();
      const filtered = DATA.transactions.filter(t => 
        t.Merchant.toLowerCase().includes(q) ||
        t.Category.toLowerCase().includes(q) ||
        t.Description.toLowerCase().includes(q)
      );
      renderLedger(filtered);
    }}

    function runLever() {{
      const foodP = parseInt(document.getElementById('rng-food').value);
      const shopP = parseInt(document.getElementById('rng-shop').value);
      const entP = parseInt(document.getElementById('rng-ent').value);
      const subA = parseInt(document.getElementById('rng-sub').value);

      document.getElementById('txt-food').innerText = foodP + '%';
      document.getElementById('txt-shop').innerText = shopP + '%';
      document.getElementById('txt-ent').innerText = entP + '%';
      document.getElementById('txt-sub').innerText = '₹' + subA;

      const foodSave = Math.round(7078 * (foodP / 100));
      const shopSave = Math.round(6335 * (shopP / 100));
      const entSave = Math.round(3200 * (entP / 100));

      const monthlyExtra = foodSave + shopSave + entSave + subA;
      const annualExtra = monthlyExtra * 12;
      const newMonthlySavings = 4514 + monthlyExtra;
      const newRate = ((newMonthlySavings / 58870) * 100).toFixed(1);

      document.getElementById('out-wealth').innerText = '+₹' + annualExtra.toLocaleString() + ' / yr';
      document.getElementById('out-rate').innerText = newRate + '%';
    }}

    runLever();
  </script>
</body>
</html>
"""

os.makedirs("docs", exist_ok=True)
with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated distinct Swiss-Editorial docs/index.html ({len(html_content)} bytes)")
