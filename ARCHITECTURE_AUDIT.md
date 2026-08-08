# SarvaFlow End-to-End Architecture Audit & Data Flow Map

**Author:** Principal Senior Architect & Lead Engineer  
**Scope:** SarvaFlow System Architecture, Data Flows, Entity Inventory, Fallback Audits & Real-Time Synchronization Gaps  
**Target Repository:** `c:\Users\shubh\OneDrive\Documents\SARVA Intelligence` / `sarvaflow`

---

## Executive Summary

This architecture audit reverse-engineers SarvaFlow end-to-end to establish an empirical, code-grounded map of data ingestion, OCR/document classification, entity management, KPI calculations, and real-time frontend rendering. 

---

## Section 1: Data Flow Map (Document Ingestion to Dashboard Render)

Below is the step-by-step trace of a single uploaded document from user selection to UI render, identifying every file, function, endpoint, and mock/stub hop.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ HOP 1: Frontend Upload Handler                                                          │
│ File: frontend/src/main.tsx                                                            │
│ Functions: handleCustomLocalFileSelect() [L349] -> handleUniversalFileUpload() [L285]  │
│ Action: Reads file via FileReader API. Binary (.pdf/.png) uses readAsDataURL(), text   │
│         (.csv/.json) uses readAsText().                                                │
│ Status: REAL (Dynamic client reader)                                                   │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │ HTTP POST multipart / JSON payload
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ HOP 2: API Ingestion Route                                                             │
│ File: backend/app/api/v1/sample_data.py                                                │
│ Function / Endpoint: POST /api/v1/sample-data/ingest-document -> ingest_custom_doc() │
│ Action: Receives IngestDocumentRequest, validates payload, invokes classifier engine. │
│ Status: REAL (FastAPI Route)                                                           │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │ Direct In-Memory Call
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ HOP 3: Taxonomy Classifier & Content Normalizer                                        │
│ File: backend/app/domain/connectors/document_classifier.py                             │
│ Class/Function: UniversalDocumentClassifierEngine._normalize_content() [L55]          │
│                 UniversalDocumentClassifierEngine.classify_and_extract() [L72]         │
│ Action: Decodes Base64 Data URLs, normalizes text stream, executes regex keyword       │
│         taxonomy classifier across 8 industry domains.                                 │
│ Status: MIXED (Real regex matching; falls back to "GENERAL / CROSS-INDUSTRY" [L101])   │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │ Content Processing
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ HOP 4: Field Extractor & Confidence Scorer                                             │
│ File: backend/app/domain/connectors/document_classifier.py                             │
│ Lines: L125-L238                                                                       │
│ Action: Extracts Vendor (re.search [L127]), Total Amount (re.findall [L146]), Date     │
│         (re.search [L167]), and Line Items. Calculates dynamic confidence score.       │
│ Status: MIXED (Real regex extraction; falls back to static defaults if regex fails)    │
│         - Fallback Amount: $30,450.00 [L164]                                           │
│         - Fallback Date: "2026-08-01" [L168]                                           │
│         - Fallback Line Items: "Primary / Secondary Allocation Line" [L181-184]        │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │ JSON Payload
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ HOP 5: Database Write & Disk Persistence                                                │
│ File: backend/app/domain/connectors/document_classifier.py                             │
│ File Target: backend/app/domain/connectors/persistent_ingestion_db.json               │
│ Function: UniversalDocumentClassifierEngine._save_persistent_state() [L43]            │
│ Action: Appends extracted document result to _ingested_documents array and flushes to  │
│         JSON file on disk to survive server process restarts.                          │
│ Status: REAL (Disk Persistence)                                                        │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │ HTTP 200 JSON Response
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ HOP 6: Frontend State Updates & Event Dispatch                                         │
│ File: frontend/src/main.tsx                                                            │
│ Functions: setBatchQueue() [L302] -> synchronizeAllTabsForDocument() [L348]           │
│ Action: Appends new batch item to queue, updates React state, triggers SSE monitoring  │
│         refreshes.                                                                     │
│ Status: REAL (React State Sync)                                                        │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │ DOM Diff Render
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ HOP 7: Dashboard Render                                                                │
│ File: frontend/src/main.tsx                                                            │
│ Components: Batch Queue Table [L975-1030], KPI Scorecards, Side-by-Side Inspector      │
│ Action: Renders extracted fields, bounding box overlays, and status badges.            │
│ Status: REAL (React DOM Render)                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Section 2: Entity Inventory & Data Origin Matrix

