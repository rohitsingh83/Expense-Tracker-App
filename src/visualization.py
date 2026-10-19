"""
Publication-quality static charts saved under outputs/charts/.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from .analysis import (
    WEEKDAY_ORDER,
    budget_vs_actual,
    category_breakdown,
    monthly_trend,
    payment_mix,
    top_merchants,
    weekday_pattern,
)
from .config import BRAND, CHART_DIR, CHART_PALETTE
from .insights import inr


def _setup_style() -> None:
    sns.set_theme(style="whitegrid", context="talk")
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#E2E8F0",
            "axes.grid": True,
            "grid.color": "#F1F5F9",
            "grid.linewidth": 0.8,
            "font.size": 11,
            "axes.titlesize": 14,
            "axes.labelsize": 11,
            "axes.titleweight": "bold",
            "axes.titlepad": 12,
            "figure.dpi": 140,
            "savefig.dpi": 160,
            "savefig.bbox": "tight",
            "savefig.facecolor": "white",
        }
    )


def _save(fig: plt.Figure, name: str) -> Path:
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    path = CHART_DIR / name
    fig.savefig(path)
    plt.close(fig)
    return path


def chart_category_bar(df: pd.DataFrame) -> Path:
    cats = category_breakdown(df)
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.barplot(
        data=cats,
        x="Total",
        y="Category",
        hue="Category",
        palette=CHART_PALETTE[: len(cats)],
        dodge=False,
        legend=False,
        ax=ax,
    )
    ax.set_title("Total Spend by Category")
    ax.set_xlabel("Amount (INR)")
    ax.set_ylabel("")
    for i, row in cats.iterrows():
        ax.text(row["Total"] + cats["Total"].max() * 0.01, i, inr(row["Total"]), va="center", fontsize=9)
    fig.tight_layout()
    return _save(fig, "01_category_bar.png")


def chart_category_pie(df: pd.DataFrame) -> Path:
    cats = category_breakdown(df)
    # Group tiny slices
    major = cats[cats["Share_%"] >= 4].copy()
    other = cats[cats["Share_%"] < 4]["Total"].sum()
    if other > 0:
        major = pd.concat(
            [major, pd.DataFrame([{"Category": "Other", "Total": other}])],
            ignore_index=True,
        )
    fig, ax = plt.subplots(figsize=(8.5, 8.5))
    wedges, texts, autotexts = ax.pie(
        major["Total"],
        labels=major["Category"],
        autopct="%1.1f%%",
        startangle=120,
        colors=CHART_PALETTE[: len(major)],
        pctdistance=0.75,
        explode=[0.02] * len(major),
    )
    for t in autotexts:
        t.set_fontsize(9)
        t.set_color("white")
        t.set_fontweight("bold")
    ax.set_title("Expense Distribution by Category")
    fig.tight_layout()
    return _save(fig, "02_category_pie.png")


def chart_monthly_income_expense(df: pd.DataFrame) -> Path:
    monthly = monthly_trend(df)
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.plot(
        monthly["YearMonth"],
        monthly["Income"],
        marker="o",
        linewidth=2.4,
        color=BRAND["income"],
        label="Income",
    )
    ax.plot(
        monthly["YearMonth"],
        monthly["Expense"],
        marker="o",
        linewidth=2.4,
        color=BRAND["expense"],
        label="Expense",
    )
    ax.fill_between(monthly["YearMonth"], monthly["Income"], alpha=0.08, color=BRAND["income"])
    ax.fill_between(monthly["YearMonth"], monthly["Expense"], alpha=0.08, color=BRAND["expense"])
    ax.set_title("Monthly Income vs Expense")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount (INR)")
    ax.legend(frameon=False)
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    return _save(fig, "03_monthly_income_expense.png")


def chart_savings_trend(df: pd.DataFrame) -> Path:
    monthly = monthly_trend(df)
    colors = [BRAND["income"] if v >= 0 else BRAND["expense"] for v in monthly["Net"]]
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.bar(monthly["YearMonth"], monthly["Net"], color=colors, width=0.65)
    ax.axhline(0, color="#94A3B8", linewidth=1)
    ax.set_title("Monthly Net Savings")
    ax.set_xlabel("Month")
    ax.set_ylabel("Net (INR)")
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    return _save(fig, "04_monthly_net_savings.png")


def chart_weekday(df: pd.DataFrame) -> Path:
    wk = weekday_pattern(df)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(
        data=wk,
        x="Weekday",
        y="Total",
        hue="Weekday",
        palette=["#0D9488"] * 5 + ["#E11D48"] * 2,
        dodge=False,
        legend=False,
        ax=ax,
        order=WEEKDAY_ORDER,
    )
    ax.set_title("Spending by Weekday (weekends highlighted)")
    ax.set_xlabel("")
    ax.set_ylabel("Amount (INR)")
    fig.tight_layout()
    return _save(fig, "05_weekday_spend.png")


def chart_payment_mix(df: pd.DataFrame) -> Path:
    mix = payment_mix(df)
    fig, ax = plt.subplots(figsize=(8, 5.5))
    sns.barplot(
        data=mix,
        x="Payment_Method",
        y="Total",
        hue="Payment_Method",
        palette=CHART_PALETTE[: len(mix)],
        dodge=False,
        legend=False,
        ax=ax,
    )
    ax.set_title("Spend by Payment Method")
    ax.set_xlabel("")
    ax.set_ylabel("Amount (INR)")
    fig.tight_layout()
    return _save(fig, "06_payment_method.png")


def chart_budget(df: pd.DataFrame) -> Path:
    b = budget_vs_actual(df)
    fig, ax = plt.subplots(figsize=(11, 6.5))
    y = np.arange(len(b))
    ax.barh(y + 0.18, b["Budget"], height=0.36, color="#CBD5E1", label="Budget")
    colors = [
        BRAND["expense"] if s == "Over budget" else BRAND["primary"] for s in b["Status"]
    ]
    ax.barh(y - 0.18, b["Avg_Monthly_Actual"], height=0.36, color=colors, label="Avg actual")
    ax.set_yticks(y)
    ax.set_yticklabels(b["Category"])
    ax.invert_yaxis()
    ax.set_title("Average Monthly Spend vs Recommended Budget")
    ax.set_xlabel("INR / month")
    ax.legend(frameon=False)
    fig.tight_layout()
    return _save(fig, "07_budget_vs_actual.png")


def chart_top_merchants(df: pd.DataFrame) -> Path:
    m = top_merchants(df, n=10)
    fig, ax = plt.subplots(figsize=(11, 5.5))
    sns.barplot(
        data=m,
        x="Amount",
        y="Merchant",
        hue="Category",
        dodge=False,
        palette="Set2",
        ax=ax,
    )
    ax.set_title("Top 10 Merchants by Spend")
    ax.set_xlabel("Amount (INR)")
    ax.set_ylabel("")
    ax.legend(title="", frameon=False, fontsize=8)
    fig.tight_layout()
    return _save(fig, "08_top_merchants.png")


def chart_heatmap(df: pd.DataFrame) -> Path:
    expense = df[df["Type"] == "Expense"].copy()
    expense["Weekday"] = pd.Categorical(expense["Weekday"], WEEKDAY_ORDER, ordered=True)
    pivot = (
        expense.pivot_table(
            index="Weekday",
            columns="Month_Num",
            values="Amount",
            aggfunc="sum",
            observed=False,
        )
        .reindex(WEEKDAY_ORDER)
    )
    fig, ax = plt.subplots(figsize=(12, 5))
    sns.heatmap(pivot, cmap="YlGnBu", ax=ax, linewidths=0.4, cbar_kws={"label": "INR"})
    ax.set_title("Spend Heatmap — Weekday × Month")
    ax.set_xlabel("Month number")
    ax.set_ylabel("")
    fig.tight_layout()
    return _save(fig, "09_weekday_month_heatmap.png")


def chart_pareto(df: pd.DataFrame) -> Path:
    cats = category_breakdown(df)
    cats = cats.sort_values("Total", ascending=False).reset_index(drop=True)
    cats["cum_pct"] = cats["Total"].cumsum() / cats["Total"].sum() * 100
    fig, ax1 = plt.subplots(figsize=(11, 5.5))
    ax1.bar(cats["Category"], cats["Total"], color=BRAND["primary"])
    ax1.set_ylabel("Amount (INR)")
    ax1.set_xlabel("")
    plt.xticks(rotation=40, ha="right")
    ax2 = ax1.twinx()
    ax2.plot(cats["Category"], cats["cum_pct"], color=BRAND["expense"], marker="o", linewidth=2)
    ax2.axhline(80, color=BRAND["warning"], linestyle="--", linewidth=1, label="80% line")
    ax2.set_ylabel("Cumulative share (%)")
    ax2.set_ylim(0, 105)
    ax1.set_title("Pareto — Which categories drive 80% of spend?")
    fig.tight_layout()
    return _save(fig, "10_pareto.png")


def generate_all_charts(df: pd.DataFrame) -> list[Path]:
    _setup_style()
    paths = [
        chart_category_bar(df),
        chart_category_pie(df),
        chart_monthly_income_expense(df),
        chart_savings_trend(df),
        chart_weekday(df),
        chart_payment_mix(df),
        chart_budget(df),
        chart_top_merchants(df),
        chart_heatmap(df),
        chart_pareto(df),
    ]
    return paths
