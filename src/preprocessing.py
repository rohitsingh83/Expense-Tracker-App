"""
Data cleaning and feature engineering.

Turns the intentionally messy raw ledger into an analysis-ready table.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .config import CLEAN_DATA_PATH, EXPENSE_CATEGORIES, INCOME_CATEGORIES, RAW_DATA_PATH

CANONICAL_CATEGORIES = {c.lower(): c for c in EXPENSE_CATEGORIES + INCOME_CATEGORIES}


def _standardize_category(value: object) -> str | float:
    if pd.isna(value):
        return np.nan
    key = str(value).strip().lower()
    if key in CANONICAL_CATEGORIES:
        return CANONICAL_CATEGORIES[key]
    # light fuzzy rescue for common variants
    aliases = {
        "food": "Food & Dining",
        "food and dining": "Food & Dining",
        "dining": "Food & Dining",
        "travel / holiday": "Travel",
        "bills": "Utilities",
        "bill": "Utilities",
        "health": "Healthcare",
        "medical": "Healthcare",
        "misc": "Miscellaneous",
        "others": "Miscellaneous",
        "other": "Miscellaneous",
        "personal": "Personal Care",
        "sub": "Subscriptions",
        "subscription": "Subscriptions",
        "salary credit": "Salary",
        "cab": "Transport",
        "uber": "Transport",
        "petrol": "Transport",
    }
    return aliases.get(key, str(value).strip().title())


def clean_expenses(df: pd.DataFrame) -> pd.DataFrame:
    """Full cleaning + feature-engineering pipeline."""
    out = df.copy()

    # 1. Drop fully empty rows
    out = out.dropna(how="all")

    # 2. Strip whitespace from object columns
    for col in out.select_dtypes(include="object").columns:
        out[col] = out[col].astype(str).str.strip()
        out[col] = out[col].replace({"nan": np.nan, "None": np.nan, "": np.nan})

    # 3. Parse dates. ISO first; fall back to mixed day/month formats from bank CSVs.
    parsed = pd.to_datetime(out["Date"], errors="coerce", format="ISO8601")
    still_bad = parsed.isna() & out["Date"].notna()
    if still_bad.any():
        parsed.loc[still_bad] = pd.to_datetime(
            out.loc[still_bad, "Date"], errors="coerce", dayfirst=True, format="mixed"
        )
    out["Date"] = parsed

    # 4. Numeric amounts
    out["Amount"] = pd.to_numeric(out["Amount"], errors="coerce")

    # 5. Standardize categories and types
    out["Category"] = out["Category"].apply(_standardize_category)
    out["Type"] = (
        out["Type"]
        .astype(str)
        .str.strip()
        .str.title()
        .replace({"Nan": np.nan, "None": np.nan})
    )

    # 6. Drop rows missing critical fields
    out = out.dropna(subset=["Date", "Amount", "Category", "Type"])

    # 7. Amounts must be positive (a negative expense is a data error here)
    out = out[out["Amount"] > 0]

    # 8. Type must be Income or Expense
    out = out[out["Type"].isin(["Income", "Expense"])]

    # 9. Fill remaining optional fields
    if "Description" in out.columns:
        out["Description"] = out["Description"].fillna("Unspecified")
    if "Merchant" in out.columns:
        out["Merchant"] = out["Merchant"].fillna("Unknown")
    if "Payment_Method" in out.columns:
        out["Payment_Method"] = out["Payment_Method"].fillna("UPI")
    if "City" in out.columns:
        out["City"] = out["City"].fillna("Hyderabad")

    # 10. De-duplicate (exact row copies from the raw extract)
    out = out.drop_duplicates()

    # 11. Feature engineering
    out["Year"] = out["Date"].dt.year
    out["Month_Num"] = out["Date"].dt.month
    out["Month"] = out["Date"].dt.month_name()
    out["Month_Period"] = out["Date"].dt.to_period("M").astype(str)
    out["Day"] = out["Date"].dt.day
    out["Weekday"] = out["Date"].dt.day_name()
    out["Week"] = out["Date"].dt.isocalendar().week.astype(int)
    out["Is_Weekend"] = out["Weekday"].isin(["Saturday", "Sunday"])
    out["Quarter"] = "Q" + out["Date"].dt.quarter.astype(str)
    out["Signed_Amount"] = np.where(out["Type"] == "Expense", -out["Amount"], out["Amount"])

    amount_bins = [0, 200, 500, 1_000, 3_000, 10_000, np.inf]
    amount_labels = ["Micro", "Small", "Medium", "Large", "Very Large", "Major"]
    out["Amount_Band"] = pd.cut(out["Amount"], bins=amount_bins, labels=amount_labels, right=True)

    festival_months = {3, 10, 11, 12}
    out["Is_Festival_Month"] = out["Month_Num"].isin(festival_months)

    out["YearMonth"] = out["Date"].dt.strftime("%Y-%m")

    out = out.sort_values("Date").reset_index(drop=True)
    return out


def load_and_clean(raw_path: Path | None = None, save: bool = True) -> pd.DataFrame:
    raw_path = raw_path or RAW_DATA_PATH
    raw = pd.read_csv(raw_path)
    cleaned = clean_expenses(raw)
    if save:
        CLEAN_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        cleaned.to_csv(CLEAN_DATA_PATH, index=False)
    return cleaned


if __name__ == "__main__":
    frame = load_and_clean()
    print(f"Cleaned shape: {frame.shape}")
    print(frame.head())
