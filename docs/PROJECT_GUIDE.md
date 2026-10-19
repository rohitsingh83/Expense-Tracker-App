# Expense Tracker App — complete project guide

This document is the full write-up (all 16 sections). **Working code lives in the repo**, not in copy-paste blocks here. Run `python main.py` then `streamlit run app.py`.

---

## 1. Project explanation

### What is an Expense Tracker App?

A system that records money in and money out, groups it (food, rent, travel…), and turns the log into summaries, charts and recommendations.

**Simple view:** a smarter passbook. You see *where* rupees went, not just *that* they left.

**Technical view:** a tabular analytics product. Transactions are facts. Cleaning, dimensional features (time, category, channel), aggregations, variance-to-budget, anomaly scores and a lightweight forecast sit on top. A dashboard is the consumption layer.

### Why it matters

- Households leak 10–20% of spend into unplanned categories without noticing.
- Finance teams waste hours reconciling spreadsheets.
- FinTech apps compete on *insights*, not on the payment rail itself.

The personal-finance software market is still growing (low-single-digit to mid CAGR depending on the report) and the broader FinTech analytics market is much larger. You do not need the exact TAM number in an interview — you need the *use case*.

### Who uses it

| User | What they do with it |
|---|---|
| Individual | Budget, cut delivery, plan a trip |
| Family / roommates | Split and reconcile (Splitwise pattern) |
| SME / startup | Burn monitoring, reimbursements |
| Bank / NBFC | Spend summaries, card insights, early stress signals |
| Accounting firm | Client expense packs |
| FinTech app | In-product “this month vs last month” cards |

Real products with a similar spine: **Mint, Google Pay, PhonePe, CRED, RazorpayX, Splitwise, YNAB**.

### Workflow

```
data input → storage → cleaning → analysis → visualisation → insights → decision
```

Example decision: “Food & Dining is 1.1× groceries. Cook three extra meals a week and the monthly leak closes.”

---

## 2. Tech-stack options

### Option A — Easy
Excel / Google Sheets + pivot tables + pie/bar charts.  
**Difficulty:** low. **Dashboard:** no. ** internships:** weak unless paired with SQL.

### Option B — Intermediate  ← **this repo**
Python, Pandas, NumPy, Matplotlib, Seaborn, Plotly, Streamlit.  
**Difficulty:** medium. **Dashboard:** yes. **Fits:** DA / BA / FA internships.

### Option C — Advanced
Option B + dbt/SQL warehouse + Prophet/ARIMA + bank CSV ingest + auth + Streamlit Cloud / FastAPI.  
**Difficulty:** high. Add *after* Option B runs.

**Best for students:** Option B. You can explain every line. You have a demo URL-quality app. You are not pretending to have a production ML platform on 12 months of fake data.

---

## 3. Architecture

**Input** — date, category, description, merchant, amount, type, payment method.

**Processing** — type coercion, null handling, de-duplication, canonical categories, time features, amount bands, signed cash-flow.

**Output** — KPI pack, category/monthly/weekday tables, budget variance, anomaly list, forecast, health score, 10 PNGs, Streamlit app, `insights.txt`.

```
Persona rules ──► data_generator ──► raw_expenses.csv (dirty)
                                          │
                                          ▼
                                   preprocessing
                                          │
                                          ▼
                               cleaned_expenses.csv
                                /        |         \
                         analysis    insights    visualization
                           │             │              │
                     reports/*.csv  insights.txt   charts/*.png
                           \             |              /
                            \____________|_____________/
                                         ▼
                                      app.py
```

---

## 4. Implementation plan (phase-wise)

