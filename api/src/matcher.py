"""Matching engine for bank statement vs backend membership data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from rapidfuzz import fuzz


@dataclass
class MatchResult:
    matched: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
    unmatched_bank: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
    unmatched_backend: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
    partial: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
    duplicates_bank: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
    duplicates_backend: pd.DataFrame = field(default_factory=lambda: pd.DataFrame())
    summary: dict[str, Any] = field(default_factory=dict)
    audit_log: dict[str, Any] = field(default_factory=dict)


def _is_offline(row: pd.Series, offline_modes: list[str]) -> bool:
    return str(row.get("payment_mode", "")).lower() in offline_modes


def _date_window(row_b: pd.Series, row_t: pd.Series, offline_modes: list[str]) -> int:
    return 7 if _is_offline(row_b, offline_modes) else 3


def _fuzzy_token_match(a: str, b: str) -> float:
    if pd.isna(a) or pd.isna(b):
        return 0.0
    return fuzz.token_sort_ratio(str(a), str(b))


def _name_in_narration(name: str, narration: str) -> bool:
    if pd.isna(name) or pd.isna(narration):
        return False
    name_tokens = set(str(name).lower().split())
    narr_tokens = set(str(narration).lower().split())
    if not name_tokens:
        return False
    return len(name_tokens & narr_tokens) >= min(2, len(name_tokens))


def _score_pair(b: pd.Series, t: pd.Series, config: dict[str, Any]) -> tuple[float, str]:
    offline_modes = config["matching"]["offline_modes"]
    ref_thresh = config["matching"]["fuzzy_reference_threshold"]

    amount_match = np.isclose(b["amount"], t["amount"], rtol=0, atol=0.01)

    date_diff = abs((b["date"] - t["payment_date"]).days)
    window = _date_window(b, t, offline_modes)
    date_ok = date_diff <= window

    ref_sim = _fuzzy_token_match(b.get("voucher_ref_no", ""), t.get("bk_no", ""))
    ref_sim_narr = _fuzzy_token_match(b.get("voucher_ref_no", ""), t.get("narration", ""))
    ref_sim = max(ref_sim, ref_sim_narr)

    name_match = _name_in_narration(b.get("particulars", ""), t.get("narration", ""))

    if ref_sim >= 99 and amount_match:
        return 100.0, "MATCHED_EXACT_REF"
    if amount_match and date_diff == 0:
        return 90.0, "MATCHED_AMOUNT_DATE"
    if ref_sim >= ref_thresh and amount_match:
        return 80.0, "MATCHED_FUZZY_REF"
    if amount_match and date_ok:
        return 70.0, "MATCHED_OFFLINE_WINDOW" if _is_offline(b, offline_modes) else "MATCHED_DATE_WINDOW"
    if name_match and amount_match and date_ok:
        return 60.0, "MATCHED_NAME_FUZZY"
    if ref_sim >= ref_thresh and not amount_match:
        return 30.0, "AMOUNT_MISMATCH"
    if ref_sim >= ref_thresh and not date_ok:
        return 20.0, "DATE_MISMATCH"

    return 0.0, "NO_MATCH"


def _find_duplicates(df: pd.DataFrame, key_col: str) -> pd.DataFrame:
    if key_col not in df.columns:
        return pd.DataFrame()
    dup_mask = df[key_col].duplicated(keep=False) & df[key_col].notna() & (df[key_col].astype(str) != "")
    return df[dup_mask].copy()


def reconcile(bank: pd.DataFrame, backend: pd.DataFrame, config: dict[str, Any]) -> MatchResult:
    result = MatchResult()

    result.duplicates_bank = _find_duplicates(bank, "bk_no")
    result.duplicates_backend = _find_duplicates(backend, "voucher_ref_no")

    if "voucher_type" in backend.columns:
        backend_work = backend[backend["voucher_type"].isin(["sales"])].copy()
    else:
        backend_work = backend.copy()

    backend_work["_backend_idx"] = backend_work.index

    bank_work = bank.copy()
    bank_work["_bank_idx"] = bank_work.index

    matched_records: list[dict] = []
    partial_records: list[dict] = []
    matched_bank_idx: set[int] = set()
    matched_backend_idx: set[int] = set()

    # Optimization: Pre-group by rounded amount to drastically reduce comparisons
    backend_work['amt_round'] = backend_work['amount'].round(2).fillna(-1)
    bank_work['amt_round'] = bank_work['amount'].round(2).fillna(-1)

    backend_grouped = dict(list(backend_work.groupby('amt_round')))
    bank_grouped = dict(list(bank_work.groupby('amt_round')))

    rule_reasons = [
        "MATCHED_EXACT_REF",
        "MATCHED_AMOUNT_DATE",
        "MATCHED_FUZZY_REF",
        "MATCHED_DATE_WINDOW",
        "MATCHED_OFFLINE_WINDOW",
        "MATCHED_NAME_FUZZY",
    ]

    all_candidates: list[tuple[float, int, int, str]] = []

    if not bank_work.empty and not backend_work.empty:
        for amt, b_group in backend_grouped.items():
            if amt not in bank_grouped:
                continue
            t_group = bank_grouped[amt]
            for b_idx, b_row in b_group.iterrows():
                for t_idx, t_row in t_group.iterrows():
                    score, matched_reason = _score_pair(b_row, t_row, config)
                    if score > 0 and matched_reason in rule_reasons:
                        all_candidates.append((score, b_idx, t_idx, matched_reason))

    rule_priority = {reason: i for i, reason in enumerate(rule_reasons)}
    all_candidates.sort(key=lambda x: (rule_priority.get(x[3], 99), -x[0]))

    for score, b_idx, t_idx, reason in all_candidates:
        if b_idx in matched_backend_idx or t_idx in matched_bank_idx:
            continue
        b_row = backend_work.loc[b_idx]
        t_row = bank_work.loc[t_idx]
        rec = {
            **{f"backend_{k}": v for k, v in b_row.items() if k != 'amt_round'},
            **{f"bank_{k}": v for k, v in t_row.items() if k != 'amt_round'},
            "match_score": score,
            "reason_code": reason,
        }
        matched_records.append(rec)
        matched_bank_idx.add(t_idx)
        matched_backend_idx.add(b_idx)

    remaining_bank = bank_work[~bank_work.index.isin(matched_bank_idx)]
    remaining_backend = backend_work[~backend_work.index.isin(matched_backend_idx)]

    import re
    def get_digits(s): 
        return re.sub(r'\D', '', str(s))

    remaining_bank['digits'] = remaining_bank.get('bk_no', pd.Series(dtype=str)).apply(get_digits)
    remaining_backend['digits'] = remaining_backend.get('voucher_ref_no', pd.Series(dtype=str)).apply(get_digits)

    for b_idx, b_row in remaining_backend.iterrows():
        b_digits = b_row['digits']
        if not b_digits:
            continue

        if len(b_digits) >= 4:
            t_cands = remaining_bank[remaining_bank['digits'].str.contains(b_digits[-4:], na=False, regex=False) | (remaining_bank['digits'] == b_digits)]
        else:
            t_cands = remaining_bank[remaining_bank['digits'] == b_digits]

        for t_idx, t_row in t_cands.iterrows():
            score, reason = _score_pair(b_row, t_row, config)
            if reason in ("AMOUNT_MISMATCH", "DATE_MISMATCH"):
                partial_records.append({
                    **{f"backend_{k}": v for k, v in b_row.items() if k not in ('digits', 'amt_round', '_backend_idx')},
                    **{f"bank_{k}": v for k, v in t_row.items() if k not in ('digits', 'amt_round', '_bank_idx')},
                    "match_score": score,
                    "reason_code": reason,
                })
                break

    result.matched = pd.DataFrame(matched_records)
    result.partial = pd.DataFrame(partial_records)

    result.unmatched_bank = bank[~bank.index.isin(matched_bank_idx)].copy()
    result.unmatched_bank["reason_code"] = "UNMATCHED_BANK_NO_BACKEND"

    result.unmatched_backend = backend[~backend.index.isin(matched_backend_idx)].copy()
    result.unmatched_backend["reason_code"] = "UNMATCHED_BACKEND_NO_BANK"

    total_bank = bank["amount"].sum() if "amount" in bank.columns else 0.0
    total_backend = backend_work["amount"].sum() if "amount" in backend_work.columns else 0.0
    matched_total = result.matched["bank_amount"].sum() if not result.matched.empty and "bank_amount" in result.matched.columns else 0.0

    result.summary = {
        "total_bank_amount": round(total_bank, 2),
        "total_backend_amount": round(total_backend, 2),
        "variance": round(total_bank - total_backend, 2),
        "matched_count": len(result.matched),
        "matched_amount": round(matched_total, 2),
        "unmatched_bank_count": len(result.unmatched_bank),
        "unmatched_backend_count": len(result.unmatched_backend),
        "partial_count": len(result.partial),
        "duplicate_bank_count": len(result.duplicates_bank),
        "duplicate_backend_count": len(result.duplicates_backend),
    }

    result.audit_log = {
        "rule_counts": result.matched["reason_code"].value_counts().to_dict()
        if not result.matched.empty else {},
        "unmatched_reasons": {
            "bank": result.unmatched_bank["reason_code"].value_counts().to_dict()
            if not result.unmatched_bank.empty else {},
            "backend": result.unmatched_backend["reason_code"].value_counts().to_dict()
            if not result.unmatched_backend.empty else {},
        },
    }

    return result
