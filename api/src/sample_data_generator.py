"""Generate realistic MCCIA-style sample data."""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd


def _random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def generate(
    n_invoices: int = 80,
    n_payments: int = 80,
    seed: int = 42,
    output_dir: str | Path = "data",
) -> tuple[Path, Path]:
    random.seed(seed)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    start = datetime(2026, 7, 1)
    end = datetime(2026, 7, 31)

    companies = [
        "Hoonar Tekwurks Private Limited", "Akura Engineering Services", "AGARWAL PACKAGING PVT LTD",
        "RigBetel Labs", "Nanda Events", "INTELIMENT TECHNOLOGIES PRIVATE LIMITED",
        "PUNE CARBIDE", "Web Trans", "Mr. Milind Jape", "Anurag Advait Halbe",
        "Deepa Narayan Sawant", "Duncan and Ross Technology Engineering India Pvt Ltd",
        "Kevian Associates", "SUMA SOFT PRIVATE LIMITED", "VIRTUOSO PROJECTS ENGINEERS PRIVATE LIMITED",
        "FINEARC SYSTEMS PRIVATE LIMITED", "Indian Oxides and Chemicals Private Limited",
        "ACME FOUNDRY FLUX COMPANY", "AMOL R MANTRI AND ASSOCIATES", "V-Smart Thermotech Pvt. Ltd.",
        "Magna Automotive India Private Limited", "RADHA ENTERPRISES", "Ri Crystal",
        "Vishal Bharat Shah", "Hetal Amey Pawar", "VISHESH S KOCHHAR", "LVL ALPHA PRIVATE LIMITED",
        "Caxyzen Labs Private Limited", "SHIVRAI TECHNOLOGIES PRIVATE LIMITED", "VARUN PRESSINGS PRIVATE LIMITED",
        "AURIC TECHNO SERVICES PRIVATE LIMTED", "PRECIHOLE MACHINE TOOLS PVT LTD", "M-Tech Innovations Ltd.",
        "Shri Shinde Avinash J.", "Svireva", "Genintel Technologies Llp", "RUZAIN ENERGY PVT LTD",
        "ADVIK HI TECH PRIVATE LIM ITED", "BizPire Consulting LLP", "ACR PROJECT CONSULTANTS PVT. LTD.",
        "Vibrant India Economic Council", "ASHORE SYSTEMS PRIVATE LIMITED", "Kadant India Private Limited",
        "Lexon Winders", "SYSTOOLS SOFTWARE PRIVATE LIMITED", "INTEGRAL PROCESS CONTROLS INDIA PRIVATE LIMITED",
        "BUSINARY CONSULTANCY SERVICES LLP", "KIRLOSKAR EBARA PUMPS LIMITED", "Richie Agarwal",
        "SAS POWERTECH PVT LTD", "Vijaylaxmi Metal Industries", "Harnex Systems Private Limited",
        "Pixaflip Technologies Private Limited", "YASH INDUSTRIES - SHAMLI VINAY NAIK", "Sparkling Soul",
        "Shoonyas Ace LLP", "VEDA ENGINEERING PRIVATE LIMITED", "Stratgem Projects and Engineering Pvt. Ltd.",
        "Trimiti Industrial Solutions", "SAVEECO ENERGY INDIA PRIVATE LIMITED", "VECTOR INFORMATIK INDIA PRIVATE LIMITED",
        "Creliant Software Pvt. Ltd.", "Bellator Engineers India Private Limited", "BKM ENGINEERING SERVICES LLP",
        "Vijigeeshu QMS Pvt.Ltd", "Royal Agro Organic Pvt Ltd", "Jiangyin Uni-Pol Vacuum Casting India Pvt LTD",
        "Rising India Research Foundation", "Abhishan Logistics", "QUALITY CIRCLE FORUM OF INDIA",
        "ROOTWARE TECHNOLOGIES", "DOMETECH ART PRIVATE LIMITED", "Sunhim ecommerce", "SHREE BIOTECH",
        "SPARKLER PIEZOCERAMICS PVT LTD", "City Corporation Limited",
    ]

    membership_ids = [f"IA-{random.randint(1000, 15500)}" for _ in range(n_invoices)]
    base_fees = [5000, 10000, 12000, 15000, 25000, 30000, 35000, 45000, 50000, 60000, 75000]
    gst_rate = 0.18

    # --- Generate Backend Invoice Ledger (Tally-style) ---
    invoice_rows = []
    booking_numbers = []
    for i in range(n_invoices):
        company = random.choice(companies)
        base = random.choice(base_fees)
        cgst = round(base * gst_rate / 2, 2)
        sgst = round(base * gst_rate / 2, 2)
        total = round(base + cgst + sgst, 2)
        bk_no = f"MBK{str(3000000 + i).zfill(7)}"
        booking_numbers.append(bk_no)
        mem_id = membership_ids[i]
        inv_date = _random_date(start, end)
        voucher_no = 5400 + i

        invoice_rows.append({
            "Date": inv_date.strftime("%d-%b-%y"),
            "Particulars": company,
            "Buyer/Supplier": company,
            "Buyer/Supplier Address": f"Pune-{random.randint(411001, 411057)}",
            "Consignee/Party": company,
            "Consignee/Party Address": f"Pune-{random.randint(411001, 411057)}",
            "Voucher Type": "Sales",
            "Voucher No.": voucher_no,
            "Voucher Ref. No.": bk_no,
            "Voucher Ref. Date": inv_date.strftime("%d-%b-%y"),
            "GSTIN/UIN": f"27{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5))}{random.randint(1000, 9999)}Z{random.randint(1, 9)}",
            "PAN No.": f"{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=5))}{random.randint(1000, 9999)}",
            "Narration": f"BILL RAISED TOWARDS MEMBERSHIP FEE FOR YEAR:2026-2027. BOOKING NO -{bk_no} MEMBERSHIP -{mem_id}",
            "Value": total,
            "Gross Total": base,
            "26-27 MEMBERSHIP FEES": base,
            "Central Goods and Service Tax": cgst,
            "State Goods and Service Tax": sgst,
            "Integrated Goods and Service Tax": 0,
            "27-28 MEMBERSHIP FEE": 0,
            "28-29 MEMBERSHIP FEE": 0,
            "ONE TIME ENTRANCE FEES": 0,
        })

    invoices = pd.DataFrame(invoice_rows)

    # --- Generate Payment Summary (Backend Collections) ---
    payment_rows = []
    # 75% of invoices have payments
    paid_indices = set(random.sample(range(n_invoices), k=int(n_invoices * 0.75)))

    for idx in paid_indices:
        inv = invoice_rows[idx]
        base = inv["Gross Total"]
        total = inv["Value"]
        bk_no = inv["Voucher Ref. No."]
        pay_date = datetime.strptime(inv["Date"], "%d-%b-%y") + timedelta(days=random.randint(-2, 5))

        # Payment modes: 10=cheque, 11=cash, 13=NEFT/online, 20=other
        mode = random.choice([10, 11, 13, 20])
        mode_str = {10: "cheque", 11: "cash", 13: "neft", 20: "other"}[mode]

        # Occasionally partial payment or amount mismatch
        paid_amount = total
        if random.random() < 0.05:
            paid_amount += random.choice([10, -10, 50, -50])

        # Bank reference
        if mode == 13:
            ref = f"NEFT{random.randint(100000000, 999999999)}"
        elif mode == 10:
            ref = f"CHQ{random.randint(100000, 999999)}"
        else:
            ref = f"REF{random.randint(100000, 999999)}"

        payment_rows.append({
            "id": 34000 + idx,
            "created_by": random.choice(["kirtik", "sonalp", "satishj", "aishwarys"]),
            "created_date": (pay_date - timedelta(days=1)).strftime("%Y-%m-%d"),
            "updated_by": None,
            "updated_date": None,
            "is_deleted": 0,
            "payment_sr_num": 1,
            "amount_payable": total,
            "amount_paid": round(paid_amount, 2),
            "balance": 0 if paid_amount >= total else round(total - paid_amount, 2),
            "cheque_no": ref if mode == 10 else None,
            "cheque_date": pay_date.strftime("%Y-%m-%d") if mode == 10 else None,
            "cash_amount": paid_amount if mode == 11 else 0,
            "is_cheque_bounce": 0,
            "cheque_bounce_charge": 0,
            "bank_name": random.choice(["HDFC BANK", "ICICI Bank", "Axis Bank", "SBI", "Bank of Baroda"]) if mode == 13 else None,
            "neft_transfer_id": ref if mode == 13 else None,
            "is_neft_failed": 0,
            "receipt_no": f"RCP{random.randint(100000, 999999)}",
            "receipt_date": pay_date.strftime("%Y-%m-%d"),
            "payment_mode": mode,
            "offline_payment_by": random.choice([10, 11, 13]) if mode in [10, 11] else None,
            "payment_date": pay_date.strftime("%Y-%m-%d"),
            "bk_no": bk_no,
            "is_other": 0,
            "payment_remark": f"Paid via {mode_str.upper()} for {bk_no}",
            "payment_status": 22 if paid_amount >= total else 21,
            "membership_id": random.randint(30000, 60000),
            "membership_invoice_id": random.randint(30000, 60000),
            "basic_amount": base,
            "is_tds": 0,
            "membership_slab_id": random.randint(500, 650),
            "subcat_value": base,
            "tds_amount": 0,
            "tally_processed": 1,
            "advance_tax_inoviced_raised": 0,
            "final_payment_status": 1 if paid_amount >= total else 0,
        })

    # Add unmatched payments (no corresponding invoice)
    for _ in range(n_payments - len(payment_rows)):
        pay_date = _random_date(start, end)
        bk_no = f"MBK{str(4000000 + random.randint(0, 999999)).zfill(7)}"
        base = random.choice(base_fees)
        total = round(base * 1.18, 2)
        payment_rows.append({
            "id": 35000 + random.randint(0, 9999),
            "created_by": "kirtik",
            "created_date": pay_date.strftime("%Y-%m-%d"),
            "updated_by": None,
            "updated_date": None,
            "is_deleted": 0,
            "payment_sr_num": 1,
            "amount_payable": total,
            "amount_paid": total,
            "balance": 0,
            "cheque_no": None,
            "cheque_date": None,
            "cash_amount": 0,
            "is_cheque_bounce": 0,
            "cheque_bounce_charge": 0,
            "bank_name": "HDFC BANK",
            "neft_transfer_id": f"NEFT{random.randint(100000000, 999999999)}",
            "is_neft_failed": 0,
            "receipt_no": f"RCP{random.randint(100000, 999999)}",
            "receipt_date": pay_date.strftime("%Y-%m-%d"),
            "payment_mode": 13,
            "offline_payment_by": None,
            "payment_date": pay_date.strftime("%Y-%m-%d"),
            "bk_no": bk_no,
            "is_other": 0,
            "payment_remark": f"Unmatched payment for {bk_no}",
            "payment_status": 22,
            "membership_id": random.randint(30000, 60000),
            "membership_invoice_id": random.randint(30000, 60000),
            "basic_amount": base,
            "is_tds": 0,
            "membership_slab_id": random.randint(500, 650),
            "subcat_value": base,
            "tds_amount": 0,
            "tally_processed": 1,
            "advance_tax_inoviced_raised": 0,
            "final_payment_status": 1,
        })

    # Duplicates disabled

    payments = pd.DataFrame(payment_rows).sample(frac=1, random_state=seed).reset_index(drop=True)
    invoices = pd.DataFrame(invoice_rows).sample(frac=1, random_state=seed).reset_index(drop=True)

    inv_path = output_dir / "sample_backend_invoices.csv"
    pay_path = output_dir / "sample_bank_payments.csv"
    invoices.to_csv(inv_path, index=False)
    payments.to_csv(pay_path, index=False)

    return pay_path, inv_path


if __name__ == "__main__":
    b, i = generate()
    print(f"Generated:\n  Bank/Payments: {b}\n  Backend/Invoices: {i}")
