"""
Generate a realistic 12-month synthetic expense ledger.

The raw file is intentionally slightly dirty (mixed case, missing values,
duplicate rows, mixed date formats) so the cleaning step has real work to do.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from .config import (
    END_DATE,
    EXPENSE_CATEGORIES,
    PERSONA,
    RANDOM_SEED,
    RAW_DATA_PATH,
    START_DATE,
)

rng = np.random.default_rng(RANDOM_SEED)


# Merchants that feel local to Hyderabad / India
MERCHANTS = {
    "Groceries": [
        "DMart Kukatpally",
        "BigBasket",
        "Reliance Fresh",
        "More Supermarket",
        "Heritage Fresh",
        "Swiggy Instamart",
        "Ratnadeep",
    ],
    "Food & Dining": [
        "Swiggy",
        "Zomato",
        "Paradise Biryani",
        "Chutneys",
        "Shah Ghouse",
        "Domino's Pizza",
        "Cafe Coffee Day",
        "Starbucks Gachibowli",
        "Abshek's Kitchen",
        "Minerva Coffee Shop",
    ],
    "Transport": [
        "Uber",
        "Ola",
        "Rapido",
        "Hyderabad Metro",
        "TSRTC",
        "Indian Oil Petrol",
        "HP Pay",
    ],
    "Utilities": [
        "TGNPDCL Electricity",
        "HMWSSB Water",
        "Jio Fiber",
        "Airtel Broadband",
        "Indane Gas",
    ],
    "Shopping": [
        "Amazon.in",
        "Flipkart",
        "Myntra",
        "Ajio",
        "Croma",
        "Lifestyle Inorbit",
        "GVK One Mall",
    ],
    "Entertainment": [
        "BookMyShow PVR",
        "Netflix top-up",
        "Spotify",
        "District by Zomato",
        "Wonderla",
        "Shilparamam",
    ],
    "Healthcare": [
        "Apollo Pharmacy",
        "MedPlus",
        "Yashoda Hospital",
        "Aarogya Clinic",
        "1mg",
        "PharmEasy",
    ],
    "Education": [
        "Udemy",
        "Coursera",
        "Amazon Books",
        "Stationery Mart",
        "NPTEL exam fee",
    ],
    "Subscriptions": [
        "Netflix",
        "Spotify Premium",
        "YouTube Premium",
        "ChatGPT Plus",
        "The Hindu Digital",
        "Hotstar",
    ],
    "Personal Care": [
        "Nykaa",
        "Local Salon",
        "Urban Company",
        "Kaya Clinic",
        "Naturals",
    ],
    "Travel": [
        "IRCTC",
        "MakeMyTrip",
        "IndiGo",
        "OYO Rooms",
        "RedBus",
        "Cleartrip",
    ],
    "Insurance": ["Star Health", "LIC Premium", "Acko Two-Wheeler"],
    "Miscellaneous": [
        "GPay self-transfer",
        "Friend repayment",
        "Temple donation",
        "Courier — DTDC",
        "Printout / xerox",
    ],
    "Rent": ["Landlord UPI — Kukatpally"],
    "Salary": ["TCS Salary Credit"],
    "Freelance": ["Upwork payout", "Freelance invoice — Tableau dashboard"],
    "Cashback": ["CRED cashback", "Amazon Pay cashback", "PhonePe rewards"],
    "Interest": ["SBI Savings interest"],
}

DESCRIPTIONS = {
    "Groceries": [
        "Weekly groceries",
        "Vegetables and milk",
        "Rice, dal and oil",
        "Snacks restock",
        "Household supplies",
    ],
    "Food & Dining": [
        "Dinner delivery",
        "Weekend lunch out",
        "Office lunch",
        "Coffee with colleagues",
        "Late-night biryani",
        "Breakfast on the go",
    ],
    "Transport": [
        "Office commute",
        "Airport drop",
        "Metro smart card",
        "Bike fuel",
        "Late-night cab",
    ],
    "Utilities": [
        "Electricity bill",
        "Water bill",
        "Internet bill",
        "Mobile recharge",
        "Gas cylinder",
    ],
    "Shopping": [
        "Clothes",
        "Headphones",
        "Home essentials",
        "Festival shopping",
        "Phone case / accessories",
    ],
    "Entertainment": [
        "Movie tickets",
        "Weekend outing",
        "Concert / event",
        "Bowling with friends",
    ],
    "Healthcare": [
        "Medicines",
        "Doctor consultation",
        "Blood test",
        "Vitamins",
    ],
    "Education": [
        "Online course",
        "Certification exam",
        "Technical book",
        "Stationery",
    ],
    "Subscriptions": [
        "Monthly subscription",
        "Plan renewal",
    ],
    "Personal Care": [
        "Haircut",
        "Skincare",
        "Salon",
        "Grooming kit",
    ],
    "Travel": [
        "Home-town trip",
        "Weekend getaway",
        "Flight tickets",
        "Hotel stay",
    ],
    "Insurance": ["Monthly premium"],
    "Miscellaneous": ["Misc. payment", "Small transfer", "Donation"],
    "Rent": ["House rent"],
    "Salary": ["Monthly salary"],
    "Freelance": ["Freelance project payout"],
    "Cashback": ["App cashback"],
    "Interest": ["Savings-account interest"],
}

# Festival / seasonal spend multipliers by calendar month
SEASONAL = {
    1: 0.88,  # post-holiday belt-tightening
    2: 0.95,
    3: 1.12,  # Holi
    4: 1.00,
    5: 1.18,  # summer travel
    6: 1.05,
    7: 0.96,
    8: 1.08,  # Independence / festivals
    9: 1.02,
    10: 1.10,  # Navratri / early Diwali prep
    11: 1.28,  # Diwali
    12: 1.22,  # Christmas / New Year
}


def _pick(seq):
    return seq[int(rng.integers(0, len(seq)))]


def _amount(low, high, round_to=1):
    value = float(rng.uniform(low, high))
    if round_to >= 1:
        return round(value, 0 if round_to == 1 else 2)
    return round(value, 2)


def _payment_for(category: str, amount: float) -> str:
    """Payment-method mix that matches Indian urban behaviour."""
    if category in {"Rent", "Insurance", "Salary", "Freelance"}:
        return "Net Banking" if category != "Salary" else "Net Banking"
    if category == "Salary":
        return "Net Banking"
    if amount >= 8_000:
        return _pick(["Net Banking", "Credit Card", "UPI"])
    weights = [0.58, 0.14, 0.12, 0.12, 0.04]
    return rng.choice(["UPI", "Debit Card", "Credit Card", "Cash", "Net Banking"], p=weights)


def _date_str(dt: datetime, messy: bool = False) -> str:
    """Occasionally emit mixed date formats so cleaning has work to do."""
    if not messy:
        return dt.strftime("%Y-%m-%d")
    fmt = _pick(["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"])
    return dt.strftime(fmt)


def _row(date, category, amount, txn_type, messy=False):
    merchant = _pick(MERCHANTS[category])
    description = _pick(DESCRIPTIONS[category])
    cat_out = category
    type_out = txn_type
    if messy:
        # mixed case / extra spaces — realistic CSV dirt
        cat_out = _pick([category, category.lower(), category.upper(), f" {category} "])
        type_out = _pick([txn_type, txn_type.lower(), txn_type.upper()])
    return {
        "Date": _date_str(date, messy=messy),
        "Category": cat_out,
        "Description": description,
        "Merchant": merchant,
        "Amount": amount,
        "Type": type_out,
        "Payment_Method": _payment_for(category, amount),
        "City": PERSONA["city"],
    }


def generate_transactions() -> pd.DataFrame:
    random.seed(RANDOM_SEED)
    start = datetime.fromisoformat(START_DATE)
    end = datetime.fromisoformat(END_DATE)

    rows: list[dict] = []
    cursor = datetime(start.year, start.month, 1)

    while cursor <= end:
        year, month = cursor.year, cursor.month
        # last day of this month, clipped to END_DATE
        if month == 12:
            month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = datetime(year, month + 1, 1) - timedelta(days=1)
        month_end = min(month_end, end)
        seasonal = SEASONAL[month]
        n_days = (month_end - datetime(year, month, 1)).days + 1

        def in_month(day: int) -> datetime:
            day = min(day, n_days)
            return datetime(year, month, day)

        # ---- Recurring income / bills (fixed calendar days) ----
        rows.append(_row(in_month(1), "Salary", PERSONA["monthly_salary"], "Income"))
        rows.append(_row(in_month(2), "Rent", 14_000, "Expense"))
        rows.append(_row(in_month(5), "Insurance", 1_185, "Expense"))
        rows.append(
            _row(in_month(7), "Utilities", _amount(1_400, 2_400), "Expense")
        )  # electricity
        rows.append(_row(in_month(8), "Utilities", 799, "Expense"))  # internet
        rows.append(_row(in_month(9), "Utilities", 399, "Expense"))  # mobile
        rows.append(_row(in_month(10), "Subscriptions", 649, "Expense"))  # Netflix
        rows.append(_row(in_month(10), "Subscriptions", 119, "Expense"))  # Spotify
        rows.append(_row(in_month(11), "Subscriptions", 299, "Expense"))  # YouTube
        rows.append(_row(in_month(15), "Education", 1_500, "Expense"))  # gym / learning

        # Quarterly freelance
        if month in {1, 4, 7, 10}:
            rows.append(_row(in_month(18), "Freelance", _amount(8_000, 16_000), "Income"))

        # Savings interest (quarterly-ish)
        if month in {3, 6, 9, 12}:
            rows.append(_row(in_month(min(28, n_days)), "Interest", _amount(220, 480), "Income"))

        # Occasional cashback
        for _ in range(int(rng.integers(1, 4))):
            day = int(rng.integers(1, n_days + 1))
            rows.append(_row(in_month(day), "Cashback", _amount(40, 350), "Income"))

        # ---- Variable daily-ish expenses ----
        def sprinkle(category, count, low, high, weekend_boost=1.0):
            for _ in range(count):
                day = int(rng.integers(1, n_days + 1))
                dt = in_month(day)
                amt = _amount(low, high) * seasonal
                if dt.weekday() >= 5:
                    amt *= weekend_boost
                rows.append(_row(dt, category, round(amt, 0), "Expense"))

        sprinkle("Groceries", int(rng.integers(5, 8)), 350, 1_800, 1.05)
        sprinkle("Food & Dining", int(rng.integers(10, 16)), 120, 850, 1.45)
        sprinkle("Transport", int(rng.integers(12, 18)), 40, 420, 0.7)
        sprinkle("Shopping", int(rng.integers(2, 5)), 400, 3_500, 1.2)
        sprinkle("Entertainment", int(rng.integers(2, 5)), 250, 1_400, 1.6)
        sprinkle("Healthcare", int(rng.integers(0, 3)), 150, 2_200, 1.0)
        sprinkle("Personal Care", int(rng.integers(1, 3)), 250, 1_200, 1.1)
        sprinkle("Miscellaneous", int(rng.integers(1, 4)), 50, 700, 1.0)

        # One or two travel spikes in summer / festival months
        if month in {5, 10, 11, 12} or rng.random() < 0.25:
            day = int(rng.integers(1, n_days + 1))
            rows.append(
                _row(in_month(day), "Travel", round(_amount(1_800, 9_500) * seasonal, 0), "Expense")
            )

        # Advance one month
        if month == 12:
            cursor = datetime(year + 1, 1, 1)
        else:
            cursor = datetime(year, month + 1, 1)

    df = pd.DataFrame(rows)
    df = df.sort_values("Date").reset_index(drop=True)
    return df


def contaminate(df: pd.DataFrame) -> pd.DataFrame:
    """Inject a small, controlled amount of dirt into the raw extract."""
    dirty = df.copy()
    n = len(dirty)

    # Mixed-case / padded categories on ~8% of rows
    idx = rng.choice(n, size=max(8, n // 12), replace=False)
    for i in idx:
        dirty.loc[i, "Category"] = _pick(
            [
                str(dirty.loc[i, "Category"]).lower(),
                str(dirty.loc[i, "Category"]).upper(),
                " " + str(dirty.loc[i, "Category"]) + " ",
            ]
        )
        dirty.loc[i, "Type"] = _pick(
            [str(dirty.loc[i, "Type"]).lower(), str(dirty.loc[i, "Type"]).upper()]
        )

    # Missing values on non-critical + a few critical fields
    for col, k in [("Description", 6), ("Merchant", 5), ("Payment_Method", 4)]:
        miss = rng.choice(n, size=k, replace=False)
        dirty.loc[miss, col] = np.nan

    miss_amt = rng.choice(n, size=3, replace=False)
    dirty.loc[miss_amt, "Amount"] = np.nan

    miss_cat = rng.choice(n, size=2, replace=False)
    dirty.loc[miss_cat, "Category"] = np.nan

    # Duplicate a handful of rows
    dupes = dirty.sample(8, random_state=RANDOM_SEED)
    dirty = pd.concat([dirty, dupes], ignore_index=True)

    # Shuffle so the file does not look pre-sorted
    dirty = dirty.sample(frac=1.0, random_state=RANDOM_SEED).reset_index(drop=True)
    return dirty


def save_raw_dataset(path: Path | None = None) -> pd.DataFrame:
    path = path or RAW_DATA_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    cleanish = generate_transactions()
    raw = contaminate(cleanish)
    raw.to_csv(path, index=False)
    return raw


if __name__ == "__main__":
    frame = save_raw_dataset()
    print(f"Wrote {len(frame)} raw rows → {RAW_DATA_PATH}")
