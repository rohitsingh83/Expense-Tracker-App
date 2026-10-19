"""
Core analytics: aggregations, trends, anomalies, forecast, health score.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import MONTHLY_BUDGETS, SAVINGS_RATE_HEALTHY, SAVINGS_RATE_OK


WEEKDAY_ORDER = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
MONTH_ORDER = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def split_types(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    return df[df["Type"] == "Income"].copy(), df[df["Type"] == "Expense"].copy()


def kpis(df: pd.DataFrame) -> dict:
    income, expense = split_types(df)
    total_income = float(income["Amount"].sum())
    total_expense = float(expense["Amount"].sum())
    net = total_income - total_expense
    savings_rate = (net / total_income) if total_income else 0.0
    n_days = max((df["Date"].max() - df["Date"].min()).days, 1)
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "net_savings": net,
        "savings_rate": savings_rate,
        "txn_count": int(len(df)),
        "expense_count": int(len(expense)),
        "income_count": int(len(income)),
        "avg_daily_spend": total_expense / n_days,
        "avg_expense_txn": float(expense["Amount"].mean()) if len(expense) else 0.0,
        "median_expense_txn": float(expense["Amount"].median()) if len(expense) else 0.0,
        "top_category": (
            expense.groupby("Category")["Amount"].sum().idxmax() if len(expense) else "—"
        ),
        "top_category_amount": (
            float(expense.groupby("Category")["Amount"].sum().max()) if len(expense) else 0.0
        ),
        "date_min": df["Date"].min(),
        "date_max": df["Date"].max(),
        "n_days": n_days,
    }


def category_breakdown(df: pd.DataFrame, txn_type: str = "Expense") -> pd.DataFrame:
    sub = df[df["Type"] == txn_type]
    out = (
        sub.groupby("Category", as_index=False)["Amount"]
        .agg(Total="sum", Transactions="count", Average="mean", Median="median")
        .sort_values("Total", ascending=False)
    )
    out["Share_%"] = out["Total"] / out["Total"].sum() * 100
    return out.reset_index(drop=True)


def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby(["YearMonth", "Type"], as_index=False)["Amount"]
        .sum()
        .pivot(index="YearMonth", columns="Type", values="Amount")
        .fillna(0)
        .reset_index()
        .sort_values("YearMonth")
    )
    if "Income" not in grouped.columns:
        grouped["Income"] = 0.0
    if "Expense" not in grouped.columns:
        grouped["Expense"] = 0.0
    grouped["Net"] = grouped["Income"] - grouped["Expense"]
    grouped["Savings_Rate_%"] = np.where(
        grouped["Income"] > 0, grouped["Net"] / grouped["Income"] * 100, 0.0
    )
    grouped["Expense_MoM_%"] = grouped["Expense"].pct_change() * 100
    grouped["Income_MoM_%"] = grouped["Income"].pct_change() * 100
    return grouped


def weekday_pattern(df: pd.DataFrame) -> pd.DataFrame:
    expense = df[df["Type"] == "Expense"]
    out = (
        expense.groupby("Weekday", as_index=False)["Amount"]
        .agg(Total="sum", Transactions="count", Average="mean")
    )
    out["Weekday"] = pd.Categorical(out["Weekday"], WEEKDAY_ORDER, ordered=True)
    return out.sort_values("Weekday").reset_index(drop=True)


def payment_mix(df: pd.DataFrame) -> pd.DataFrame:
    expense = df[df["Type"] == "Expense"]
    out = (
        expense.groupby("Payment_Method", as_index=False)["Amount"]
        .agg(Total="sum", Transactions="count")
        .sort_values("Total", ascending=False)
    )
    out["Share_%"] = out["Total"] / out["Total"].sum() * 100
    return out.reset_index(drop=True)


def top_merchants(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    expense = df[df["Type"] == "Expense"]
    return (
        expense.groupby(["Merchant", "Category"], as_index=False)["Amount"]
        .sum()
        .sort_values("Amount", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )


def budget_vs_actual(df: pd.DataFrame, budgets: dict | None = None) -> pd.DataFrame:
    """Compare average monthly spend vs recommended budget for each category."""
    budgets = budgets or MONTHLY_BUDGETS
    expense = df[df["Type"] == "Expense"]
    n_months = max(expense["YearMonth"].nunique(), 1)
    actual = (
        expense.groupby("Category")["Amount"].sum() / n_months
    ).rename("Avg_Monthly_Actual")
    out = pd.DataFrame({"Category": list(budgets.keys())})
    out["Budget"] = out["Category"].map(budgets)
    out = out.merge(actual, on="Category", how="left").fillna({"Avg_Monthly_Actual": 0.0})
    out["Variance"] = out["Budget"] - out["Avg_Monthly_Actual"]
    out["Variance_%"] = np.where(out["Budget"] > 0, out["Variance"] / out["Budget"] * 100, 0.0)
    out["Status"] = np.where(
        out["Avg_Monthly_Actual"] > out["Budget"] * 1.05,
        "Over budget",
        np.where(out["Avg_Monthly_Actual"] > out["Budget"] * 0.9, "Near limit", "Within budget"),
    )
    return out.sort_values("Avg_Monthly_Actual", ascending=False).reset_index(drop=True)


def detect_anomalies(df: pd.DataFrame, z_thresh: float = 2.5) -> pd.DataFrame:
    """Flag unusually large expenses within each category (modified z-score)."""
    expense = df[df["Type"] == "Expense"].copy()
    parts = []
    for _, grp in expense.groupby("Category"):
        if len(grp) < 4:
            continue
        median = grp["Amount"].median()
        mad = (grp["Amount"] - median).abs().median()
        if mad == 0:
            continue
        scores = 0.6745 * (grp["Amount"] - median) / mad
        flagged = grp[scores.abs() >= z_thresh].copy()
        flagged["Anomaly_Score"] = scores.loc[flagged.index]
        parts.append(flagged)
    if not parts:
        return expense.iloc[0:0]
    out = pd.concat(parts).sort_values("Amount", ascending=False)
    return out[
        [
            "Date",
            "Category",
            "Description",
            "Merchant",
            "Amount",
            "Payment_Method",
            "Anomaly_Score",
        ]
    ].reset_index(drop=True)


def forecast_next_month(df: pd.DataFrame) -> dict:
    """Simple linear-trend forecast of next month's total expense."""
    monthly = monthly_trend(df)
    y = monthly["Expense"].to_numpy(dtype=float)
    if len(y) < 3:
        pred = float(y.mean()) if len(y) else 0.0
        return {"next_month_expense": pred, "method": "mean", "n_months": len(y)}
    x = np.arange(len(y), dtype=float)
    slope, intercept = np.polyfit(x, y, 1)
    linear_pred = float(intercept + slope * len(y))
    ma_pred = float(y[-3:].mean())
    # Blend linear trend with a 3-month moving average (stable for noisy spend)
    pred = max(0.0, 0.4 * linear_pred + 0.6 * ma_pred)
    return {
        "next_month_expense": pred,
        "linear_pred": linear_pred,
        "ma3_pred": ma_pred,
        "slope_per_month": float(slope),
        "method": "0.4*linear + 0.6*MA3",
        "n_months": len(y),
        "last_month_expense": float(y[-1]),
    }


