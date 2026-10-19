#!/usr/bin/env python3
"""
Expense Tracker App — command-line pipeline.

Usage
-----
    python main.py              # run everything
    python main.py --generate   # synthetic data only
    python main.py --analyze    # clean + analyse existing data
    python main.py --charts     # rebuild charts from cleaned data
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow `python main.py` from the project root without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


from src.analysis import (  # noqa: E402
    budget_vs_actual,
    category_breakdown,
    detect_anomalies,
    financial_health_score,
    forecast_next_month,
    kpis,
    monthly_trend,
)
from src.config import (  # noqa: E402
    CHART_DIR,
    CLEAN_DATA_PATH,
    INSIGHTS_PATH,
    RAW_DATA_PATH,
    REPORT_DIR,
    SUMMARY_PATH,
)
from src.data_generator import save_raw_dataset  # noqa: E402
from src.insights import generate_insights, inr, insights_as_text  # noqa: E402
from src.preprocessing import load_and_clean  # noqa: E402
from src.visualization import generate_all_charts  # noqa: E402


def banner(text: str) -> None:
    print("\n" + "=" * 64)
    print(text)
    print("=" * 64)


def run_generate() -> None:
    banner("PHASE 1 — Generating synthetic expense ledger")
    raw = save_raw_dataset()
    print(f"  rows written : {len(raw)}")
    print(f"  file         : {RAW_DATA_PATH}")
    print("  note         : file is intentionally slightly dirty (missing values,")
    print("                 mixed case, duplicates) so cleaning has real work to do.")


def run_analyze():
    banner("PHASE 2 — Cleaning + feature engineering")
    if not RAW_DATA_PATH.exists():
        print("Raw data missing — generating it first.")
        run_generate()
    df = load_and_clean()
    print(f"  cleaned rows : {len(df)}")
    print(f"  columns      : {list(df.columns)}")
    print(f"  file         : {CLEAN_DATA_PATH}")

    banner("PHASE 3 — Analysis")
    metrics = kpis(df)
    health = financial_health_score(df)
    forecast = forecast_next_month(df)
    cats = category_breakdown(df)
    monthly = monthly_trend(df)
    budget = budget_vs_actual(df)
    anomalies = detect_anomalies(df)

    print(f"  period           : {metrics['date_min'].date()} → {metrics['date_max'].date()}")
    print(f"  total income     : {inr(metrics['total_income'])}")
    print(f"  total expense    : {inr(metrics['total_expense'])}")
    print(f"  net savings      : {inr(metrics['net_savings'])}")
    print(f"  savings rate     : {metrics['savings_rate'] * 100:.1f}%")
    print(f"  avg daily spend  : {inr(metrics['avg_daily_spend'])}")
    print(f"  top category     : {metrics['top_category']} ({inr(metrics['top_category_amount'])})")
    print(f"  health score     : {health['score']}/100 ({health['label']})")
    print(f"  next-month fcst  : {inr(forecast['next_month_expense'])}")
    print(f"  anomalies        : {len(anomalies)}")

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    monthly.to_csv(SUMMARY_PATH, index=False)
    cats.to_csv(REPORT_DIR / "category_breakdown.csv", index=False)
    budget.to_csv(REPORT_DIR / "budget_vs_actual.csv", index=False)
    anomalies.to_csv(REPORT_DIR / "anomalies.csv", index=False)

    banner("PHASE 4 — Insights")
    text = insights_as_text(df)
    INSIGHTS_PATH.write_text(text, encoding="utf-8")
    print(text)
    print(f"  saved → {INSIGHTS_PATH}")
    return df


def run_charts(df=None) -> None:
    banner("PHASE 5 — Visualizations")
    if df is None:
        import pandas as pd

        if not CLEAN_DATA_PATH.exists():
            df = run_analyze()
        else:
            df = pd.read_csv(CLEAN_DATA_PATH, parse_dates=["Date"])
    paths = generate_all_charts(df)
    print(f"  charts written to {CHART_DIR}")
    for p in paths:
        print(f"    • {p.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Expense Tracker App pipeline")
    parser.add_argument("--generate", action="store_true", help="Generate synthetic data only")
    parser.add_argument("--analyze", action="store_true", help="Clean + analyse")
    parser.add_argument("--charts", action="store_true", help="Rebuild charts")
    args = parser.parse_args()

    run_all = not (args.generate or args.analyze or args.charts)
    if args.generate or run_all:
        run_generate()
    df = None
    if args.analyze or run_all:
        df = run_analyze()
    if args.charts or run_all:
        run_charts(df)

    banner("DONE")
    print("  Next:  streamlit run app.py")
    print("  Or:    open outputs/charts/ and outputs/reports/")


if __name__ == "__main__":
    main()
