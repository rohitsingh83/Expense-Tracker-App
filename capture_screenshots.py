"""
capture_screenshots.py
Captures screenshots of the interactive website (docs/index.html)
and the live GitHub repository for Expense-Tracker-App.
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

os.makedirs("screenshots", exist_ok=True)

chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--hide-scrollbars")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=chrome_options)

try:
    # 1. Local HTML App Overview
    local_url = "file:///" + os.path.abspath("docs/index.html").replace("\\", "/")
    print(f"Loading {local_url}...")
    driver.get(local_url)
    time.sleep(3)
    driver.save_screenshot("screenshots/01_financial_overview_kpis.png")
    print("Saved 01_financial_overview_kpis.png")

    # 2. Cash Flow & Net Savings
    driver.execute_script("window.scrollTo(0, 650);")
    time.sleep(2)
    driver.save_screenshot("screenshots/02_cashflow_velocity_charts.png")
    print("Saved 02_cashflow_velocity_charts.png")

    # 3. Category Breakdown & Budget vs Actual
    driver.execute_script("window.scrollTo(0, 1400);")
    time.sleep(2)
    driver.save_screenshot("screenshots/03_budget_vs_actual_burn.png")
    print("Saved 03_budget_vs_actual_burn.png")

    # 4. Interactive What-If Simulator & Ledger
    driver.execute_script("window.scrollTo(0, 2100);")
    time.sleep(2)
    driver.save_screenshot("screenshots/04_what_if_budget_planner.png")
    print("Saved 04_what_if_budget_planner.png")

    # 5. Remote GitHub Repository
    github_url = "https://github.com/rohitsingh83/Expense-Tracker-App"
    print(f"Loading {github_url}...")
    driver.get(github_url)
    time.sleep(4)
    driver.save_screenshot("screenshots/05_github_repository.png")
    print("Saved 05_github_repository.png")

finally:
    driver.quit()

print("Expense-Tracker-App screenshot capture complete.")
