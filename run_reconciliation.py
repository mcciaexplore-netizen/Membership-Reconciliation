#!/usr/bin/env python3
"""Convenience runner: generate MCCIA-style sample data and reconcile."""

from pathlib import Path

from src.ingest import load_backend_data, load_bank_statement, load_config
from src.matcher import reconcile
from src.reporter import write_report
from src.sample_data_generator import generate


def main() -> None:
    base = Path(__file__).parent
    config = load_config(base / "config" / "config.yaml")

    bank_path, backend_path = generate(output_dir=base / "data")

    # For this schema, bank = payment summary, backend = invoice ledger
    bank = load_bank_statement(bank_path, config)
    backend = load_backend_data(backend_path, config)

    result = reconcile(bank, backend, config)
    output_path = base / "output" / "reconciliation_report.xlsx"
    write_report(result, output_path)

    print("\n=== Reconciliation Summary ===")
    for k, v in result.summary.items():
        print(f"{k}: {v}")
    print(f"\nReport saved to: {output_path.resolve()}")


if __name__ == "__main__":
    main()
