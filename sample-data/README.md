# SarvaFlow Universal Ingestion Mock Dataset

This directory contains a generalized, production-realistic test dataset covering multiple industry domains (Manufacturing, Software/SaaS, AI/Compute-Intensive, General Services) across small business through large enterprise scales.

## Document Directory & Test Targets

| File Name | Industry Context | Document Type | Purpose / Test Scenario |
| :--- | :--- | :--- | :--- |
| `inv_01_clean_hardware_supplier.txt` | Manufacturing | Supplier Invoice | Clean digital AP invoice with unit costs & 2/10 Net 30 terms |
| `inv_02_scanned_skewed_logistics.txt` | Manufacturing | Freight Invoice | Scanned/skewed logistics bill to test OCR tilt tolerance |
| `inv_03_photo_paper_receipt.txt` | General | Paper Receipt | Mobile photo receipt with handwritten approval annotation |
| `inv_04_saas_billing_export.csv` | Software/SaaS | SaaS Invoice | CSV export of multi-seat SaaS subscription billing |
| `inv_05_messy_repair_service.txt` | General | Service Invoice | Messy low-contrast scan with poor lighting & smudged text |
| `bom_01_simple_assembly.csv` | Manufacturing | Bill of Materials | 1-tier hardware assembly BOM (casing, screws, PCB) |
| `bom_02_mid_complexity_drone.json` | Manufacturing | Bill of Materials | Mid-complexity robotics assembly with unit cost breakdown |
| `bom_03_multitier_industrial_server.json` | Manufacturing | Bill of Materials | Multi-tier server rack BOM with sub-assemblies & raw silicon |
| `po_01_raw_metal_stock.json` | Manufacturing | Purchase Order | Standard raw aluminum stock PO matching supplier terms |
| `po_02_electronic_components.json` | Manufacturing | Purchase Order | Microcontroller & sensor component purchase order |
| `po_03_price_variance_exception.json` | Manufacturing | Purchase Order | Price-variance exception test ($12,500 PO vs $14,800 Invoiced) |
| `cloud_01_compute_cluster_usage.json` | AI / Compute | Cloud Infra | Reserved + Spot GPU cluster compute hours & interconnect |
| `cloud_02_data_labeling_saas.json` | AI / Compute | Vendor Invoice | Data labeling/annotation service & high-bandwidth storage |
| `bank_01_operating_account.csv` | General | Bank Statement | 30-day operating bank feed export for cash reconciliation |
| `bank_02_interbank_swift.mt940` | General | Bank Statement | ISO MT940 SWIFT interbank statement with :61: & :86: fields |
| `payroll_01_q2_biweekly_run.csv` | General | Payroll Run | Biweekly payroll export covering FTE wages & 1099 contractors |

## Testing Usage Instructions
You can drop or select any file from this directory in the **Universal Financial Document Ingestion Engine** window to test automatic industry taxonomy classification, field-level extraction confidence scoring, side-by-side bounding box overlay, and the real-time correction-feedback loop.
