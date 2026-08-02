# SarvaFlow 100-Record Volume Test Dataset (`sample-data-100`)

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