| Phase | What | Why | Output | Mistake to avoid |
|---|---|---|---|---|
| 1 Setup | venv, `pip install -r requirements.txt` | Reproducible env | working Python | installing into global Python |
| 2 Data | `python main.py --generate` | Need a ledger | `data/raw_expenses.csv` | using 20 fake rows — too thin for EDA |
| 3 Cleaning | `src/preprocessing.py` | Dirty data is the point | `cleaned_expenses.csv` | dropping nulls *before* inspecting them |
| 4 EDA | groupby / describe / nunique | Understand shape | printed profile | jumping to charts with unclean dates |
| 5 Features | month, weekday, weekend, festival, amount band | Dimensions for cuts | extra columns | leaking future info (none here, but know the idea) |
| 6 Analysis | KPIs, budget, anomalies, forecast | The “so what” | `outputs/reports/` | global z-score (rent always wins) |
| 7 Viz | 10 charts + Plotly | Proof + demo | `outputs/charts/` | default rainbow palettes, no titles |
| 8 Insights | `src/insights.py` | Interview narrative | `insights.txt` | insights that just repeat the chart title |
| 9 GitHub | see `GITHUB_GUIDE.md` | Portfolio | public repo | one 4,000-file commit named `final` |

---

## 5. Folder structure

See root `README.md`. Rule of thumb:

- `src/` — reusable logic (imported by CLI, app, notebook)
- `notebooks/` — explanation for humans
- `data/` — committed synthetic data (this project is not secret)
- `outputs/` — committed artefacts so the README has pictures without re-running
- `docs/` — interview and GitHub notes, not code

---

## 6. Installation guide

**Hardware:** any laptop with 4 GB RAM. Google Colab also works for the notebook path (Streamlit is happier locally).

**Software:** Python 3.10+, pip, Git.

