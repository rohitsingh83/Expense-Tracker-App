"""
Project configuration: paths, categories, budgets, and visual theme.

All amounts are in Indian Rupees (INR). The synthetic profile models a
junior working professional living in Hyderabad, Telangana.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "outputs"
CHART_DIR = OUTPUT_DIR / "charts"
REPORT_DIR = OUTPUT_DIR / "reports"
IMAGE_DIR = ROOT_DIR / "images"

RAW_DATA_PATH = DATA_DIR / "raw_expenses.csv"
CLEAN_DATA_PATH = DATA_DIR / "cleaned_expenses.csv"
INSIGHTS_PATH = REPORT_DIR / "insights.txt"
SUMMARY_PATH = REPORT_DIR / "monthly_summary.csv"

# ---------------------------------------------------------------------------
# Synthetic-data window  (today is 2026-10-18)
# ---------------------------------------------------------------------------
START_DATE = "2025-11-01"
END_DATE = "2026-10-15"
RANDOM_SEED = 42

# ---------------------------------------------------------------------------
# Persona
# ---------------------------------------------------------------------------
PERSONA = {
    "name": "Arjun Rao",
    "city": "Hyderabad",
    "role": "Junior Data Analyst",
    "monthly_salary": 55_000,
    "currency": "INR",
}

# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------
INCOME_CATEGORIES = ["Salary", "Freelance", "Cashback", "Interest"]

EXPENSE_CATEGORIES = [
    "Rent",
    "Groceries",
    "Food & Dining",
    "Transport",
    "Utilities",
    "Shopping",
    "Entertainment",
    "Healthcare",
    "Education",
    "Subscriptions",
    "Personal Care",
    "Travel",
    "Insurance",
    "Miscellaneous",
]

PAYMENT_METHODS = ["UPI", "Debit Card", "Credit Card", "Cash", "Net Banking"]

# Recommended monthly budgets (INR) — used for budget-vs-actual analysis
MONTHLY_BUDGETS = {
    "Rent": 14_000,
    "Groceries": 5_500,
    "Food & Dining": 4_500,
    "Transport": 3_000,
    "Utilities": 2_800,
    "Shopping": 3_500,
    "Entertainment": 2_000,
    "Healthcare": 1_500,
    "Education": 2_000,
    "Subscriptions": 1_200,
    "Personal Care": 1_200,
    "Travel": 2_500,
    "Insurance": 1_200,
    "Miscellaneous": 1_500,
}

# Savings-rate targets used by the financial-health score
SAVINGS_RATE_HEALTHY = 0.20
SAVINGS_RATE_OK = 0.10

# ---------------------------------------------------------------------------
# Visual theme
# ---------------------------------------------------------------------------
BRAND = {
    "primary": "#0D9488",
    "primary_dark": "#0F766E",
    "income": "#16A34A",
    "expense": "#E11D48",
    "warning": "#D97706",
    "info": "#2563EB",
    "purple": "#7C3AED",
    "muted": "#64748B",
}

CHART_PALETTE = [
    "#0D9488",
    "#E11D48",
    "#D97706",
    "#2563EB",
    "#7C3AED",
    "#0891B2",
    "#DB2777",
    "#65A30D",
    "#EA580C",
    "#4F46E5",
    "#0E7490",
    "#BE123C",
    "#A16207",
    "#4338CA",
]