def financial_health_score(df: pd.DataFrame) -> dict:
    """
    0–100 score combining savings rate, budget discipline, and spend stability.
    """
    metrics = kpis(df)
    budget = budget_vs_actual(df)
    monthly = monthly_trend(df)

    # Savings component (40 pts)
    sr = metrics["savings_rate"]
    if sr >= SAVINGS_RATE_HEALTHY:
        savings_pts = 40
    elif sr >= SAVINGS_RATE_OK:
        savings_pts = 25 + 15 * (sr - SAVINGS_RATE_OK) / (SAVINGS_RATE_HEALTHY - SAVINGS_RATE_OK)
    elif sr >= 0:
        savings_pts = 25 * (sr / SAVINGS_RATE_OK)
    else:
        savings_pts = 0

    # Budget discipline (35 pts) — share of categories within budget
    within = (budget["Status"] == "Within budget").mean() if len(budget) else 0
    budget_pts = 35 * within

    # Stability (25 pts) — lower month-to-month expense volatility is better
    if len(monthly) >= 3:
        cv = monthly["Expense"].std() / monthly["Expense"].mean()
        stability_pts = float(np.clip(25 * (1 - cv), 0, 25))
    else:
        stability_pts = 12.0

    score = int(round(savings_pts + budget_pts + stability_pts))
    if score >= 80:
        label = "Excellent"
    elif score >= 65:
        label = "Good"
    elif score >= 50:
        label = "Fair"
    else:
        label = "Needs attention"

    return {
        "score": int(np.clip(score, 0, 100)),
        "label": label,
        "savings_points": round(savings_pts, 1),
        "budget_points": round(budget_pts, 1),
        "stability_points": round(stability_pts, 1),
    }


def weekend_vs_weekday(df: pd.DataFrame) -> dict:
    expense = df[df["Type"] == "Expense"]
    wknd = expense[expense["Is_Weekend"]]["Amount"]
    wkdy = expense[~expense["Is_Weekend"]]["Amount"]
    return {
        "weekend_total": float(wknd.sum()),
        "weekday_total": float(wkdy.sum()),
        "weekend_avg_txn": float(wknd.mean()) if len(wknd) else 0.0,
        "weekday_avg_txn": float(wkdy.mean()) if len(wkdy) else 0.0,
        "weekend_txn": int(len(wknd)),
        "weekday_txn": int(len(wkdy)),
    }