Below is every distinct entity displayed on the SarvaFlow dashboard, detailing its exact data origin.

| Entity Type | Dashboard Component | Current Data Origin | Calculation Method / File & Line | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Ingested Documents** | Ingestion Hub Batch Queue Table | `persistent_ingestion_db.json` & React `batchQueue` state | In-Memory `_ingested_documents` array loaded from JSON store on startup (`document_classifier.py` L37) | **LIVE PERSISTED** |
| **Invoices (AP/AR)** | Ingestion Queue & 3-Way Match | Regex Extracted or Default Fallback | Extracted via `document_classifier.py` L125-165. Extracted amount/vendor written to disk | **PARTIAL FALLBACK** |
| **Purchase Orders (POs)** | Multi-Agent Mesh & Unified Trace | `unified-trace` endpoint in `sample_data.py` L124 | Hardcoded trace `TRC-2026-991` (PO-2026-EX-882, Titan Industrial Tooling Ltd) in `sample_data.py` L125-134 | **HARDCODED MOCK** |
| **Bank Statements & MT940** | Reconciliation Tab & Ingestion Queue | Regex Extracted & Plaid Sandbox Connector | Extracted via `document_classifier.py` L82-84 & Plaid webhook receiver `plaid.py` L52-60 | **LIVE INTEGRATED** |
| **Multi-Agent Mesh States** | Agent Mesh Execution Cards | React `agentMeshList` state in `main.tsx` L70-130 | SSE event stream (`GET /stream-events`) or client trigger function | **LIVE STREAMED** |
| **AI Health Scorecard** | Executive Overview Health Card | `health_score.py` L11-28 | **HARDCODED CONSTANT**: Score = `94`, Rating = `"EXCELLENT"`, Runway = `"18.4 Months"` in `health_score.py` L14-21 | **HARDCODED STUB** |
| **Liquid Cash Reserves** | Executive Overview KPI Card | React `healthScorecard` state ($42.95M) | Static initial state value in `main.tsx` L145 | **STATIC CONSTANT** |
| **90-Day Cash Forecast** | Cash Flow Projection Chart | `forecasting/service.py` L46-134 | **COMPUTED**: Calculates 90-day daily p10/p50/p90 projections from base parameters | **LIVE COMPUTED** |
| **Risk Flags & Exceptions** | Risk Monitoring Widget | `unified-trace` endpoint in `sample_data.py` L121 | Hardcoded JSON list in `sample_data.py` L123-158 | **HARDCODED MOCK** |
| **Bilateral Netting Summary**| Tier-1 Ops Netting Card | `tier1_ops/bilateral_netting.py` L15-45 | **COMPUTED**: Sums gross intercompany invoices and calculates fee savings | **LIVE COMPUTED** |

---

## Section 3: Default / Fallback Path Audit

Below is the complete audit of every location where default or fallback values are returned instead of real extracted/computed data.

### 1. Document Taxonomy Classification Fallback
* **Location**: `backend/app/domain/connectors/document_classifier.py`, Line 101–102
* **Trigger Condition**: When an uploaded document contains no matching keywords for Payroll, Bank MT940, PO Match, Deduplication, Hardware BOM, AI Compute, or SaaS.
* **Fallback Output**:
  ```python
  industry_domain = explicit_domain or "GENERAL / CROSS-INDUSTRY"
  doc_category = "General AP/AR Invoice"
  ```
* **Impact**: Unrecognized document formats default to `"GENERAL / CROSS-INDUSTRY"`.

