"""API endpoints for Financial System Connectors and Data Ingestion."""
from __future__ import annotations

import os
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from app.domain.connectors.service import DataSourceType, IngestionResult, IngestionService

router = APIRouter(prefix="/connectors", tags=["Connectors & Ingestion"])
ingestion_service = IngestionService()


class ZohoAuthRequest(BaseModel):
    tenant_id: UUID
    client_id: Optional[str] = "demo_zoho_client_id"
    client_secret: Optional[str] = "demo_zoho_client_secret"
    organization_id: Optional[str] = "987654321_ZOHO_IN"
    refresh_token: Optional[str] = "demo_zoho_refresh_token"


class QuickBooksSyncRequest(BaseModel):
    tenant_id: UUID
    realm_id: Optional[str] = "qb_sandbox_realm_9901"
    access_token: Optional[str] = "ey_qb_sandbox_access_token"
    environment: str = Field("sandbox", description="sandbox or production")


MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024  # 25MB Limit


@router.post("/csv", response_model=IngestionResult, status_code=status.HTTP_200_OK)
async def ingest_csv_file(
    tenant_id: UUID = Form(...),
    file: UploadFile = File(...)
) -> IngestionResult:
    """Upload and parse a financial CSV/Excel file into canonical transactions."""
    fn = file.filename.lower()
    if not (fn.endswith(".csv") or fn.endswith(".xlsx") or fn.endswith(".xls") or fn.endswith(".txt")):
        raise HTTPException(status_code=400, detail="Supported formats: CSV, XLSX, XLS, TXT")
    
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File size exceeds maximum allowed limit of 25MB")

    csv_text = contents.decode("utf-8", errors="ignore")
    return ingestion_service.process_csv_transactions(tenant_id=tenant_id, csv_content=csv_text, source_name="CSV_UPLOAD")


@router.post("/bank-statement", response_model=IngestionResult, status_code=status.HTTP_200_OK)
async def ingest_bank_statement_csv(
    tenant_id: UUID = Form(...),
    file: UploadFile = File(...)
) -> IngestionResult:
    """Upload and parse a Bank Statement CSV into canonical transactions."""
    fn = file.filename.lower()
    if not (fn.endswith(".csv") or fn.endswith(".xlsx") or fn.endswith(".txt")):
        raise HTTPException(status_code=400, detail="Supported bank statement formats: CSV, XLSX, TXT")
    
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File size exceeds maximum allowed limit of 25MB")

    csv_text = contents.decode("utf-8", errors="ignore")
    return ingestion_service.process_csv_transactions(tenant_id=tenant_id, csv_content=csv_text, source_name="BANK_STATEMENT_CSV")


@router.post("/zoho", response_model=IngestionResult, status_code=status.HTTP_200_OK)
async def sync_zoho_books(req: ZohoAuthRequest) -> IngestionResult:
    """Connect & Sync Zoho Books (Self-Client OAuth2 / Mock Mode)."""
    # Realistic Zoho Books payload (Invoices, Contacts, Expenses mapped into NormalizedDataSource)
    mock_zoho_payload = {
        "invoices": [
            {
                "invoice_id": "ZH-INV-1001",
                "invoice_number": "INV-2026-ZB-01",
                "customer_name": "Reliance Retail Operations India",
                "date": "2026-08-01",
                "due_date": "2026-08-31",
                "total": 450000.00,
                "currency_code": "INR",
                "gst_no": "27AAACR5432E1Z2",
                "line_items": [{"description": "Retail SaaS & Terminal License Fee", "rate": 450000.00, "quantity": 1}]
            },
            {
                "invoice_id": "ZH-INV-1002",
                "invoice_number": "INV-2026-ZB-02",
                "customer_name": "Tata Digital Logistics",
                "date": "2026-08-05",
                "due_date": "2026-09-04",
                "total": 280000.00,
                "currency_code": "INR",
                "gst_no": "27AAACT9876F1Z5",
                "line_items": [{"description": "Supply Chain Analytics Platform", "rate": 280000.00, "quantity": 1}]
            }
        ],
        "contacts": [
            {
                "contact_name": "Reliance Retail Operations India",
                "company_name": "Reliance Retail Ltd",
                "contact_type": "customer",
                "email": "ap@relianceretail.example.in",
                "phone": "+91-22-6000-1111",
                "gst_no": "27AAACR5432E1Z2"
            },
            {
                "contact_name": "Infosys Cloud Infra Vendor",
                "company_name": "Infosys BPM Technologies",
                "contact_type": "vendor",
                "email": "ar@infosys.example.in",
                "phone": "+91-80-2852-0261",
                "gst_no": "29AAACI1234A1Z9"
            }
        ],
        "expenses": [
            {
                "account_name": "Cloud Data Center Hosting (AWS India)",
                "amount": 125000.00,
                "currency_code": "INR",
                "date": "2026-08-03",
                "description": "AWS Mumbai Region EC2 & RDS Infrastructure",
                "vendor_name": "Amazon Web Services India Pvt Ltd"
            }
        ]
    }
    return ingestion_service.process_zoho_payload(tenant_id=req.tenant_id, payload=mock_zoho_payload)


@router.post("/tally", response_model=IngestionResult, status_code=status.HTTP_200_OK)
async def ingest_tally_export_file(
    tenant_id: UUID = Form(...),
    file: UploadFile = File(...)
) -> IngestionResult:
    """Ingest Tally XML / Excel Voucher Export (Tally Prime v1)."""
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File size exceeds maximum allowed limit of 25MB")

    text_content = contents.decode("utf-8", errors="ignore")
    return ingestion_service.process_tally_export(tenant_id=tenant_id, file_name=file.filename, content=text_content)


@router.post("/quickbooks-webhook", response_model=IngestionResult, status_code=status.HTTP_200_OK)
async def ingest_quickbooks_payload(
    tenant_id: UUID,
    payload: Dict[str, Any]
) -> IngestionResult:
    """Ingest real-time bill webhook payloads from QuickBooks."""
    return ingestion_service.process_quickbooks_bill_payload(tenant_id=tenant_id, payload=payload)


@router.post("/quickbooks/sync", response_model=IngestionResult, status_code=status.HTTP_200_OK)
async def sync_quickbooks_sandbox(req: QuickBooksSyncRequest) -> IngestionResult:
    """Sync QuickBooks Online (Sandbox by default, production gated by feature flag)."""
    is_prod_enabled = os.getenv("QUICKBOOKS_PRODUCTION_ENABLED", "false").lower() == "true"
    
    if req.environment == "production" and not is_prod_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="QuickBooks Production API connection is gated pending Intuit App Review approval. Please use Sandbox mode."
        )

    mock_qb_payload = {
        "VendorRef": {"name": "Silicon Valley Cloud Hosting LLC"},
        "DocNumber": f"QB-SBOX-{req.realm_id[:6] if req.realm_id else '001'}",
        "TotalAmt": 8450.00,
        "TxnDate": "2026-08-08",
        "DueDate": "2026-09-08",
        "CurrencyRef": {"value": "USD"},
        "Line": [
            {"Description": "Enterprise Sandbox Compute Instance", "Amount": 8450.00}
        ]
    }
    return ingestion_service.process_quickbooks_bill_payload(tenant_id=req.tenant_id, payload=mock_qb_payload)