```bash
# Windows (PowerShell)
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Libraries: pandas, numpy, matplotlib, seaborn, plotly, streamlit, openpyxl.

Colab extras (if you only run analysis there):

```python
!pip install pandas numpy matplotlib seaborn plotly openpyxl
```

---

## 7. Full project code

Do not paste 1,500 lines into a report. Point to:

| File | Responsibility |
|---|---|
| `src/config.py` | paths, persona, budgets, colours |
| `src/data_generator.py` | 12-month INR ledger + controlled dirt |
| `src/preprocessing.py` | clean + feature engineering |
| `src/analysis.py` | KPIs, cuts, anomalies, forecast, score |
| `src/insights.py` | English sentences + Indian numbering |
| `src/visualization.py` | 10 matplotlib/seaborn figures |
| `main.py` | CLI orchestrator |
| `app.py` | Streamlit dashboard |
| `notebooks/01_expense_eda.ipynb` | step-by-step EDA |

Every public function has a docstring. Read `preprocessing.clean_expenses` and `analysis.detect_anomalies` before any interview.

---

## 8. Virtual simulation

**Persona:** Arjun Rao, junior data analyst, Kukatpally / Hyderabad. Salary ₹55,000 on the 1st. Rent ₹14,000 on the 2nd.

**How expenses are generated**

1. For each month Nov 2025 → Oct 2026, write salary, rent, insurance, utilities, OTT, learning fee.
2. Sprinkle groceries, dining, transport, shopping, entertainment with a seasonal multiplier (Diwali 1.28×, January 0.88×, …).
3. Weekend dining/entertainment tickets are boosted; weekday transport is higher.
4. Quarterly freelance + interest; random cashback.
5. **Contaminate** ~8% of rows (case, nulls) and duplicate 8 rows.

**Categories:** Rent, Groceries, Food & Dining, Transport, Utilities, Shopping, Entertainment, Healthcare, Education, Subscriptions, Personal Care, Travel, Insurance, Miscellaneous + income (Salary, Freelance, Cashback, Interest).

**How overspending is detected**

- Category monthly average vs `MONTHLY_BUDGETS` in `config.py` (±5% / ±10% bands).
- Modified z-score ≥ 2.5 *inside* a category.
- Savings rate vs 10% / 20% thresholds.

**Simulation steps**

1. `python main.py --generate` → raw CSV  
2. `python main.py --analyze` → cleaned CSV + reports + printed insights  
3. `python main.py --charts` → 10 PNGs  
4. `streamlit run app.py` → filter, screenshot  
5. Commit

**Proof to save:** CLI log, `insights.txt`, all 10 charts, 4–5 dashboard screenshots, `git log`.

---

## 9. How to run

```bash
python main.py                 # everything
python main.py --generate      # data only
python main.py --analyze       # clean + analyse
python main.py --charts        # rebuild PNGs
streamlit run app.py           # dashboard at http://localhost:8501
```

**You should see**

- Income, expense, net, savings rate, health score, forecast in the terminal
- `outputs/reports/monthly_summary.csv`, `category_breakdown.csv`, `budget_vs_actual.csv`, `anomalies.csv`, `insights.txt`
- Dashboard tabs: Overview, Categories, Trends, Budget health, Insights & anomalies, Transactions

---

## 10. GitHub upload

Follow `docs/GITHUB_GUIDE.md`.

- Repo: `Expense-Tracker-App`
- Description: *Data-driven expense tracker: synthetic INR ledger, EDA, budget vs actual, anomaly detection, forecast, Streamlit dashboard.*
- Topics: `data-science` `pandas` `streamlit` `personal-finance` `eda` `python` `fintech`

---

## 11. README

The root `README.md` **is** the GitHub README (overview, problem, solution, features, stack, run, results, chart table). Do not duplicate it.

---

## 12. Proof-building strategy (5 days)

| Day | Work | Commits | Screenshot |
|---|---|---|---|
| 1 | venv, folders, generator | `feat: project skeleton and synthetic generator` | raw CSV preview |
| 2 | cleaning + features | `feat: cleaning pipeline` | before/after null counts |
| 3 | analysis + insights | `feat: KPIs, budget, anomalies, forecast` | terminal KPIs |
| 4 | charts + Streamlit | `feat: visualisations and dashboard` | 3 dashboard shots |
| 5 | README, interview notes, push | `docs: README and interview prep` | GitHub repo page |

Keep `git log --oneline` as an appendix in your internship report.

---

## 13. Screenshots / outputs to capture

- Dataset preview (`df.head()` / Excel)
- Category bar + pie
- Monthly income vs expense
- Net savings bars
- Weekday pattern
- Payment mix
- Budget vs actual
- Pareto
- Heatmap
- Dashboard Overview, Budget, Insights tabs
- Anomaly table
- `insights.txt`

---

## 14. Interview preparation

See `docs/INTERVIEW_PREP.md` (10 core questions + extras, HR and technical answers).

---

## 15. Future improvements

- Mobile / PWA wrapper  
- Real-time: watch a folder of bank CSVs  
- AI: description → category classifier; LLM monthly commentary  
- Budget alerts at 80% of envelope  
- Goal tracking (emergency fund = 6× monthly expense)  
- Bank API (Account Aggregator in India) once you have legal access  
- Multi-user auth

---

## 16. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: pandas` | venv not active | activate `.venv`, re-pip |
| `FileNotFoundError: raw_expenses.csv` | skipped generate | `python main.py --generate` |
| Dates became `NaT` | mixed formats | already handled; if you add a new format, extend `to_datetime` |
| Charts blank / no window | running on a server | pipeline uses `savefig`; don’t `plt.show()` in `main.py` |
| Seaborn `palette` warning | `palette` without `hue` | this repo already passes `hue=` |
| Streamlit not opening | wrong directory | run from project root so `data/` resolves |
| `Address already in use` | port 8501 busy | `streamlit run app.py --server.port 8502` |
| Indian comma format looks wrong | used US `:,` | use `insights.inr()` |
| Dashboard charts unreadable | light Plotly on dark theme | `style_fig()` sets transparent paper + light font |
| Health score 0 | filtered only expenses | health uses income too — set type filter to All |
| Git rejected push | no remote / auth | create repo first, `git remote add origin …` |

Hardware IoT (ESP32 buttons) from some tutorials is **out of scope** here. This is a data-science portfolio piece, not an embedded project. You can mention it as a future “data-capture” idea; do not wire it unless you actually have the board.
