# Interview preparation — Expense Tracker App

Use the **short answer** in HR / intro rounds. Use the **technical answer** when a DA / BA / FA interviewer digs in.

---

### 1. Explain your Expense Tracker project.

**HR / 30 seconds**  
I built a system that takes a year of day-to-day money movements, cleans them, and shows where the money went, whether the person is over budget, and what next month might cost. It ends in a dashboard a non-technical user can filter.

**Technical**  
End-to-end Python pipeline on a 12-month synthetic INR ledger for a Hyderabad junior analyst. Stages: dirty CSV generation → pandas cleaning & feature engineering → aggregations (category, month, weekday, payment mix, Pareto) → budget variance → modified z-score anomalies → blended linear/MA3 forecast → financial health score → Streamlit + static charts. No bank APIs; the value is the analytics layer.

---

### 2. What problem does it solve?

**HR**  
People know they overspend but cannot see the pattern. The app turns a pile of transactions into a few decisions: which category to cut, which month was worst, which payments look odd.

**Technical**  
It is a spend-intelligence layer. Same job Mint, GPay insights, CRED, RazorpayX and PhonePe do on real rails: categorise, aggregate, visualise, alert. For a student portfolio it proves you can take messy tabular data to a decision, not just a notebook of plots.

---

### 3. What data did you use? Why synthetic?

**HR**  
I could not use anyone’s real bank statement, so I generated a realistic fake year of income and expenses in rupees, with Hyderabad merchants.

**Technical**  
~700–900 rows, Nov 2025–Oct 2026. Fields: date, category, description, merchant, amount, type, payment method, city. Recurring items (salary, rent, OTT, insurance) plus stochastic daily spend with weekend and festival multipliers. The *raw* file is contaminated on purpose (mixed date formats, nulls, duplicates, case noise) so cleaning is demonstrable. Seed is fixed (`RANDOM_SEED = 42`) for reproducibility.

---

### 4. Tools and libraries?

Python, Pandas (reshape / groupby / datetime), NumPy (forecast, scores), Matplotlib & Seaborn (static report charts), Plotly (interactive dashboard), Streamlit (app), openpyxl (Excel-ready). Git for proof of work.

---

### 5. What analysis did you perform?

- Descriptive: totals, averages, medians, ticket-size bands  
- Composition: category share, payment mix, top merchants, Pareto  
- Time: monthly income vs expense, MoM %, weekday seasonality, heatmap  
- Diagnostic: budget vs actual, weekend vs weekday ticket size  
- Detection: modified z-score anomalies *within* category (not global — rent would otherwise drown food)  
- Predictive: next-month expense = `0.4 * linear trend + 0.6 * 3-month MA`  
- Score: 0–100 health = savings (40) + budget discipline (35) + stability (25)

---

### 6. What visualisations?

Bar (category, merchants, payment), pie / donut, treemap, line (income vs expense), grouped bar (budget vs actual), Pareto dual-axis, weekday bar with weekend highlight, weekday×month heatmap, health gauge. Static PNGs live in `outputs/charts/`; interactive copies are in Streamlit.

---

### 7. What insights can it generate?

Examples the pipeline is designed to surface:

- Savings rate vs the 20% planner rule of thumb  
- Top two categories as a share of outflow  
- Categories over the recommended monthly envelope, with the rupee leak  
- Best / worst savings month  
- Weekend tickets vs weekday tickets  
- Dining vs groceries (delivery leak)  
- Subscription load  
- Unusual merchants / amounts  
- Next-month spend forecast vs last month  

Exact sentences are generated in `src/insights.py` and saved to `outputs/reports/insights.txt`.

---

### 8. Challenges?

1. **Dirty input** — mixed date formats needed `dayfirst=True` plus `errors='coerce'`, then drop NaT.  
2. **Category drift** — `food` vs `Food & Dining`; solved with a canonical map + aliases.  
3. **Anomalies** — a global z-score flags rent every month. Category-level modified z-score (MAD) is robust to skew.  
4. **Forecast on 12 points** — too little for Prophet; a blended linear + MA3 is honest about uncertainty.  
5. **Dashboard vs notebook** — recruiters want something they can click; Streamlit is the demo layer, notebooks/scripts are the proof of method.

---

### 9. How would you improve it?

- Ingest real bank/UPI CSV (HDFC, SBI, GPay export)  
- Auto-categorise descriptions with a small classifier or rules+LLM  
- Recurring-transaction detection (same merchant ±3 days, ±5% amount)  
- Prophet / SARIMA once there are 24+ months  
- Budget alerts (email / WhatsApp) when a category hits 80%  
- Multi-profile (family) and goal tracking  
- Deploy on Streamlit Cloud with a public URL on the resume

---

### 10. Explain it to a non-technical person.

Imagine all your GPay, card and cash spends for a year dumped into one Excel. This project sorts that mess, draws simple pictures of where money went, warns you if a category is over a sensible monthly limit, points at weird one-off spends, and guesses next month’s total so you can plan.

---

## Extra questions you should be ready for

**Why modified z-score, not IQR or Isolation Forest?**  
N per category is small (often 10–40). MAD-based modified z-score is simple, robust to outliers, and easy to explain. Isolation Forest is overkill and harder to defend with n≈800.

**Why not a real ML model for “expense prediction”?**  
Twelve monthly points. A linear slope plus a short moving average is the statistically honest choice. I would upgrade the model only after 24 months of data.

**How is the health score weighted?**  
Savings rate is the outcome that matters most (40). Hitting envelopes is the controllable behaviour (35). Jumping around month to month is a stability penalty (25). Thresholds: 20% savings = full savings points; 10% = partial.

**How would this run at a bank?**  
Replace the generator with a warehouse extract (FCT_TRANSACTION). Cleaning becomes a dbt model. Anomalies become a daily batch. The Streamlit app becomes a Looker/Power BI tile or an in-app insight card.

**What is your favourite insight from *this* seed?**  
Run `python main.py` and quote a number from `insights.txt` — never invent it in the interview. Interviewers sometimes open the repo.

**SQL equivalent of your category breakdown?**

```sql
SELECT category,
       SUM(amount) AS total,
       COUNT(*)    AS txns,
       AVG(amount) AS avg_amt
FROM expenses
WHERE type = 'Expense'
GROUP BY category
ORDER BY total DESC;
```

Know this. Many DA interviews switch from Python to SQL mid-answer.
