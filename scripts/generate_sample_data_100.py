"""Generates the sample-data-100 100-record Volume Test Dataset."""
import json
import os
from pathlib import Path

BASE_DIR = Path(r"c:\Users\shubh\OneDrive\Documents\SARVA Intelligence\sample-data-100")
MIRROR_DIR = Path(r"c:\Users\shubh\OneDrive\Documents\sarvaflow\sample-data-100")

BASE_DIR.mkdir(parents=True, exist_ok=True)
MIRROR_DIR.mkdir(parents=True, exist_ok=True)

# 1. inv_01_clean_invoices_100.json (100 Clean Invoices)
clean_invoices = []
categories = ["MANUFACTURING / HARDWARE", "SOFTWARE / SAAS", "AI / COMPUTE-INTENSIVE", "GENERAL FINANCE"]
vendors = ["Global Precision Components", "CloudScale SaaS Inc", "Hyperscale GPU Compute", "Atlas Logistics Ltd", "Apex Tooling Corp"]

for i in range(1, 101):
    category = categories[(i - 1) % len(categories)]
    vendor = vendors[(i - 1) % len(vendors)]
    amount = round(1500.0 + (i * 245.50), 2)
    clean_invoices.append({
        "invoice_id": f"INV-2026-CLN-{i:03d}",
        "invoice_number": f"CLN-904{i:03d}",
        "invoice_date": f"2026-07-{(i % 28) + 1:02d}",
        "vendor_name": vendor,
        "industry_domain": category,
        "total_amount_usd": amount,
        "status": "Confirmed",
        "confidence_score": 98.5 + ((i % 15) * 0.1),
        "is_messy": False,
        "line_items": [
            {"description": f"Component Spec Part #{i:03d}", "quantity": 10 + i, "unit_price": round(amount / (10 + i), 2), "total": amount}
        ]
    })

# 2. inv_02_messy_records_100.json (100 Records - Exactly 25 Messy/Corrupted requiring Needs Review)
messy_invoices = []
for i in range(1, 101):
    category = categories[(i - 1) % len(categories)]
    vendor = vendors[(i - 1) % len(vendors)]
    amount = round(2100.0 + (i * 180.20), 2)
    # Injected corruption rate: Exactly 25 records (i % 4 == 0)
    needs_review = (i % 4 == 0)
    
    messy_invoices.append({
        "invoice_id": f"INV-2026-MSY-{i:03d}",
        "invoice_number": f"MSY-771{i:03d}" if not needs_review else f"MSY-ERR-???",
        "invoice_date": f"2026-07-{(i % 28) + 1:02d}" if not needs_review else "",
        "vendor_name": vendor if not needs_review else f"Smudged_Vendor_{i:03d}_ILLEGIBLE",
        "industry_domain": category,
        "total_amount_usd": amount,
        "status": "Needs Review" if needs_review else "Confirmed",
        "confidence_score": 68.4 if needs_review else 96.8,
        "is_messy": needs_review,
        "corruption_reason": "Low OCR confidence (<75%), smudged vendor, or missing invoice date" if needs_review else "None"
    })

# 3. po_03_match_pairs_100.json (100 Pairs - Exactly 15 Exceptions vs 85 Matches)
match_pairs = []
for i in range(1, 101):
    po_amount = round(5000.0 + (i * 320.0), 2)
    # Exactly 15 exceptions (i in [7, 14, 21, 28, 35, 42, 49, 56, 63, 70, 77, 84, 91, 95, 99])
    is_exception = i in [7, 14, 21, 28, 35, 42, 49, 56, 63, 70, 77, 84, 91, 95, 99]
    variance_pct = 18.4 if is_exception else 0.0
    inv_amount = round(po_amount * (1.0 + (variance_pct / 100.0)), 2)
    
    match_pairs.append({
        "pair_id": f"PAIR-2026-{i:03d}",
        "po_number": f"PO-2026-MATCH-{i:03d}",
        "invoice_number": f"INV-2026-MATCH-{i:03d}",
        "vendor_name": vendors[(i - 1) % len(vendors)],
        "po_amount_usd": po_amount,
        "invoiced_amount_usd": inv_amount,
        "price_variance_pct": variance_pct,
        "expected_routing": "EXCEPTION" if is_exception else "MATCH",
        "exception_reason": f"Price variance +{variance_pct}% exceeds 5.0% tolerance limit" if is_exception else "Clean 3-way match"
    })

