# Membership Reconciliation — What Is Missing & Where

This document lists gaps, limitations, and recommended next steps for the current implementation.

## 1. Data Quality & Ingestion

| # | Missing Item | Location / Module | Impact | Recommended Fix |
|---|---|---|---|---|
| 1 | **No handling of multi-currency** | `ingest.py`, `matcher.py` | FX differences can create false mismatches | Add `currency` normalisation and optional FX conversion table |
| 2 | **No validation of amount signs** | `ingest.py` | Refunds may be misclassified | Explicitly tag negative bank amounts as refunds; validate against backend status |
| 3 | **No support for bank statement fees/charges** | `ingest.py` | Net bank credit may differ from invoice amount | Deduct gateway fees or match gross vs net amounts separately |
| 4 | **No handling of consolidated bulk deposits** | `matcher.py` | One bank entry may cover multiple backend bookings | Add 1:N and N:M split/combine matching logic |
| 5 | **No data-quality report** | `reporter.py` | Users cannot see ingestion issues | Add a `Data Quality` sheet with nulls, bad dates, zero amounts |

## 2. Matching Logic

| # | Missing Item | Location / Module | Impact | Recommended Fix |
|---|---|---|---|---|
| 6 | **No manual override workflow** | `matcher.py` | Unmatched records cannot be resolved persistently | Add `manual_mapping.csv` input and `MANUAL_OVERRIDE` reason code |
| 7 | **No learning from past resolutions** | `matcher.py` | Same unmatched patterns repeat every run | Store historical match decisions and use them as training data |
| 8 | **Greedy matching may be sub-optimal** | `matcher.py` | A lower-priority match may block a better match | Implement Hungarian / linear-sum assignment for global optimisation |
| 9 | **No partial-payment handling** | `matcher.py` | Instalments or part payments are not reconciled | Allow amount tolerance and instalment aggregation |
| 10 | **No refund-pair logic** | `matcher.py` | Refund bank entries may match to original booking instead of refund record | Match negative bank amounts only to `Refunded` backend rows |
| 11 | **Limited fuzzy logic for narration** | `matcher.py` | UPI IDs embedded in narration are not extracted | Use regex to extract UTR/txn IDs from narration before matching |
| 12 | **No blacklist / ignore list** | `matcher.py` | Internal transfers, interest, charges create noise | Add ignore-keywords config and `IGNORED` category |

## 3. Output & Reporting

| # | Missing Item | Location / Module | Impact | Recommended Fix |
|---|---|---|---|---|
| 13 | **No variance explanation narrative** | `reporter.py` | Finance team must manually explain variance | Auto-generate text explaining unmatched + partial totals |
| 14 | **No channel/mode pivot tables** | `reporter.py` | Hard to spot channel-specific leakage | Add pivot sheets: variance by channel, mode, plan, salesperson |
| 15 | **No trend / ageing analysis** | `reporter.py` | Old unmatched items are not prioritised | Add `days_unmatched` column and ageing buckets |
| 16 | **No email / notification trigger** | `reporter.py` | Stakeholders must manually check output | Integrate with email/Slack for exception alerts |
| 17 | **No dashboard / visual charts** | `reporter.py` | Hard to consume for non-technical users | Build HTML/Excel dashboard with charts |

## 4. Operations & Governance

| # | Missing Item | Location / Module | Impact | Recommended Fix |
|---|---|---|---|---|
| 18 | **No role-based access control** | Entire project | Sensitive financial data exposed | Run inside secure environment with user authentication |
| 19 | **No audit trail of who ran what** | `cli.py` | Cannot trace reconciliation runs | Log user, timestamp, input file hashes, config version |
| 20 | **No unit / integration tests** | `tests/` | Regressions likely | Add `pytest` suite covering all rules and edge cases |
| 21 | **No CI/CD or scheduling** | Project root | Runs are manual | Add GitHub Actions / cron / Airflow DAG |
| 22 | **No data retention policy** | Entire project | Old files accumulate | Archive or purge input/output files per policy |

## 5. Scalability & Performance

| # | Missing Item | Location / Module | Impact | Recommended Fix |
|---|---|---|---|---|
| 23 | **O(n²) candidate generation** | `matcher.py` | Slow beyond ~50k rows | Use indexing by amount/date buckets before scoring |
| 24 | **No streaming / chunked processing** | `ingest.py` | Memory issues with large files | Use pandas chunks or Dask/Polars |
| 25 | **No database connector** | `ingest.py` | Must export CSV/Excel first | Add direct connectors to MySQL/Postgres/SQL Server |

## 6. User Experience

| # | Missing Item | Location / Module | Impact | Recommended Fix |
|---|---|---|---|---|
| 26 | **No web UI for upload & review** | Entire project | Non-technical users struggle with CLI | Build a lightweight Streamlit / Flask UI |
| 27 | **No interactive exception handling** | Entire project | Users cannot mark matches in the UI | Add review screen with approve/reject/manual-link actions |
| 28 | **No sample templates for users** | `data/` | Users may provide wrong column names | Provide Excel templates with validated headers |

## Quick-Win Priority Order
1. Add regex extraction of UTR/txn IDs from narration.
2. Add `manual_mapping.csv` support.
3. Add data-quality sheet.
4. Add pivot/variance-by-channel sheets.
5. Add pytest test suite.
6. Optimise matcher with amount/date indexing.
