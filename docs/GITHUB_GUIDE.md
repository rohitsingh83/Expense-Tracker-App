# GitHub upload guide

Use this when the local project already runs (`python main.py` and `streamlit run app.py`).

## Suggested repo metadata

| Field | Value |
|---|---|
| **Repository name** | `Expense-Tracker-App` |
| **Description** | Data-driven expense tracker: synthetic INR ledger, EDA, budget vs actual, anomaly detection, forecast, Streamlit dashboard. |
| **Visibility** | Public |
| **Topics / tags** | `data-science`, `pandas`, `streamlit`, `personal-finance`, `eda`, `python`, `data-analytics`, `fintech`, `budgeting`, `plotly` |
| **License** | MIT |

## One-time setup

```bash
cd Expense-Tracker-App

git init
git add .
git commit -m "feat: initial expense tracker pipeline, charts and Streamlit dashboard"

# Create the empty repo on GitHub first, then:
git branch -M main
git remote add origin https://github.com/<your-username>/Expense-Tracker-App.git
git push -u origin main
```

If GitHub CLI is installed:

```bash
gh repo create Expense-Tracker-App --public --source=. --remote=origin --push
```

## Commit message style (good proof of process)

Recruiters skim `git log`. Prefer small, dated commits over one giant dump.

```
feat: generate 12-month synthetic Hyderabad expense ledger
feat: add cleaning pipeline for mixed dates, nulls and duplicates
feat: category, monthly trend and Pareto analysis
feat: budget vs actual and financial health score
feat: anomaly detection with modified z-score
feat: next-month expense forecast (linear + MA3)
feat: static matplotlib / seaborn chart pack
feat: Streamlit dashboard with filters and insights
docs: README, architecture and interview Q&A
```

## What to tick on GitHub after the push

1. Pin the repo on your profile.
2. Add a social preview: upload `outputs/charts/03_monthly_income_expense.png`.
3. In the About panel, paste the description and topics above.
4. Optional: deploy the app to [Streamlit Community Cloud](https://streamlit.io/cloud) pointing at `app.py`. Put the live URL in the README badge row.

## Screenshots to attach (README or `/images`)

Capture these while the dashboard is running:

1. Overview KPIs + income vs expense chart
2. Category treemap / bar
3. Budget vs actual (red = over)
4. Insights tab with health gauge
5. Anomalies table
6. CLI output of `python main.py`
7. `data/cleaned_expenses.csv` preview in VS Code / Excel

Save them as `images/01_overview.png` etc. and embed:

```markdown
![Overview](images/01_overview.png)
```

## .gitignore already excludes

`__pycache__/`, virtualenvs, `.ipynb_checkpoints/`, OS junk. **Do commit** `data/`, `outputs/charts/` and `outputs/reports/` — they are the proof.