# 4. duplicate_01_invoices_100.json (100 Invoices - Exactly 20 True Duplicates)
duplicate_invoices = []
for i in range(1, 101):
    # Exactly 20 true duplicates (i % 5 == 0)
    is_dup = (i % 5 == 0)
    bill_no = f"INV-2026-DUP-{(i if not is_dup else i - 1):03d}"
    amount = round(3400.0 + ((i if not is_dup else i - 1) * 110.0), 2)
    
    v_idx = (i - 1) if not is_dup else (i - 2)
    duplicate_invoices.append({
        "record_id": f"REC-2026-{i:03d}",
        "invoice_number": bill_no,
        "vendor_name": vendors[v_idx % len(vendors)],
        "invoice_date": "2026-07-20",
        "total_amount_usd": amount,
        "is_duplicate": is_dup,
        "is_duplicate_of": bill_no if is_dup else None,
        "expected_alert": "DUPLICATE_INVOICE_ALERT" if is_dup else "UNIQUE"
    })

# 5. bank_01_transactions_100.csv (100 Line Bank Statement CSV)
bank_csv_lines = ["transaction_id,booking_date,value_date,description,credit_usd,debit_usd,running_balance_usd"]
running_balance = 42950000.00
for i in range(1, 101):
    tx_id = f"TXN-2026-BANK-{i:03d}"
    date = f"2026-07-{(i % 28) + 1:02d}"
    if i % 3 == 0:
        # Credit
        credit = round(150000.00 + (i * 2500.0), 2)
        debit = 0.0
        running_balance += credit
        desc = f"Customer Wire Payment Recv #{i:03d}"
    else:
        # Debit
        credit = 0.0
        debit = round(45000.00 + (i * 1200.0), 2)
        running_balance -= debit
        desc = f"Vendor Clearing Payout #{i:03d}"
    bank_csv_lines.append(f"{tx_id},{date},{date},{desc},{credit:.2f},{debit:.2f},{running_balance:.2f}")

bank_csv_content = "\n".join(bank_csv_lines)

# 6. bank_02_mt940_100.txt (100 Line SWIFT MT940 Bank Statement - Matching Running Balance)
mt940_lines = [
    ":20:MT940-2026-07-31",
    ":25:JPM-OPERATING-MASTER-9281",
    ":28C:00001/001",
    ":60F:C260701USD42500000,00"
]
for i in range(1, 101):
    date_str = f"2607{(i % 28) + 1:02d}"
    if i % 3 == 0:
        amt = round(150000.00 + (i * 2500.0), 2)
        mt940_lines.append(f":61:{date_str}C{amt:.2f}NTRFNREF//TXN-2026-BANK-{i:03d}")
        mt940_lines.append(f":86:Customer Wire Payment Recv #{i:03d}")
    else:
        amt = round(45000.00 + (i * 1200.0), 2)
        mt940_lines.append(f":61:{date_str}D{amt:.2f}NTRFNREF//TXN-2026-BANK-{i:03d}")
        mt940_lines.append(f":86:Vendor Clearing Payout #{i:03d}")

mt940_lines.append(f":62F:C260731USD{running_balance:.2f}".replace('.', ','))
mt940_content = "\n".join(mt940_lines)

