"""
Expense Tracker Dashboard — Streamlit front-end.

Run from the project root:
    streamlit run app.py
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.analysis import (  # noqa: E402
    WEEKDAY_ORDER,
    budget_vs_actual,
    category_breakdown,
    detect_anomalies,
    financial_health_score,
    forecast_next_month,
    kpis,
    monthly_trend,
    payment_mix,
    top_merchants,
    weekday_pattern,
)
from src.config import CLEAN_DATA_PATH, PERSONA, RAW_DATA_PATH  # noqa: E402
from src.data_generator import save_raw_dataset  # noqa: E402
from src.insights import generate_insights, inr  # noqa: E402
from src.preprocessing import load_and_clean  # noqa: E402

# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Khaata · Expense Intelligence",
    page_icon="₹",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Dark fog · bone text · one dusty steel. Quiet, not neon.
INK = "#EDEDE8"
MUTED = "#9A9A92"
LINE = "#2C2C28"
PAPER = "#111110"
SURFACE = "#1B1B19"
ACCENT = "#8FA4C2"
FOREST = "#8FA4C2"
BRICK = "#C8C4BA"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=MUTED, size=12, family="DM Sans, Segoe UI, sans-serif"),
    margin=dict(l=8, r=8, t=12, b=8),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        orientation="h",
        yanchor="bottom",
        y=1.02,
        x=0,
        font=dict(size=12, color=MUTED),
    ),
    hoverlabel=dict(bgcolor=SURFACE, font_size=12, font_family="DM Sans", font_color=INK, bordercolor=LINE),
    hovermode="x unified",
)

CAT_COLOR = {
    "Rent": "#EDEDE8",
    "Groceries": "#8FA4C2",
    "Food & Dining": "#C8C4BA",
    "Transport": "#9A9A92",
    "Utilities": "#7A7A74",
    "Shopping": "#B4B4AC",
    "Entertainment": "#6B7C92",
    "Healthcare": "#A8B4C4",
    "Education": "#8FA4C2",
    "Subscriptions": "#EDEDE8",
    "Personal Care": "#9A9A92",
    "Travel": "#7A8BA0",
    "Insurance": "#A1A19A",
    "Miscellaneous": "#6B6B66",
    "Salary": "#8FA4C2",
    "Freelance": "#A8B4C4",
    "Cashback": "#C8C4BA",
    "Interest": "#9A9A92",
}
CAT_ICON = {
    "Rent": "🏠",
    "Groceries": "🛒",
    "Food & Dining": "🍽️",
    "Transport": "🛵",
    "Utilities": "💡",
    "Shopping": "🛍️",
    "Entertainment": "🎬",
    "Healthcare": "💊",
    "Education": "📚",
    "Subscriptions": "📺",
    "Personal Care": "✂️",
    "Travel": "✈️",
    "Insurance": "🛡️",
    "Miscellaneous": "📦",
    "Salary": "💼",
    "Freelance": "💻",
    "Cashback": "🎁",
    "Interest": "🏦",
}
PALETTE = list(CAT_COLOR.values())

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');

html, body, [class*="css"], .stApp, p, div, span, input, label {
  font-family: 'DM Sans', 'Segoe UI', sans-serif;
}
.stApp { background: #111110; }
.block-container { padding-top: 1.15rem; padding-bottom: 3.2rem; max-width: 1280px; }

header[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"],
.stDeployButton, div[data-testid="stStatusWidget"] { display: none !important; }

[data-testid="stSidebar"] {
  background: #161614;
  border-right: 1px solid #2C2C28;
}
[data-testid="stSidebar"] * { color: #EDEDE8; }

.brand {
  display: flex; gap: 12px; align-items: center;
  padding: 2px 2px 16px 2px;
  border-bottom: 1px solid #2C2C28;
  margin-bottom: 14px;
}
.brand-mark {
  width: 40px; height: 40px; border-radius: 10px;
  background: #8FA4C2; color: #111110;
  font-family: Fraunces, Georgia, serif; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem; letter-spacing: -1px;
}
.brand h2 {
  margin: 0; font-family: Fraunces, Georgia, serif;
  font-size: 1.2rem; letter-spacing: -0.3px; color: #EDEDE8; font-weight: 700;
}
.brand p { margin: 0; color: #9A9A92; font-size: 0.72rem; letter-spacing: 0.8px; text-transform: uppercase; }

.persona {
  display: flex; gap: 10px; align-items: center;
  background: #1B1B19; border: 1px solid #2C2C28;
  border-radius: 12px; padding: 10px 12px; margin: 8px 0 14px 0;
}
.avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: #8FA4C2; color: #111110; font-weight: 700;
  display: flex; align-items: center; justify-content: center; font-size: 0.8rem;
}
.persona .name { color: #EDEDE8; font-weight: 600; font-size: 0.92rem; }
.persona .role { color: #9A9A92; font-size: 0.75rem; }

.hero {
  background: #1B1B19;
  border: 1px solid #2C2C28;
  border-radius: 18px;
  padding: 26px 28px 22px 28px;
  margin-bottom: 18px;
}
.hero-top { display: flex; justify-content: space-between; gap: 16px; align-items: flex-start; flex-wrap: wrap; }
.kicker {
  color: #8FA4C2; font-size: 0.7rem; letter-spacing: 2px;
  text-transform: uppercase; font-weight: 600;
}
.hero h1 {
  font-family: Fraunces, Georgia, serif; color: #EDEDE8; font-size: 2rem;
  margin: 6px 0 8px 0; letter-spacing: -0.6px; font-weight: 600; line-height: 1.15;
}
.hero .sub { color: #9A9A92; margin: 0; font-size: 0.95rem; }
.chip-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 16px; }
.chip {
  background: #111110; border: 1px solid #2C2C28;
  color: #C8C4BA; border-radius: 999px; padding: 5px 12px; font-size: 0.78rem;
}
.chip b { color: #EDEDE8; }
.chip.good { background: #1A1E24; border-color: #2C2C28; color: #8FA4C2; }
.chip.bad  { background: #111110; border-color: #2C2C28; color: #C8C4BA; }
.chip.warn { background: #111110; border-color: #2C2C28; color: #8FA4C2; }

.health-orb {
  width: 92px; height: 92px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
}
.health-orb .inner {
  width: 74px; height: 74px; border-radius: 50%;
  background: #1B1B19; display: flex; flex-direction: column;
  align-items: center; justify-content: center;
}
.health-orb .n {
  color: #EDEDE8; font-family: Fraunces, Georgia, serif;
  font-size: 1.4rem; font-weight: 700; line-height: 1;
}
.health-orb .l { color: #9A9A92; font-size: 0.6rem; letter-spacing: 0.8px; text-transform: uppercase; margin-top: 2px; }

.kpi-grid {
  display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin: 2px 0 18px 0;
}
@media (max-width: 1100px) { .kpi-grid { grid-template-columns: repeat(2, 1fr); } }
.kpi {
  background: #1B1B19;
  border: 1px solid #2C2C28;
  border-radius: 14px; padding: 16px 16px 14px 16px;
  min-height: 112px;
}
.kpi .label {
  color: #9A9A92; font-size: 0.7rem; letter-spacing: 1px;
  text-transform: uppercase; font-weight: 600;
}
.kpi .value {
  color: #EDEDE8; font-family: Fraunces, Georgia, serif;
  font-size: 1.55rem; font-weight: 600; margin-top: 10px; letter-spacing: -0.4px;
}
.kpi.good .value, .kpi.bad .value, .kpi.teal .value, .kpi.warn .value { color: #EDEDE8; }
.kpi .hint { color: #9A9A92; font-size: 0.78rem; margin-top: 8px; }
.delta { font-weight: 600; font-size: 0.75rem; }
.delta.up { color: #8FA4C2; }
.delta.down { color: #C8C4BA; }

.alert {
  display: flex; gap: 12px; align-items: flex-start;
  border-radius: 12px; padding: 12px 14px; margin: 0 0 16px 0;
  background: #1B1B19; border: 1px solid #2C2C28;
}
.alert.warn { border-left: 3px solid #8FA4C2; }
.alert.bad  { border-left: 3px solid #C8C4BA; }
.alert.good { border-left: 3px solid #8FA4C2; }
.alert .ico {
  width: 28px; height: 28px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  background: #111110; flex-shrink: 0; font-size: 0.9rem; color: #EDEDE8;
}
.alert b { color: #EDEDE8; font-size: 0.92rem; }
.alert p { margin: 3px 0 0 0; color: #9A9A92; font-size: 0.82rem; }

.section-head { display: flex; justify-content: space-between; align-items: baseline; margin: 10px 0 10px 0; }
.section-head h3 {
  margin: 0; color: #EDEDE8; font-family: Fraunces, Georgia, serif;
  font-size: 1.12rem; letter-spacing: -0.2px; font-weight: 600;
}
.section-head span { color: #9A9A92; font-size: 0.78rem; }

.brow { margin: 0 0 14px 0; }
.brow-top { display: flex; justify-content: space-between; font-size: 0.84rem; margin-bottom: 6px; gap: 8px; }
.brow-top .cat { color: #EDEDE8; font-weight: 600; }
.brow-top .amt { color: #9A9A92; font-variant-numeric: tabular-nums; }
.track { height: 6px; background: #2C2C28; border-radius: 99px; overflow: hidden; }
.fill { height: 100%; border-radius: 99px; }
.fill.ok { background: #8FA4C2; }
.fill.warn { background: #8FA4C2; }
.fill.bad { background: #C8C4BA; }

.txn { display: flex; gap: 10px; align-items: center; padding: 9px 0; border-bottom: 1px solid #2C2C28; }
.txn:last-child { border-bottom: none; }
.dot {
  width: 34px; height: 34px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.95rem; background: #111110; flex-shrink: 0;
}
.txn .name { color: #EDEDE8; font-size: 0.86rem; font-weight: 600; }
.txn .sub { color: #9A9A92; font-size: 0.72rem; }
.txn .amt { margin-left: auto; font-weight: 600; font-variant-numeric: tabular-nums; font-size: 0.9rem; color: #EDEDE8; }
.txn .amt.ex { color: #C8C4BA; }
.txn .amt.in { color: #8FA4C2; }

.insight {
  background: #1B1B19; border: 1px solid #2C2C28;
  border-left: 3px solid #8FA4C2;
  border-radius: 10px; padding: 12px 14px; margin-bottom: 8px;
  color: #C8C4BA; font-size: 0.9rem; line-height: 1.55;
}
.insight b { color: #8FA4C2; }

.action {
  background: #1B1B19; border: 1px solid #2C2C28;
  border-radius: 12px; padding: 12px 14px; margin-bottom: 8px;
}
.action .t { color: #EDEDE8; font-weight: 600; font-size: 0.9rem; }
.action .s { color: #9A9A92; font-size: 0.8rem; margin-top: 3px; }
.action .save { color: #8FA4C2; font-weight: 700; font-size: 0.85rem; margin-top: 6px; }

.stat-trio { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin-bottom: 14px; }
.stat {
  background: #1B1B19; border: 1px solid #2C2C28;
  border-radius: 14px; padding: 14px 14px; text-align: center;
}
.stat .n { font-family: Fraunces, Georgia, serif; font-size: 1.4rem; color: #EDEDE8; font-weight: 600; }
.stat .l { color: #9A9A92; font-size: 0.75rem; margin-top: 3px; }

.badge { display: inline-block; padding: 2px 9px; border-radius: 999px; font-size: 0.7rem; font-weight: 700; margin-left: 6px; }
.badge-ok { background: #1A1E24; color: #8FA4C2; }
.badge-warn { background: #1A1A18; color: #C8C4BA; }
.badge-bad { background: #1A1A18; color: #C8C4BA; }

.cat-row {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 2px; border-bottom: 1px solid #2C2C28;
}
.cat-row .share { width: 54px; text-align: right; color: #9A9A92; font-size: 0.78rem; }
.cat-row .barwrap { flex: 1; height: 6px; background: #2C2C28; border-radius: 99px; overflow: hidden; }
.cat-row .name { width: 140px; color: #EDEDE8; font-size: 0.85rem; font-weight: 600; }
.cat-row .val { width: 92px; text-align: right; color: #EDEDE8; font-weight: 600; font-size: 0.85rem; }

div[data-testid="stTabs"] [data-baseweb="tab-list"] {
  gap: 4px; background: transparent; border-bottom: 1px solid #2C2C28;
  padding-bottom: 0; margin-bottom: 12px;
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
  background: transparent; border-radius: 0; padding: 10px 14px;
  color: #9A9A92; font-weight: 600;
}
div[data-testid="stTabs"] [aria-selected="true"] {
  background: transparent !important;
  color: #8FA4C2 !important;
  box-shadow: inset 0 -2px 0 #8FA4C2;
}

[data-testid="stMetricValue"] { font-family: Fraunces, Georgia, serif; }

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-thumb { background: #2C2C28; border-radius: 8px; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def esc(value) -> str:
    return html.escape("" if value is None else str(value))


def inr_compact(n: float) -> str:
    sign = "-" if n < 0 else ""
    n = abs(float(n))
    if n >= 1_00_00_000:
        return f"{sign}₹{n / 1_00_00_000:.2f} Cr"
    if n >= 1_00_000:
        return f"{sign}₹{n / 1_00_000:.2f} L"
    if n >= 10_000:
        return f"{sign}₹{n / 1_000:.1f}k"
    return inr(n if sign == "" else -n)


def cat_color(name: str) -> str:
    return CAT_COLOR.get(name, "#9A9A92")


def cat_icon(name: str) -> str:
    return CAT_ICON.get(name, "•")


def style_fig(fig: go.Figure, height: int = 340) -> go.Figure:
    fig.update_layout(**PLOTLY_LAYOUT, height=height)
    fig.update_xaxes(gridcolor="rgba(44,44,40,0.9)", zerolinecolor=LINE, tickfont=dict(size=11, color=MUTED))
    fig.update_yaxes(gridcolor="rgba(44,44,40,0.9)", zerolinecolor=LINE, tickfont=dict(size=11, color=MUTED))
    return fig


def show_fig(fig: go.Figure, height: int = 340) -> None:
    st.plotly_chart(
        style_fig(fig, height),
        width="stretch",
        config={"displayModeBar": False, "responsive": True},
    )


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    if not RAW_DATA_PATH.exists():
        save_raw_dataset()
    if not CLEAN_DATA_PATH.exists():
        return load_and_clean()
    df = pd.read_csv(CLEAN_DATA_PATH, parse_dates=["Date"])
    if "Is_Weekend" in df.columns:
        df["Is_Weekend"] = df["Is_Weekend"].astype(str).str.lower().isin(["true", "1", "yes"])
    return df


def period_bounds(df: pd.DataFrame, preset: str):
    max_d = pd.Timestamp(df["Date"].max()).normalize()
    min_d = pd.Timestamp(df["Date"].min()).normalize()
    month_start = max_d.replace(day=1)
    if preset == "This month":
        return month_start, max_d
    if preset == "Last month":
        last_end = month_start - pd.Timedelta(days=1)
        last_start = last_end.replace(day=1)
        return last_start, last_end
    if preset == "Last 3 months":
        start = (month_start - pd.DateOffset(months=2)).replace(day=1)
        return max(start, min_d), max_d
    if preset == "Last 6 months":
        start = (month_start - pd.DateOffset(months=5)).replace(day=1)
        return max(start, min_d), max_d
    return min_d, max_d


def mom(df: pd.DataFrame) -> dict:
    monthly = monthly_trend(df)
    if len(monthly) < 2:
        return {}
    last, prev = monthly.iloc[-1], monthly.iloc[-2]
    def pct(a, b):
        return ((a - b) / b) if b else 0.0
    return {
        "expense": pct(last["Expense"], prev["Expense"]),
        "income": pct(last["Income"], prev["Income"]),
        "net_abs": last["Net"] - prev["Net"],
        "last_month": last["YearMonth"],
        "prev_month": prev["YearMonth"],
    }


def delta_html(value: float, invert: bool = False) -> str:
    """invert=True means a drop is good (expenses)."""
    if value == 0:
        return '<span class="delta">flat vs prior month</span>'
    good = (value < 0) if invert else (value > 0)
    cls = "up" if good else "down"
    arrow = "↓" if value < 0 else "↑"
    return f'<span class="delta {cls}">{arrow} {abs(value)*100:.1f}% vs prior month</span>'


def section(title: str, subtitle: str = "") -> None:
    st.markdown(
        f'<div class="section-head"><h3>{esc(title)}</h3><span>{esc(subtitle)}</span></div>',
        unsafe_allow_html=True,
    )


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    initials = "".join(p[0] for p in PERSONA["name"].split()[:2]).upper()
    st.sidebar.markdown(
        f"""
        <div class="brand">
          <div class="brand-mark">₹</div>
          <div>
            <h2>khaata</h2>
            <p>expense intelligence</p>
          </div>
        </div>
        <div class="persona">
          <div class="avatar">{initials}</div>
          <div>
            <div class="name">{esc(PERSONA['name'])}</div>
            <div class="role">{esc(PERSONA['role'])} · {esc(PERSONA['city'])}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    preset = st.sidebar.selectbox(
        "Period",
        ["All time", "Last 6 months", "Last 3 months", "This month", "Last month", "Custom range"],
        index=0,
    )
    min_d, max_d = df["Date"].min().date(), df["Date"].max().date()
    if preset == "Custom range":
        picked = st.sidebar.date_input("Date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        if isinstance(picked, (list, tuple)) and len(picked) == 2:
            start, end = pd.Timestamp(picked[0]), pd.Timestamp(picked[1])
        else:
            start, end = pd.Timestamp(min_d), pd.Timestamp(max_d)
    else:
        start, end = period_bounds(df, preset)

    df = df[(df["Date"] >= start) & (df["Date"] <= end + pd.Timedelta(days=0))]

    with st.sidebar.expander("Categories", expanded=False):
        cats = sorted(df["Category"].dropna().unique().tolist())
        picked_cats = st.multiselect(" ", cats, default=cats, label_visibility="collapsed")
        if picked_cats:
            df = df[df["Category"].isin(picked_cats)]

    with st.sidebar.expander("Payment method", expanded=False):
        methods = sorted(df["Payment_Method"].dropna().unique().tolist())
        picked_pay = st.multiselect("  ", methods, default=methods, label_visibility="collapsed")
        if picked_pay:
            df = df[df["Payment_Method"].isin(picked_pay)]

    txn_type = st.sidebar.radio("Transaction type", ["All", "Expense", "Income"], horizontal=True)
    if txn_type != "All":
        df = df[df["Type"] == txn_type]

    st.sidebar.markdown("---")
    st.sidebar.caption(f"{len(df):,} rows in view")
    st.sidebar.caption(f"{start.strftime('%d %b %Y')} → {end.strftime('%d %b %Y')}")
    return df


def overview_tab(df: pd.DataFrame) -> None:
    metrics = kpis(df)
    health = financial_health_score(df)
    forecast = forecast_next_month(df)
    cats = category_breakdown(df)
    budget = budget_vs_actual(df)
    monthly = monthly_trend(df)
    dlt = mom(df)
    over = budget[budget["Status"] == "Over budget"] if not budget.empty else budget

    ring_color = FOREST if health["score"] >= 65 else ACCENT if health["score"] >= 50 else BRICK
    st.markdown(
        f"""
        <div class="hero">
          <div class="hero-top">
            <div>
              <div class="kicker">Personal finance OS · Hyderabad ledger</div>
              <h1>Good to have you, {esc(PERSONA['name'].split()[0])}.</h1>
              <p class="sub">A year of UPI, cards and cash — cleaned, scored and turned into decisions.</p>
              <div class="chip-row">
                <span class="chip">{metrics['date_min'].strftime('%b %Y')} – {metrics['date_max'].strftime('%b %Y')}</span>
                <span class="chip"><b>{metrics['txn_count']:,}</b> transactions</span>
                <span class="chip {'good' if metrics['savings_rate']>=0.2 else 'warn' if metrics['savings_rate']>=0.1 else 'bad'}">
                  <b>{metrics['savings_rate']*100:.1f}%</b> saved
                </span>
                <span class="chip">Forecast {inr_compact(forecast['next_month_expense'])} next month</span>
              </div>
            </div>
            <div class="health-orb" style="background: conic-gradient({ring_color} {health['score']*3.6}deg, #2C2C28 0deg);">
              <div class="inner">
                <div class="n">{health['score']}</div>
                <div class="l">{esc(health['label'])}</div>
              </div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if metrics["savings_rate"] < 0.10:
        leak = float(over["Variance"].abs().sum()) if len(over) else 0
        top_cut = over.iloc[0]["Category"] if len(over) else metrics["top_category"]
        st.markdown(
            f"""
            <div class="alert bad">
              <div class="ico">⚠</div>
              <div>
                <b>Savings rate {metrics['savings_rate']*100:.1f}% — below the 10% safety line.</b>
                <p>{len(over)} categor{'y is' if len(over)==1 else 'ies are'} over envelope
                (monthly leak {inr(leak)}). Highest-ROI cut: {esc(top_cut)}.</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif len(over):
        st.markdown(
            f"""
            <div class="alert warn">
              <div class="ico">●</div>
              <div>
                <b>{len(over)} categories are running hot.</b>
                <p>{esc(', '.join(over['Category'].tolist()))}. Combined monthly leak {inr(over['Variance'].abs().sum())}.</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="alert good">
              <div class="ico">✓</div>
              <div>
                <b>Every envelope is within budget.</b>
                <p>Keep the savings rate moving toward the 20% planner benchmark.</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    exp_delta = delta_html(dlt.get("expense", 0), invert=True) if dlt else '<span class="hint">need 2 months</span>'
    inc_delta = delta_html(dlt.get("income", 0), invert=False) if dlt else ""
    net_hint = (
        f"{'▲' if dlt.get('net_abs',0)>=0 else '▼'} {inr(abs(dlt.get('net_abs',0)))} vs {dlt.get('prev_month','')}"
        if dlt else f"{metrics['savings_rate']*100:.1f}% of income"
    )

    st.markdown(
        f"""
        <div class="kpi-grid">
          <div class="kpi good">
            <div class="label">Income</div>
            <div class="value">{inr_compact(metrics['total_income'])}</div>
            <div class="hint">{metrics['income_count']} credits · {inc_delta}</div>
          </div>
          <div class="kpi bad">
            <div class="label">Spend</div>
            <div class="value">{inr_compact(metrics['total_expense'])}</div>
            <div class="hint">{metrics['expense_count']} debits · {exp_delta}</div>
          </div>
          <div class="kpi {'good' if metrics['net_savings']>=0 else 'bad'}">
            <div class="label">Net saved</div>
            <div class="value">{inr_compact(metrics['net_savings'])}</div>
            <div class="hint">{esc(net_hint)}</div>
          </div>
          <div class="kpi teal">
            <div class="label">Daily burn</div>
            <div class="value">{inr(metrics['avg_daily_spend'])}</div>
            <div class="hint">median ticket {inr(metrics['median_expense_txn'])}</div>
          </div>
          <div class="kpi warn">
            <div class="label">Top leak</div>
            <div class="value" style="font-size:1.15rem">{esc(metrics['top_category'])}</div>
            <div class="hint">{inr(metrics['top_category_amount'])} in this window</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.65, 1], gap="large")
    with left:
        section("Cashflow", "Income vs expense · hover a month")
        fig = go.Figure()
        if len(monthly):
            fig.add_bar(
                x=monthly["YearMonth"],
                y=monthly["Net"],
                name="Net",
                marker_color=["rgba(143,164,194,0.28)" if v >= 0 else "rgba(200,196,186,0.22)" for v in monthly["Net"]],
                yaxis="y",
                opacity=0.9,
            )
            fig.add_trace(
                go.Scatter(
                    x=monthly["YearMonth"],
                    y=monthly["Income"],
                    name="Income",
                    mode="lines+markers",
                    line=dict(color=FOREST, width=2.6, shape="spline"),
                    marker=dict(size=7),
                    hovertemplate="Income %{y:,.0f}<extra></extra>",
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=monthly["YearMonth"],
                    y=monthly["Expense"],
                    name="Expense",
                    mode="lines+markers",
                    line=dict(color=ACCENT, width=2.6, shape="spline"),
                    marker=dict(size=7),
                    hovertemplate="Expense %{y:,.0f}<extra></extra>",
                )
            )
        fig.update_layout(bargap=0.35)
        show_fig(fig, 360)

    with right:
        section("Where it went", "Share of outflow")
        if len(cats):
            fig = go.Figure(
                go.Pie(
                    labels=cats["Category"],
                    values=cats["Total"],
                    hole=0.72,
                    marker=dict(colors=[cat_color(c) for c in cats["Category"]], line=dict(color=SURFACE, width=2)),
                    textinfo="none",
                    hovertemplate="%{label}<br>₹%{value:,.0f}<br>%{percent}<extra></extra>",
                    sort=False,
                )
            )
            fig.update_layout(
                showlegend=False,
                annotations=[
                    dict(
                        text=f"<b style='font-size:16px;color:{INK}'>{inr_compact(cats['Total'].sum())}</b>"
                        f"<br><span style='color:{MUTED};font-size:11px'>spent</span>",
                        x=0.5,
                        y=0.5,
                        showarrow=False,
                    )
                ],
            )
            show_fig(fig, 360)

    bleft, bright = st.columns([1.15, 1], gap="large")
    with bleft:
        section("Envelope health", "Avg monthly actual vs recommended budget")
        rows = []
        for _, r in budget.head(8).iterrows():
            pct = (r["Avg_Monthly_Actual"] / r["Budget"] * 100) if r["Budget"] else 0
            cls = "bad" if r["Status"] == "Over budget" else "warn" if r["Status"] == "Near limit" else "ok"
            width = min(pct, 100)
            rows.append(
                f"""
                <div class="brow">
                  <div class="brow-top">
                    <span class="cat">{cat_icon(r['Category'])} {esc(r['Category'])}</span>
                    <span class="amt">{inr(r['Avg_Monthly_Actual'])} / {inr(r['Budget'])} · {pct:.0f}%</span>
                  </div>
                  <div class="track"><div class="fill {cls}" style="width:{width:.1f}%"></div></div>
                </div>
                """
            )
        st.markdown("".join(rows) if rows else "<p>No expense rows.</p>", unsafe_allow_html=True)

    with bright:
        section("Latest activity", "Newest 8 movements")
        recent = df.sort_values("Date", ascending=False).head(8)
        bits = []
        for _, r in recent.iterrows():
            kind = "in" if r["Type"] == "Income" else "ex"
            sign = "+" if kind == "in" else "−"
            bits.append(
                f"""
                <div class="txn">
                  <div class="dot">{cat_icon(r['Category'])}</div>
                  <div>
                    <div class="name">{esc(r.get('Merchant', r['Category']))}</div>
                    <div class="sub">{pd.to_datetime(r['Date']).strftime('%d %b')} · {esc(r['Category'])} · {esc(r['Payment_Method'])}</div>
                  </div>
                  <div class="amt {kind}">{sign}{inr(r['Amount'])}</div>
                </div>
                """
            )
        st.markdown("".join(bits), unsafe_allow_html=True)

    section("Three things worth acting on", "auto-generated from the ledger")
    insights = generate_insights(df)
    cols = st.columns(3)
    picks = [insights[i] for i in (2, 5, 9) if i < len(insights)] or insights[:3]
    for col, line in zip(cols, picks):
        col.markdown(f'<div class="insight">{esc(line)}</div>', unsafe_allow_html=True)


def categories_tab(df: pd.DataFrame) -> None:
    cats = category_breakdown(df)
    if cats.empty:
        st.warning("No expense rows in the current filter.")
        return

    c1, c2, c3 = st.columns(3)
    c1.markdown(
        f'<div class="stat"><div class="n">{len(cats)}</div><div class="l">categories</div></div>',
        unsafe_allow_html=True,
    )
    top2 = cats.head(2)["Share_%"].sum() if len(cats) >= 2 else cats["Share_%"].sum()
    c2.markdown(
        f'<div class="stat"><div class="n">{top2:.0f}%</div><div class="l">share of top 2</div></div>',
        unsafe_allow_html=True,
    )
    c3.markdown(
        f'<div class="stat"><div class="n">{inr_compact(cats["Total"].sum())}</div><div class="l">total outflow</div></div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.25, 1], gap="large")
    with left:
        section("Ranked spend", "Click a bar for the rupee value")
        fig = go.Figure(
            go.Bar(
                x=cats["Total"],
                y=cats["Category"],
                orientation="h",
                marker=dict(color=[cat_color(c) for c in cats["Category"]], cornerradius=6),
                text=[inr_compact(v) for v in cats["Total"]],
                textposition="outside",
                hovertemplate="%{y}: ₹%{x:,.0f}<extra></extra>",
            )
        )
        fig.update_layout(yaxis=dict(autorange="reversed"), margin=dict(l=8, r=80, t=8, b=8))
        show_fig(fig, 420)

    with right:
        section("Share of wallet", "")
        rows = []
        mx = cats["Total"].max() or 1
        for _, r in cats.iterrows():
            rows.append(
                f"""
                <div class="cat-row">
                  <div class="name">{cat_icon(r['Category'])} {esc(r['Category'])}</div>
                  <div class="barwrap"><div class="fill ok" style="width:{r['Total']/mx*100:.1f}%;background:{cat_color(r['Category'])}"></div></div>
                  <div class="share">{r['Share_%']:.1f}%</div>
                  <div class="val">{inr_compact(r['Total'])}</div>
                </div>
                """
            )
        st.markdown("".join(rows), unsafe_allow_html=True)

    section("Pareto — which categories drive 80%?", "The dashed line is the 80% mark")
    pareto = cats.sort_values("Total", ascending=False).copy()
    pareto["cum"] = pareto["Total"].cumsum() / pareto["Total"].sum() * 100
    fig = go.Figure()
    fig.add_bar(
        x=pareto["Category"],
        y=pareto["Total"],
        name="Spend",
        marker=dict(color=INK, cornerradius=5),
        hovertemplate="%{x}: ₹%{y:,.0f}<extra></extra>",
    )
    fig.add_scatter(
        x=pareto["Category"],
        y=pareto["cum"],
        name="Cumulative %",
        yaxis="y2",
        mode="lines+markers",
        line=dict(color=ACCENT, width=2.6, shape="spline"),
        hovertemplate="%{y:.1f}%<extra></extra>",
    )
    fig.add_hline(y=80, line_dash="dot", line_color=ACCENT, yref="y2")
    fig.update_layout(yaxis2=dict(overlaying="y", side="right", range=[0, 105], title="Cumulative %", showgrid=False))
    show_fig(fig, 340)

    section("Category table", "")
    show = cats.copy()
    show["Total"] = show["Total"].map(inr)
    show["Average"] = show["Average"].map(inr)
    show["Median"] = show["Median"].map(inr)
    show["Share_%"] = show["Share_%"].map(lambda x: f"{x:.1f}%")
    st.dataframe(show, width="stretch", hide_index=True)


def trends_tab(df: pd.DataFrame) -> None:
    monthly = monthly_trend(df)
    section("Month-wise surplus / deficit", "Green = saved · rose = drew down")
    fig = go.Figure()
    colors = [FOREST if v >= 0 else ACCENT for v in monthly["Net"]]
    fig.add_bar(
        x=monthly["YearMonth"],
        y=monthly["Net"],
        marker_color=colors,
        name="Net",
        text=[inr_compact(v) for v in monthly["Net"]],
        textposition="outside",
        hovertemplate="%{x}: ₹%{y:,.0f}<extra></extra>",
    )
    fig.add_hline(y=0, line_color=LINE)
    show_fig(fig, 320)

    c1, c2 = st.columns(2, gap="large")
    with c1:
        section("Week rhythm", "Weekends highlighted")
        wk = weekday_pattern(df)
        fig = go.Figure(
            go.Bar(
                x=wk["Weekday"],
                y=wk["Total"],
                marker_color=[INK] * 5 + [ACCENT] * 2,
                hovertemplate="%{x}: ₹%{y:,.0f}<extra></extra>",
            )
        )
        show_fig(fig, 300)
    with c2:
        section("How you pay", "UPI still rules urban India")
        mix = payment_mix(df)
        fig = go.Figure(
            go.Pie(
                labels=mix["Payment_Method"],
                values=mix["Total"],
                hole=0.62,
                marker=dict(colors=[INK, ACCENT, "#9A9A92", "#6B7C92", "#C8C4BA"], line=dict(color=SURFACE, width=2)),
                textinfo="label+percent",
                textfont=dict(size=11, color=INK),
                hovertemplate="%{label}: ₹%{value:,.0f}<extra></extra>",
            )
        )
        fig.update_layout(showlegend=False)
        show_fig(fig, 300)

    expense = df[df["Type"] == "Expense"].copy()
    if not expense.empty:
        section("Seasonality heatmap", "Weekday × month number")
        heat = expense.groupby(["Weekday", "Month_Num"], as_index=False)["Amount"].sum()
        heat["Weekday"] = pd.Categorical(heat["Weekday"], WEEKDAY_ORDER, ordered=True)
        pivot = heat.pivot(index="Weekday", columns="Month_Num", values="Amount")
        fig = go.Figure(
            go.Heatmap(
                z=pivot.values,
                x=[str(c) for c in pivot.columns],
                y=list(pivot.index),
                colorscale=[[0, "#1B1B19"], [0.55, "#3A4554"], [1, "#8FA4C2"]],
                hovertemplate="Month %{x} · %{y}<br>₹%{z:,.0f}<extra></extra>",
                colorbar=dict(title="INR"),
            )
        )
        show_fig(fig, 280)

    section("Monthly ledger", "")
    table = monthly.copy()
    for col in ("Income", "Expense", "Net"):
        table[col] = table[col].map(inr)
    table["Savings_Rate_%"] = monthly["Savings_Rate_%"].map(lambda x: f"{x:.1f}%")
    if "Expense_MoM_%" in table.columns:
        table["Expense_MoM_%"] = monthly["Expense_MoM_%"].map(lambda x: "—" if pd.isna(x) else f"{x:.1f}%")
    st.dataframe(table, width="stretch", hide_index=True)


def budget_tab(df: pd.DataFrame) -> None:
    b = budget_vs_actual(df)
    over = b[b["Status"] == "Over budget"]
    near = b[b["Status"] == "Near limit"]
    ok = b[b["Status"] == "Within budget"]
    leak = float(over["Variance"].abs().sum()) if len(over) else 0

    st.markdown(
        f"""
        <div class="stat-trio">
          <div class="stat"><div class="n" style="color:#C8C4BA">{len(over)}</div><div class="l">over budget</div></div>
          <div class="stat"><div class="n" style="color:#8FA4C2">{len(near)}</div><div class="l">near the line</div></div>
          <div class="stat"><div class="n" style="color:#8FA4C2">{len(ok)}</div><div class="l">within envelope</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if leak:
        st.markdown(
            f"""
            <div class="alert bad">
              <div class="ico">₹</div>
              <div>
                <b>Monthly leak {inr(leak)} across {len(over)} categories.</b>
                <p>Closing just the top two overruns would recover most of the gap to a 10% savings rate.</p>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    section("Every envelope", "Average month in this window vs recommended budget")
    rows = []
    for _, r in b.iterrows():
        pct = (r["Avg_Monthly_Actual"] / r["Budget"] * 100) if r["Budget"] else 0
        cls = {"Over budget": "bad", "Near limit": "warn", "Within budget": "ok"}[r["Status"]]
        badge = {"Over budget": "badge-bad", "Near limit": "badge-warn", "Within budget": "badge-ok"}[r["Status"]]
        width = min(pct, 100)
        variance = r["Variance"]
        var_txt = f"{inr(abs(variance))} {'under' if variance>=0 else 'over'}"
        rows.append(
            f"""
            <div class="brow">
              <div class="brow-top">
                <span class="cat">{cat_icon(r['Category'])} {esc(r['Category'])}
                  <span class="badge {badge}">{esc(r['Status'])}</span></span>
                <span class="amt">{inr(r['Avg_Monthly_Actual'])} / {inr(r['Budget'])} · {var_txt}</span>
              </div>
              <div class="track"><div class="fill {cls}" style="width:{width:.1f}%"></div></div>
            </div>
            """
        )
    st.markdown("".join(rows), unsafe_allow_html=True)
    st.caption("Envelopes are recommended monthly budgets for a Hyderabad junior analyst — not bank-hard limits.")

    section("Actual vs budget", "Rose = over · teal = within")
    fig = go.Figure()
    fig.add_bar(
        y=b["Category"],
        x=b["Budget"],
        name="Budget",
        orientation="h",
        marker=dict(color="rgba(237,237,232,0.12)", cornerradius=4),
    )
    fig.add_bar(
        y=b["Category"],
        x=b["Avg_Monthly_Actual"],
        name="Avg actual",
        orientation="h",
        marker=dict(
            color=[ACCENT if s == "Over budget" else FOREST for s in b["Status"]],
            cornerradius=4,
        ),
    )
    fig.update_layout(barmode="overlay", yaxis=dict(autorange="reversed"))
    show_fig(fig, 460)


def insights_tab(df: pd.DataFrame) -> None:
    health = financial_health_score(df)
    forecast = forecast_next_month(df)
    anomalies = detect_anomalies(df)
    merchants = top_merchants(df, n=8)
    cats = category_breakdown(df)
    n_months = max(df["YearMonth"].nunique(), 1)

    col1, col2 = st.columns([1.35, 1], gap="large")
    with col1:
        section("What the data is saying", "14 auto-generated observations")
        for i, line in enumerate(generate_insights(df), start=1):
            st.markdown(f'<div class="insight"><b>{i:02d}</b> &nbsp;{esc(line)}</div>', unsafe_allow_html=True)
    with col2:
        section("Health score", "40 savings · 35 discipline · 25 stability")
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=health["score"],
                number={"suffix": "/100", "font": {"size": 32, "color": INK, "family": "Fraunces, Georgia, serif"}},
                gauge={
                    "axis": {"range": [0, 100], "tickcolor": LINE},
                    "bar": {"color": ACCENT, "thickness": 0.22},
                    "bgcolor": SURFACE,
                    "steps": [
                        {"range": [0, 50], "color": "#222220"},
                        {"range": [50, 65], "color": "#2A2A28"},
                        {"range": [65, 80], "color": "#2E3540"},
                        {"range": [80, 100], "color": "#3A4554"},
                    ],
                    "threshold": {"line": {"color": INK, "width": 2}, "value": 80},
                },
                title={"text": health["label"], "font": {"color": MUTED, "size": 14}},
            )
        )
        fig.update_layout(height=250, **PLOTLY_LAYOUT)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

        def bar(label, got, tot):
            pct = got / tot * 100 if tot else 0
            return (
                f'<div class="brow"><div class="brow-top"><span class="cat">{esc(label)}</span>'
                f'<span class="amt">{got:.0f}/{tot}</span></div>'
                f'<div class="track"><div class="fill ok" style="width:{pct:.1f}%"></div></div></div>'
            )

        st.markdown(
            bar("Savings rate", health["savings_points"], 40)
            + bar("Budget discipline", health["budget_points"], 35)
            + bar("Spend stability", health["stability_points"], 25),
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="insight">Next-month expense forecast <b>{inr(forecast["next_month_expense"])}</b> '
            f'({esc(forecast["method"])}).</div>',
            unsafe_allow_html=True,
        )

        section("Moves that actually move the needle", "")
        actions = []
        food = cats[cats["Category"] == "Food & Dining"]
        if len(food):
            save = food.iloc[0]["Total"] * 0.15 / n_months
            actions.append(("Cook 3 extra meals / week", "Cut dining 15% vs this run-rate.", save))
        subs = cats[cats["Category"] == "Subscriptions"]
        if len(subs):
            save = min(700, subs.iloc[0]["Total"] / n_months * 0.3)
            actions.append(("Audit unused OTTs", "Two idle plans is ₹200–₹700 a month.", save))
        shop = cats[cats["Category"] == "Shopping"]
        if len(shop):
            save = shop.iloc[0]["Total"] * 0.10 / n_months
            actions.append(("48-hour cart rule", "Delay non-essential shopping 2 days.", save))
        for title, sub, save in actions:
            st.markdown(
                f'<div class="action"><div class="t">{esc(title)}</div>'
                f'<div class="s">{esc(sub)}</div>'
                f'<div class="save">~{inr(save)} / month</div></div>',
                unsafe_allow_html=True,
            )

    section("Unusual expenses", "Modified z-score ≥ 2.5 inside each category — rent never flags just for being large")
    if anomalies.empty:
        st.success("No statistically unusual expenses in this window.")
    else:
        view = anomalies.copy()
        view["Date"] = pd.to_datetime(view["Date"]).dt.strftime("%d %b %Y")
        view["Amount"] = view["Amount"].map(inr)
        view["Anomaly_Score"] = view["Anomaly_Score"].map(lambda x: f"{x:.2f}")
        st.dataframe(view, width="stretch", hide_index=True)

    section("Merchants taking the rupees", "")
    fig = go.Figure(
        go.Bar(
            x=merchants["Amount"],
            y=merchants["Merchant"],
            orientation="h",
            marker=dict(color=[cat_color(c) for c in merchants["Category"]], cornerradius=6),
            hovertemplate="%{y}<br>₹%{x:,.0f}<extra></extra>",
            text=merchants["Category"],
            textposition="inside",
            insidetextanchor="start",
            textfont=dict(color=PAPER, size=11),
        )
    )
    fig.update_layout(yaxis=dict(autorange="reversed"))
    show_fig(fig, 340)


def transactions_tab(df: pd.DataFrame) -> None:
    section("Ledger explorer", "Search, then download the slice")
    c1, c2, c3 = st.columns([2, 1, 1])
    q = c1.text_input("Search merchant or description", placeholder="e.g. Swiggy, rent, Netflix")
    kind = c2.selectbox("Type", ["All", "Expense", "Income"])
    sort = c3.selectbox("Sort", ["Newest first", "Oldest first", "Amount high → low"])

    view = df.copy()
    if q:
        mask = view["Description"].astype(str).str.contains(q, case=False, na=False) | view[
            "Merchant"
        ].astype(str).str.contains(q, case=False, na=False)
        view = view[mask]
    if kind != "All":
        view = view[view["Type"] == kind]
    if sort == "Newest first":
        view = view.sort_values("Date", ascending=False)
    elif sort == "Oldest first":
        view = view.sort_values("Date", ascending=True)
    else:
        view = view.sort_values("Amount", ascending=False)

    inc = view.loc[view["Type"] == "Income", "Amount"].sum()
    exp = view.loc[view["Type"] == "Expense", "Amount"].sum()
    st.markdown(
        f"""
        <div class="stat-trio">
          <div class="stat"><div class="n">{len(view):,}</div><div class="l">rows</div></div>
          <div class="stat"><div class="n" style="color:#8FA4C2">{inr_compact(inc)}</div><div class="l">inflow</div></div>
          <div class="stat"><div class="n" style="color:#C8C4BA">{inr_compact(exp)}</div><div class="l">outflow</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    show = view[
        ["Date", "Type", "Category", "Merchant", "Description", "Amount", "Payment_Method", "Weekday"]
    ].copy()
    show["Date"] = pd.to_datetime(show["Date"]).dt.strftime("%Y-%m-%d")
    st.dataframe(
        show,
        width="stretch",
        hide_index=True,
        height=520,
        column_config={
            "Amount": st.column_config.NumberColumn("Amount (₹)", format="₹%.0f"),
            "Type": st.column_config.TextColumn("Type", width="small"),
            "Category": st.column_config.TextColumn("Category", width="medium"),
        },
    )
    st.download_button(
        "Download this slice as CSV",
        view.to_csv(index=False).encode("utf-8"),
        "filtered_expenses.csv",
        "text/csv",
    )


def main() -> None:
    full = load_data()
    filtered = apply_filters(full)
    if filtered.empty:
        st.warning("No rows match the current filters. Widen the period or categories.")
        return

    tabs = st.tabs(["Overview", "Categories", "Trends", "Budget", "Insights", "Ledger"])
    with tabs[0]:
        overview_tab(filtered)
    with tabs[1]:
        categories_tab(filtered)
    with tabs[2]:
        trends_tab(filtered)
    with tabs[3]:
        budget_tab(filtered)
    with tabs[4]:
        insights_tab(filtered)
    with tabs[5]:
        transactions_tab(filtered)


if __name__ == "__main__":
    main()
