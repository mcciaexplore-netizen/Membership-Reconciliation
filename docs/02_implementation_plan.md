# Membership Reconciliation — Implementation Plan

## Phase 1: Project Setup & Data Ingestion
1. Create folder structure: `src/`, `data/`, `output/`, `tests/`, `config/`.
2. Install dependencies: `pandas`, `openpyxl`, `rapidfuzz`, `pyyaml`, `pytest`.
3. Build `ingest.py`:
   - Read CSV/Excel for both bank statement and backend data.
   - Normalise column names (snake_case).
   - Parse dates with multiple format fallbacks.
   - Clean amounts (remove currency symbols, commas, handle negatives/refunds).
   - Validate required columns and raise explicit errors.

## Phase 2: Pre-processing & Deduplication
1. Standardise `amount` to numeric.
2. Create composite keys:
   - `bank_key` = `txn_id` or `utr` or `reference_no`
   - `backend_key` = `payment_reference`
3. Detect duplicate keys on each side and output `duplicate_references` sheet.
4. Filter backend records:
   - Include `Confirmed` and `Refunded`.
   - Exclude `Cancelled` (unless paired with a refund in bank).
5. Tag refund transactions in bank (negative amount) and backend (`Refunded`).

## Phase 3: Matching Engine
Build `matcher.py` with rule-based pipeline:

```
For each rule in priority order:
    Find candidate pairs
    Score each pair
    Apply greedy 1:1 assignment (highest score first)
    Mark matched rows and remove from subsequent rules
```

Rules implemented:
1. Exact reference match + amount match.
2. Exact amount + exact date match.
3. Fuzzy reference match (rapidfuzz) + amount match.
4. Amount match + date window (±3 days online, ±7 days offline).
5. Fuzzy name-in-narration + amount + date window.

Scoring function combines:
- Reference similarity (0–1)
- Amount exactness (0 or 1)
- Date proximity (inverse of days difference)

## Phase 4: Output Generation
Build `reporter.py` to create Excel workbook:
- `Matched`
- `Unmatched Bank`
- `Unmatched Backend`
- `Partial / Discrepant`
- `Duplicates`
- `Summary`

Summary includes:
- Total bank credits, total backend collections
- Counts per reason code
- Variance (bank − backend)
- Breakdown by payment mode and sales channel

Also write `audit_log.json` with:
- Run timestamp
- Config used
- Rule match counts
- Unmatched reason distribution

## Phase 5: CLI & Config
Build `cli.py` using `argparse`:
```bash
python -m membership_reconciliation \
  --bank data/bank_statement.csv \
  --backend data/backend_memberships.xlsx \
  --config config/config.yaml \
  --output output/reconciliation_report.xlsx
```

`config.yaml` contains:
- Column mappings
- Date formats
- Date tolerance windows
- Fuzzy-match thresholds
- Currency settings

## Phase 6: Testing
- Unit tests for each matching rule.
- Integration test with sample data.
- Edge cases: duplicates, refunds, offline delays, missing columns.

## Phase 7: Documentation & Handover
- README with setup and run instructions.
- Gap analysis document.
- Sample data generator.

## Timeline (Indicative)
| Phase | Effort |
|---|---|
| 1 — Setup & ingestion | 1 day |
| 2 — Pre-processing | 1 day |
| 3 — Matching engine | 3 days |
| 4 — Reporting | 2 days |
| 5 — CLI & config | 1 day |
| 6 — Testing | 2 days |
| 7 — Docs & handover | 1 day |
| **Total** | **~11 days** |