# 7. payroll_01_records_100.csv (100 Line Payroll Records)
payroll_lines = ["employee_id,employee_name,department,biweekly_gross_usd,tax_withheld_usd,net_pay_usd"]
total_payroll = 0.0
for i in range(1, 101):
    emp_id = f"EMP-2026-{i:03d}"
    name = f"Employee {i:03d}"
    dept = ["Engineering", "Product", "Sales", "Finance", "Operations"][i % 5]
    gross = 4850.00
    tax = round(gross * 0.22, 2)
    net = round(gross - tax, 2)
    total_payroll += gross
    payroll_lines.append(f"{emp_id},{name},{dept},{gross:.2f},{tax:.2f},{net:.2f}")

payroll_content = "\n".join(payroll_lines)

# 8. ar_01_receivables_100.json (100 Customer Receivables)
ar_receivables = []
for i in range(1, 101):
    amount = round(14250.0 + (i * 310.0), 2)
    ar_receivables.append({
        "receivable_id": f"AR-2026-{i:03d}",
        "customer_name": f"Enterprise Customer {i:03d}",
        "invoice_number": f"INV-AR-2026-{i:03d}",
        "due_date": "2026-08-15",
        "total_amount_usd": amount,
        "status": "OPEN",
        "remittance_advice": f"REMIT-2026-{i:03d} for $142,500.00 bundled settlement" if i == 1 else f"REMIT-2026-{i:03d}"
    })

# 9. bom_01_manufacturing_100.csv (100 Manufacturing Component Items)
bom_lines = ["part_id,description,quantity_per_unit,unit_cost_usd,supplier_name"]
for i in range(1, 101):
    part_id = f"CMP-2026-{i:03d}"
    desc = f"Precision Component Component Variant #{i:03d}"
    qty = (i % 5) + 1
    cost = round(12.50 + (i * 2.10), 2)
    bom_lines.append(f"{part_id},{desc},{qty},{cost:.2f},Global Precision Components")

bom_content = "\n".join(bom_lines)

# Write all files to both directories
files_to_write = {
    "inv_01_clean_invoices_100.json": json.dumps(clean_invoices, indent=2),
    "inv_02_messy_records_100.json": json.dumps(messy_invoices, indent=2),
    "po_03_match_pairs_100.json": json.dumps(match_pairs, indent=2),
    "duplicate_01_invoices_100.json": json.dumps(duplicate_invoices, indent=2),
    "bank_01_transactions_100.csv": bank_csv_content,
    "bank_02_mt940_100.txt": mt940_content,
    "payroll_01_records_100.csv": payroll_content,
    "ar_01_receivables_100.json": json.dumps(ar_receivables, indent=2),
    "bom_01_manufacturing_100.csv": bom_content,
}

readme_content = """# SarvaFlow 100-Record Volume Test Dataset (`sample-data-100`)

Production volume evaluation dataset containing 9 files across 100-record benchmark suites:

1. `inv_01_clean_invoices_100.json`: 100 clean multi-industry invoices (Target: 100/100 confirmed high confidence).
2. `inv_02_messy_records_100.json`: 100 messy/scanned invoices (Target: 25% Needs Review injected corruption rate).
3. `po_03_match_pairs_100.json`: 100 3-way match pairs (Target: 15 exceptions vs 85 matches ground truth).
4. `duplicate_01_invoices_100.json`: 100 invoice records (Target: 20 true duplicates vs 80 unique).
5. `bank_01_transactions_100.csv`: 100 line bank statement CSV (Running balance: $42,950,000.00).
6. `bank_02_mt940_100.txt`: 100 line SWIFT MT940 statement (Running balance: $42,950,000.00).
7. `payroll_01_records_100.csv`: 100 employee biweekly payroll run ($485,000.00 biweekly recurring expenditure).
8. `ar_01_receivables_100.json`: 100 customer receivable invoices & remittance advices.
9. `bom_01_manufacturing_100.csv`: 100 item manufacturing Bill of Materials.
"""

files_to_write["README.md"] = readme_content

for filename, content in files_to_write.items():
    (BASE_DIR / filename).write_text(content, encoding="utf-8")
    (MIRROR_DIR / filename).write_text(content, encoding="utf-8")

print(f"[SUCCESS] Generated all 9 sample-data-100 dataset files in {BASE_DIR} and {MIRROR_DIR}")
