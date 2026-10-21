# Membership Reconciliation System — Full Prompt

## 1. Objective
Build a Python-based **Membership Reconciliation Engine** that compares financial transactions recorded in the organisation’s **bank statement** against membership bookings recorded in the **internal backend system** (online + offline). The engine must identify matched, unmatched, partial/discrepant, and duplicate records, and produce an auditable reconciliation report.

## 2. Inputs

### 2.1 Bank Statement
A CSV/Excel export from the bank containing at minimum:
- `txn_date` — transaction date (DD-MM-YYYY or ISO)
- `txn_id` / `utr` / `reference_no` — unique bank reference
- `amount` — credited amount (INR/USD/etc.)
- `narration` / `description` — remitter name, mode, notes
- `currency` (optional)
- `account_number` (optional, for multi-account reconciliation)

### 2.2 Backend Membership Data
A CSV/Excel export from the internal CRM/ERP containing:
- `booking_date` — date membership was booked
- `member_id` / `customer_id`
- `member_name`
- `membership_plan` / `tier`
- `amount` — amount charged / collected
- `payment_mode` — Online (UPI, Card, Netbanking) / Offline (Cash, Cheque, POS)
- `payment_reference` — UTR, cheque no., transaction ID, invoice no.
- `sales_channel` — Website, App, Sales Desk, Partner, Field Agent
- `booking_status` — Confirmed, Cancelled, Refunded, Pending
- `sales_person` / `agent_id` (optional)

## 3. Expected Outputs

### 3.1 Reconciliation Report (Excel with multiple sheets)
1. **Matched** — bank txn ↔ backend booking, 1:1 exact match on amount + reference/date.
2. **Unmatched Bank** — money received in bank but no corresponding backend booking.
3. **Unmatched Backend** — backend booking recorded but no corresponding bank credit.
4. **Partial / Discrepant** — reference matches but amount differs, or date differs beyond tolerance.
5. **Duplicates** — same bank reference linked to multiple backend bookings or vice versa.
6. **Summary Dashboard** — counts, totals, variance by channel/mode/status.

### 3.2 Audit Log
A timestamped log of matching rules applied, thresholds used, and manual-review flags.

## 4. Matching Rules (in priority order)

| Priority | Rule | Fields | Tolerance |
|---|---|---|---|
| 1 | Exact Reference Match | `payment_reference` == `txn_id`/`utr` | Exact |
| 2 | Exact Amount + Date Match | `amount` equal and `booking_date` == `txn_date` | ±0 date |
| 3 | Fuzzy Reference + Amount Match | `payment_reference` fuzzy similar to `narration`/`txn_id` and amount equal | Levenshtein ≤ 2 |
| 4 | Amount + Date Window Match | `amount` equal and dates within ±3 days | ±3 days |
| 5 | Fuzzy Name + Amount + Date Window | `member_name` found in `narration` and amount/date window match | Name token match + ±3 days |

## 5. Business Rules
- Only reconcile backend bookings with `booking_status` in (`Confirmed`, `Refunded`). Exclude `Cancelled` unless a refund is present in bank statement.
- Refunds in bank statement (negative amounts) should be matched against backend `Refunded` bookings.
- Offline cash/cheque collections may appear in bank statement with delay; use ±7 day window for offline modes.
- Flag duplicate `payment_reference` values on either side before matching.
- Allow manual override mapping via a separate `manual_mapping.csv`.

## 6. Non-Functional Requirements
- Language: Python 3.10+
- Libraries: pandas, openpyxl, rapidfuzz, numpy
- Input formats: CSV and Excel (.xlsx)
- Output: Excel workbook + JSON audit log
- Config-driven: thresholds, date formats, and columns configurable via `config.yaml`
- CLI interface with arguments for input files and output path
- Unit tests for matching rules

## 7. Success Criteria
- >95% of exact-reference transactions auto-matched.
- All unmatched records clearly categorised with a reason code.
- Variance between bank total and backend total explained in the summary.
- Report generated in <30 seconds for up to 100,000 rows per side.

## 8. Reason Codes
- `MATCHED_EXACT_REF`
- `MATCHED_AMOUNT_DATE`
- `MATCHED_FUZZY_REF`
- `MATCHED_OFFLINE_WINDOW`
- `UNMATCHED_BANK_NO_BACKEND`
- `UNMATCHED_BACKEND_NO_BANK`
- `AMOUNT_MISMATCH`
- `DATE_MISMATCH`
- `DUPLICATE_REFERENCE`
- `MANUAL_OVERRIDE`
- `PENDING_REVIEW`
