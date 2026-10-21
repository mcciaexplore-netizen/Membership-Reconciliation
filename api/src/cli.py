"""Command-line interface for membership reconciliation."""

from __future__ import annotations

import argparse
from pathlib import Path

from .ingest import load_backend_data, load_bank_statement, load_config
from .matcher import reconcile
from .reporter import write_report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Reconcile bank statement membership transactions against backend bookings."
    )
    parser.add_argument("--bank", required=True, help="Path to bank statement CSV/Excel")
    parser.add_argument("--backend", required=True, help="Path to backend membership CSV/Excel")
    parser.add_argument("--config", default="config/config.yaml", help="Path to config YAML")
    parser.add_argument("--output", default="output/reconciliation_report.xlsx", help="Output Excel path")
    args = parser.parse_args()

    config = load_config(args.config)
    bank = load_bank_statement(args.bank, config)
    backend = load_backend_data(args.backend, config)

    result = reconcile(bank, backend, config)
    write_report(result, args.output)

    print("Reconciliation complete.")
    print(f"  Output: {Path(args.output).resolve()}")
    print(f"  Matched: {result.summary['matched_count']}")
    print(f"  Unmatched Bank: {result.summary['unmatched_bank_count']}")
    print(f"  Unmatched Backend: {result.summary['unmatched_backend_count']}")
    print(f"  Variance: {result.summary['variance']}")


if __name__ == "__main__":
    main()
