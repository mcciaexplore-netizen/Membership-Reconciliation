"""Data ingestion and normalisation for membership reconciliation."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd
import yaml


def load_config(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    new_cols = []
    seen = {}
    for c in df.columns:
        norm = re.sub(r"[^0-9a-zA-Z]+", "_", str(c).strip()).strip("_").lower()
        if not norm or norm == "nan":
            norm = "unnamed"
        if norm in seen:
            seen[norm] += 1
            new_cols.append(f"{norm}_{seen[norm]}")
        else:
            seen[norm] = 0
            new_cols.append(norm)
    df.columns = new_cols
    return df


def map_columns(df: pd.DataFrame, aliases: dict[str, list[str]]) -> pd.DataFrame:
    df = df.copy()
    reverse_map: dict[str, str] = {}
    for canonical, alias_list in aliases.items():
        for alias in alias_list:
            alias_norm = alias.lower().replace(" ", "_")
            if alias_norm in df.columns and alias_norm not in reverse_map:
                reverse_map[alias_norm] = canonical
                break  # Only map the first matched alias to avoid duplicate column names
    return df.rename(columns=reverse_map)


def parse_dates(series: pd.Series, formats: list[str]) -> pd.Series:
    parsed = pd.to_datetime(series, errors="coerce", dayfirst=True)
    if parsed.notna().all():
        return parsed
    for fmt in formats:
        attempt = pd.to_datetime(series, format=fmt, errors="coerce")
        parsed = parsed.fillna(attempt)
    return parsed


def clean_amount(series: pd.Series) -> pd.Series:
    cleaned = (
        series.astype(str)
        .str.replace(r"[^0-9.\-]", "", regex=True)
        .replace("", "0")
    )
    return pd.to_numeric(cleaned, errors="coerce")


def read_input(path: str | Path, config_section: dict[str, Any]) -> pd.DataFrame:
    path = Path(path)
    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    elif path.suffix.lower() in (".xlsx", ".xls"):
        # Read first sheet, skip header rows for Tally exports
        df = pd.read_excel(path, sheet_name=0, header=None)
        # Detect if this is a Tally-style export with header rows
        # Find the row with "Date" or "Particulars" or actual headers
        for i in range(min(15, len(df))):
            row_vals = [str(v).strip().lower() if pd.notna(v) else "" for v in df.iloc[i]]
            if any(h in row_vals for h in ["date", "particulars", "voucher", "bk_no", "amount_paid"]):
                df = pd.read_excel(path, sheet_name=0, header=i)
                break
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")

    df = normalise_columns(df)
    df = map_columns(df, config_section["column_aliases"])

    missing = [c for c in config_section["required_columns"] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Found: {list(df.columns)}")

    # Handle amount
    if "amount_paid" in df.columns:
        df["amount"] = clean_amount(df["amount_paid"])
    elif "value" in df.columns:
        val_series = df["value"]
        if "gross_total" in df.columns:
            val_series = val_series.fillna(df["gross_total"])
        df["amount"] = clean_amount(val_series)
    else:
        df["amount"] = clean_amount(df["amount"])

    # Handle date
    date_col = "payment_date" if "payment_date" in config_section["required_columns"] else "date"
    df[date_col] = parse_dates(df[date_col], config_section["date_formats"])

    # Drop rows with unparseable dates or amounts
    df = df.dropna(subset=[date_col, "amount"]).copy()

    # Normalise payment mode / status
    for col in ["payment_mode", "voucher_type", "payment_status"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.lower()

    return df


def load_bank_statement(path: str | Path, config: dict[str, Any]) -> pd.DataFrame:
    return read_input(path, config["bank_statement"])


def load_backend_data(path: str | Path, config: dict[str, Any]) -> pd.DataFrame:
    return read_input(path, config["backend_data"])
