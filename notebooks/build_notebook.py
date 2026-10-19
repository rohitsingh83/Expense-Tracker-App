"""Build notebooks/01_expense_eda.ipynb (run from project root)."""

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parent.parent
nb = nbf.v4.new_notebook()
nb["metadata"] = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "pygments_lexer": "ipython3"},
}

cells = []


def md(text: str) -> None:
    cells.append(nbf.v4.new_markdown_cell(text))


def code(text: str) -> None:
    cells.append(nbf.v4.new_code_cell(text))


md(
    """# Expense Tracker App — EDA notebook

**Project:** Expense Tracker App using Data Science  
**Persona:** Arjun Rao, Junior Data Analyst, Hyderabad  
**Window:** Nov 2025 – Oct 2026 (synthetic INR ledger)

This notebook is the *explain-out-loud* version of `src/`. The production pipeline is `python main.py`; the interactive demo is `streamlit run app.py`.

**Run order:** execute `python main.py` once so `data/` and `outputs/` exist, then run all cells.
"""
)

md(
    """## 0. Setup
"""
)

code(
    """import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT))

from src.analysis import (
    budget_vs_actual,
    category_breakdown,
    detect_anomalies,
    financial_health_score,
    forecast_next_month,
    kpis,
    monthly_trend,
    payment_mix,
    weekday_pattern,
)
from src.config import CLEAN_DATA_PATH, RAW_DATA_PATH
from src.insights import generate_insights, inr

sns.set_theme(style="whitegrid")
pd.set_option("display.max_columns", 30)
pd.set_option("display.float_format", lambda x: f"{x:,.2f}")
print("Project root:", ROOT)
print("Raw exists   :", RAW_DATA_PATH.exists())
print("Clean exists :", CLEAN_DATA_PATH.exists())
"""
)

md(
    """## 1. Inspect the raw (dirty) extract

The generator writes a *deliberately messy* CSV: mixed category case, nulls, duplicate rows. Always look before you clean.
"""
)

code(
    """raw = pd.read_csv(RAW_DATA_PATH)
print("Shape:", raw.shape)
print("\\nDtypes:\\n", raw.dtypes)
print("\\nNulls:\\n", raw.isnull().sum())
print("\\nDuplicate rows:", int(raw.duplicated().sum()))
print("\\nRaw category values (including noise):")
print(raw["Category"].dropna().unique()[:25])
raw.head(8)
"""
)

md(
    """## 2. Load the cleaned ledger

Cleaning lives in `src/preprocessing.py`: date parse, numeric coerce, canonical categories, drop critical-nulls, de-duplicate, then feature engineering.
"""
)

code(
    """df = pd.read_csv(CLEAN_DATA_PATH, parse_dates=["Date"])
print("Cleaned shape:", df.shape)
print("Period:", df["Date"].min().date(), "→", df["Date"].max().date())
print("Columns:", list(df.columns))
print("\\nType split:\\n", df["Type"].value_counts())
print("\\nCategories:\\n", df["Category"].value_counts())
df.head()
"""
)

md(
    """## 3. Headline KPIs

These are the four numbers you should be able to quote in an interview without opening a laptop.
"""
)

code(
    """m = kpis(df)
health = financial_health_score(df)
fc = forecast_next_month(df)

print(f"Income        : {inr(m['total_income'])}")
print(f"Expense       : {inr(m['total_expense'])}")
print(f"Net savings   : {inr(m['net_savings'])}")
print(f"Savings rate  : {m['savings_rate']*100:.1f}%")
print(f"Avg daily     : {inr(m['avg_daily_spend'])}")
print(f"Top category  : {m['top_category']} ({inr(m['top_category_amount'])})")
print(f"Health score  : {health['score']}/100 ({health['label']})")
print(f"Next month    : {inr(fc['next_month_expense'])}  [{fc['method']}]")
"""
)

md(
    """## 4. Category analysis
"""
)

code(
    """cats = category_breakdown(df)
display(cats)

fig, ax = plt.subplots(figsize=(10, 5))
sns.barplot(data=cats, x="Total", y="Category", ax=ax, color="#0D9488")
ax.set_title("Total spend by category")
ax.set_xlabel("INR")
plt.tight_layout()
plt.show()
"""
)

md(
    """## 5. Monthly income vs expense
"""
)

code(
    """monthly = monthly_trend(df)
display(monthly)

fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(monthly["YearMonth"], monthly["Income"], marker="o", label="Income", color="#16A34A")
ax.plot(monthly["YearMonth"], monthly["Expense"], marker="o", label="Expense", color="#E11D48")
ax.set_title("Monthly income vs expense")
ax.set_ylabel("INR")
plt.xticks(rotation=45, ha="right")
ax.legend()
plt.tight_layout()
plt.show()
"""
)

md(
    """## 6. Behaviour cuts — weekday & payment method
"""
)

code(
    """display(weekday_pattern(df))
display(payment_mix(df))
"""
)

md(
    """## 7. Budget vs actual

Recommended monthly envelopes live in `src/config.py` (`MONTHLY_BUDGETS`). Status bands: over (>105%), near (90–105%), within.
"""
)

code(
    """budget = budget_vs_actual(df)
display(budget)
print("Over budget:", budget.loc[budget["Status"] == "Over budget", "Category"].tolist())
"""
)

md(
    """## 8. Anomalies (modified z-score within category)

A *global* z-score would flag rent every month. We score inside each category using median absolute deviation.
"""
)

code(
    """anoms = detect_anomalies(df)
print(f"{len(anoms)} unusual expense(s)")
anoms
"""
)

md(
    """## 9. Auto-generated narrative insights

This is the text that goes into `outputs/reports/insights.txt` and the Insights tab of the dashboard.
"""
)

code(
    """for i, line in enumerate(generate_insights(df), start=1):
    print(f"{i}. {line}")
"""
)

md(
    """## 10. How this maps to a real FinTech job

| This project | Bank / app analogue |
|---|---|
| `raw_expenses.csv` | Card / UPI / CBS extract |
| `preprocessing.py` | dbt staging model |
| Category + Pareto | Share-of-wallet report |
| Budget vs actual | Envelope / MCC limits |
| Modified z-score | Transaction monitoring (simplified) |
| Linear+MA3 forecast | Next-month spend card |
| Streamlit | Internal Looker / in-app insight |

Next steps if you extend the repo: ingest a real GPay/HDFC CSV, add a description→category classifier, deploy the app to Streamlit Cloud.
"""
)

nb["cells"] = cells
out = ROOT / "notebooks" / "01_expense_eda.ipynb"
out.write_text(nbf.writes(nb), encoding="utf-8")
print("Wrote", out)