### 2. Extracted Field Fallbacks (Amount, Date, Line Items)
* **Location**: `backend/app/domain/connectors/document_classifier.py`, Lines 164, 168, 181–184
* **Trigger Condition**: When regex patterns fail to extract structured amounts or dates from messy/unstructured text files.
* **Fallback Outputs**:
  * **Amount Fallback** (Line 164): `30450.00`
  * **Date Fallback** (Line 168): `"2026-08-01"`
  * **Line Items Fallback** (Line 181–184):
    ```python
    line_items = [
        {"line_number": 1, "description": f"Primary {doc_category} Allocation Line", "amount_usd": round(total_amount * 0.7, 2)},
        {"line_number": 2, "description": "Secondary Operational Line Item", "amount_usd": round(total_amount * 0.3, 2)}
    ]
    ```
* **Root Cause of the "Guessed Taxonomy / Hardcoded Value" Bug**: When document text parsing yields no regex match, the engine silently assigns fallback values without flagging that real extraction failed.

### 3. AI Financial Health Scorecard Hardcoded Stub
* **Location**: `backend/app/domain/cfo_copilot/health_score.py`, Lines 14–26
* **Trigger Condition**: Every call to `GET /api/v1/sample-data/health-scorecard`.
* **Fallback Output**: Returns static dictionary (`overall_health_score: 94`, `total_captured_value_usd: 152500.00`).
* **Impact**: The executive health score does not dynamically recalculate based on real ingested document totals unless explicitly overridden in React state.

### 4. Static Demo Batch Queue Items
* **Location**: `frontend/src/main.tsx`, Lines 173–270
* **Trigger Condition**: Initial app mount.
* **Fallback Output**: Pre-loads 3 demo items (`batch-01`, `batch-02`, `batch-03`).
* **Impact**: Initial items present hardcoded values (`$30,450.00`, `$11,671.60`, `$485,000.00`).

---

## Section 4: Real-Time Gap Audit

| Dashboard Component / Entity | Updates Live via SSE/Sockets? | Refresh Mechanism | Root Cause / Technical Gap |
| :--- | :--- | :--- | :--- |
| **Agent Mesh Execution Badges** | **YES** | SSE Stream (`/api/v1/monitoring/stream-events`) & Client Event Bus | Connected to `EventSource` listener in `main.tsx` L490. Updates badges without page reload. |
| **Batch Processing Queue Table** | **YES (POST Response)** | React `setBatchQueue` state update on upload completion | Synchronized immediately when `POST /ingest-document` returns. |
| **Executive Health Score Card** | **NO** | Client React state mutation | Backend `health_score.py` returns static JSON. Requires explicit state dispatcher call. |
| **Liquid Cash Reserves KPI** | **NO** | Manual Page Reload or Explicit Ingestion Trigger | Value stored in local React state `$42,950,000.00`. Does not auto-subscribe to DB changes. |
| **90-Day Cash Forecast Baseline** | **PARTIAL** | Triggered only on Payroll upload | Recalibrates payroll expense baseline when payroll file uploaded; otherwise static. |
| **Unified Anomaly Risk Traces** | **NO** | Manual Fetch (`loadAccuracyAndTraceData()`) | `GET /unified-trace` polled on demand; no server push event on new exception detection. |
| **Persistent Ingestion Audit Log** | **YES (Client Side)** | Appended in React `synchronizeAllTabsForDocument` | Client appends log entries immediately upon document upload response. |

---

## Architectural Recommendations for Phase 2 & Phase 3

1. **Phase 2 (Live Per-Entity Dashboard Updates)**:
   * Expand the SSE stream in `backend/app/api/v1/monitoring.py` to broadcast granular per-entity event channels:
     * `DOCUMENT_EXTRACTED` (with `file_name`, `entity_type`, `impact_kpi`)
     * `CASH_RESERVES_UPDATED` (with updated total)
     * `FORECAST_RECALIBRATED` (with new baseline)
   * Add per-card "Last updated by [Filename] at [Time]" indicators in `frontend/src/main.tsx`.

2. **Phase 3 (Quarantine Default-Extraction Documents)**:
   * Introduce explicit code-level marker `is_fallback_extraction: bool` in `UniversalDocumentClassifierEngine`.
   * When regex matching fails and defaults trigger, set `is_fallback_extraction = True` and `status = "Needs Reprocessing"`.
   * Exclude quarantined items from KPI aggregates, agent mesh inputs, and cash forecast baselines.
   * Add a 1-click **"Reprocess Document"** action button in the Ingestion Hub queue.

---

*End of Architecture Audit Document.*
