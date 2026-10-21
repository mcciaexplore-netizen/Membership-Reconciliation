# Membership Reconciliation Engine

A Python project to reconcile bank statement membership transactions against internal backend membership bookings (online + offline).

## Quick Start (Dashboard)

The recommended way to use the application is through the premium Streamlit dashboard.

```bash
cd membership_reconciliation
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run the UI
streamlit run frontend/app.py
```

## Folder Structure

```
membership_reconciliation/
├── config/
│   └── config.yaml              # Column mappings, tolerances, rules
├── data/
│   ├── sample_bank_statement.csv
│   └── sample_backend_data.csv
├── frontend/
│   └── app.py                   # Streamlit UI dashboard
├── output/                      # Generated reports
├── src/
│   ├── ingest.py                # Data loading & normalisation
│   ├── matcher.py               # Reconciliation rules
│   └── reporter.py              # Excel output logic
└── requirements.txt
```

## Configuration

Edit `config/config.yaml` to map your column names, date formats, and matching tolerances to match your uploaded files.

## Output

The reconciliation engine generates an Excel report with the following sheets:
- **Matched** — successfully paired records
- **Unmatched Bank** — bank credits with no backend booking
- **Unmatched Backend** — backend bookings with no bank credit
- **Partial Discrepant** — reference matched but amount/date differs
- **Duplicates** — duplicate references
- **Summary** — high-level reconciliation metrics

