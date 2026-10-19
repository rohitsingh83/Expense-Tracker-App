"""
Narrative insight generator — the "so what" layer recruiters look for.
"""

from __future__ import annotations

from .analysis import (
    budget_vs_actual,
    category_breakdown,
    detect_anomalies,
    financial_health_score,
    forecast_next_month,
    kpis,
    monthly_trend,
    weekend_vs_weekday,
)
from .config import PERSONA


def inr(n: float) -> str:
    n = int(round(n))
    sign = "-" if n < 0 else ""
    s = str(abs(n))
    if len(s) <= 3:
        body = s
    else:
        body = s[-3:]
        s = s[:-3]
        while s:
            body = s[-2:] + "," + body
            s = s[:-2]
    return f"{sign}₹{body}"


def pct(n: float) -> str:
    return f"{n:.1f}%"


def generate_insights(df) -> list[str]:
    metrics = kpis(df)
    cats = category_breakdown(df)
    monthly = monthly_trend(df)
    budget = budget_vs_actual(df)
    health = financial_health_score(df)
    forecast = forecast_next_month(df)
    wk = weekend_vs_weekday(df)
    anomalies = detect_anomalies(df)

    insights: list[str] = []

    insights.append(
        f"{PERSONA['name']} ({PERSONA['role']}, {PERSONA['city']}) recorded "
        f"{metrics['txn_count']} transactions between "
        f"{metrics['date_min'].strftime('%d %b %Y')} and "
        f"{metrics['date_max'].strftime('%d %b %Y')}."
    )

    insights.append(
        f"Total inflows {inr(metrics['total_income'])} vs outflows "
        f"{inr(metrics['total_expense'])} → net savings {inr(metrics['net_savings'])} "
        f"({pct(metrics['savings_rate'] * 100)} savings rate)."
    )

    if metrics["savings_rate"] >= 0.20:
        insights.append(
            "Savings rate is at or above the 20% thumb-rule used by certified financial planners — keep this up."
        )
    elif metrics["savings_rate"] >= 0.10:
        insights.append(
            "Savings rate is positive but below the 20% healthy benchmark. Trimming the top two variable categories would close the gap."
        )
    else:
        insights.append(
            "Savings rate is below 10%. This is the primary risk: a single unplanned expense (medical / travel) would wipe out the buffer."
        )

    if len(cats):
        top = cats.iloc[0]
        second = cats.iloc[1] if len(cats) > 1 else None
        insights.append(
            f"Largest expense category is {top['Category']} at {inr(top['Total'])} "
            f"({pct(top['Share_%'])} of all spending, {int(top['Transactions'])} transactions)."
        )
        if second is not None:
            insights.append(
                f"Next is {second['Category']} at {inr(second['Total'])} ({pct(second['Share_%'])}). "
                f"Together the top two categories consume {pct(top['Share_%'] + second['Share_%'])} of outflow."
            )

    over = budget[budget["Status"] == "Over budget"]
    if len(over):
        names = ", ".join(over["Category"].tolist())
        leak = over["Variance"].abs().sum()
        insights.append(
            f"{len(over)} categor{'y is' if len(over) == 1 else 'ies are'} over the recommended monthly budget "
            f"({names}). Combined monthly leak: {inr(leak)}."
        )
    else:
        insights.append("Every expense category is within (or very near) its recommended monthly budget.")

    if len(monthly) >= 2:
        last = monthly.iloc[-1]
        prev = monthly.iloc[-2]
        direction = "rose" if last["Expense"] >= prev["Expense"] else "fell"
        delta = last["Expense"] - prev["Expense"]
        insights.append(
            f"Spending {direction} {inr(abs(delta))} month-on-month "
            f"({last['YearMonth']}: {inr(last['Expense'])} vs {prev['YearMonth']}: {inr(prev['Expense'])})."
        )
        best = monthly.loc[monthly["Net"].idxmax()]
        worst = monthly.loc[monthly["Net"].idxmin()]
        insights.append(
            f"Best savings month: {best['YearMonth']} (net {inr(best['Net'])}). "
            f"Tightest month: {worst['YearMonth']} (net {inr(worst['Net'])})."
        )

    if wk["weekday_txn"] and wk["weekend_txn"]:
        # Compare average daily spend (weekend has 2 days, weekday 5)
        # We don't have exact day counts, so compare average transaction size.
        ratio = wk["weekend_avg_txn"] / wk["weekday_avg_txn"] if wk["weekday_avg_txn"] else 1
        if ratio >= 1.25:
            insights.append(
                f"Weekend transactions are {ratio:.1f}× larger than weekday ones "
                f"(avg {inr(wk['weekend_avg_txn'])} vs {inr(wk['weekday_avg_txn'])}). "
                f"Food & Dining and Entertainment usually drive this."
            )
        else:
            insights.append(
                "Weekend and weekday ticket sizes are similar — spending is fairly evenly spread through the week."
            )

    food = cats[cats["Category"] == "Food & Dining"]
    groceries = cats[cats["Category"] == "Groceries"]
    if len(food) and len(groceries):
        if food.iloc[0]["Total"] > groceries.iloc[0]["Total"] * 0.9:
            insights.append(
                "Food delivery / dining is almost as high as groceries. Cooking 3 extra meals a week is the highest-ROI habit change."
            )

    subs = cats[cats["Category"] == "Subscriptions"]
    if len(subs) and subs.iloc[0]["Total"] > 8_000:
        insights.append(
            f"Subscriptions total {inr(subs.iloc[0]['Total'])} across the period. "
            f"Audit unused OTTs — cancelling two plans typically saves ₹200–₹700 / month."
        )

    if len(anomalies):
        top_a = anomalies.iloc[0]
        insights.append(
            f"{len(anomalies)} unusual expenses flagged (modified z-score ≥ 2.5). "
            f"Largest: {inr(top_a['Amount'])} at {top_a['Merchant']} ({top_a['Category']}) "
            f"on {pd_date(top_a['Date'])}."
        )

    insights.append(
        f"Next-month expense forecast: {inr(forecast['next_month_expense'])} "
        f"(blend of linear trend and 3-month average; last month was "
        f"{inr(forecast.get('last_month_expense', 0))})."
    )

    insights.append(
        f"Financial Health Score: {health['score']}/100 ({health['label']}) — "
        f"savings {health['savings_points']}/40, budget discipline {health['budget_points']}/35, "
        f"stability {health['stability_points']}/25."
    )

    return insights


def pd_date(value) -> str:
    try:
        return value.strftime("%d %b %Y")
    except Exception:
        import pandas as pd

        return pd.to_datetime(value).strftime("%d %b %Y")


def insights_as_text(df) -> str:
    lines = generate_insights(df)
    numbered = [f"{i}. {line}" for i, line in enumerate(lines, start=1)]
    header = "EXPENSE TRACKER — AUTO-GENERATED INSIGHTS\n" + "=" * 52 + "\n"
    return header + "\n".join(numbered) + "\n"
