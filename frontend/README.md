# Membership Reconciliation — Streamlit Frontend

A simple web UI to upload bank statement and backend membership files, run the reconciliation engine, and visualise the results.

## Run the Frontend

From the project root:

```bash
cd membership_reconciliation
pip install -r requirements.txt
streamlit run frontend/app.py
```

Then open the URL shown in the terminal (usually `http://localhost:8501`).

## Features

- Upload **Bank Statement** and **Backend Membership Data** (CSV or Excel)
- One-click **Run Reconciliation**
- KPI cards: totals, variance, matched/unmatched/partial counts
- Interactive charts: status pie chart, rule breakdown bar chart
- Tabbed data views for matched, unmatched, partial, and duplicate records
- Download generated **Excel report** and **JSON audit log**
