"""Tests for Universal Data Source Abstraction across CSV, Zoho Books, Tally v1, and QuickBooks."""
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
TENANT_ID = str(uuid4())


def test_csv_excel_path_returns_normalized_data_source():
    csv_data = "date,amount,description,reference\n2026-08-01,150000.0,Enterprise License,INV-9901"
    files = {"file": ("test_sheet.csv", csv_data, "text/csv")}
    response = client.post("/api/v1/connectors/csv", data={"tenant_id": TENANT_ID}, files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["source_type"] == "CSV_UPLOAD"
    assert "data_source" in data
    assert data["data_source"]["source_type"] == "CSV_UPLOAD"
    assert len(data["normalized_transactions"]) >= 1


def test_bank_statement_csv_path():
    csv_data = "Transaction Date,Amount,Description\n2026-08-02,500000.0,Direct Wire Deposit"
    files = {"file": ("bank_stmt.csv", csv_data, "text/csv")}
    response = client.post("/api/v1/connectors/bank-statement", data={"tenant_id": TENANT_ID}, files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["source_type"] == "BANK_STATEMENT_CSV"
    assert data["data_source"]["source_type"] == "BANK_STATEMENT_CSV"


def test_zoho_books_path_returns_normalized_schema():
    payload = {
        "tenant_id": TENANT_ID,
        "client_id": "zoho_client_test",
        "client_secret": "zoho_secret_test",
        "organization_id": "99887766_IN"
    }
    response = client.post("/api/v1/connectors/zoho", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["source_type"] == "ZOHO_BOOKS"
    assert len(data["normalized_invoices"]) >= 1
    assert len(data["normalized_contacts"]) >= 1
    assert len(data["normalized_expenses"]) >= 1
    assert data["data_source"]["provider_name"] == "Zoho Books OAuth API"


def test_tally_v1_export_path_returns_normalized_schema():
    xml_tally = """<ENVELOPE>
      <BODY>
        <DATA>
          <TALLYMESSAGE>
            <VOUCHER>
              <VOUCHERNUMBER>TAL-VCH-8801</VOUCHERNUMBER>
              <DATE>2026-08-05</DATE>
              <PARTYLEDGERNAME>Mahindra Industrial Ltd</PARTYLEDGERNAME>
              <AMOUNT>350000.00</AMOUNT>
            </VOUCHER>
          </TALLYMESSAGE>
        </DATA>
      </BODY>
    </ENVELOPE>"""
    files = {"file": ("tally_voucher.xml", xml_tally, "text/xml")}
    response = client.post("/api/v1/connectors/tally", data={"tenant_id": TENANT_ID}, files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["source_type"] == "TALLY_EXPORT"
    assert len(data["normalized_invoices"]) >= 1
    assert data["normalized_invoices"][0]["currency"] == "INR"
    assert data["data_source"]["source_type"] == "TALLY_EXPORT"


def test_quickbooks_sandbox_sync_path():
    payload = {
        "tenant_id": TENANT_ID,
        "realm_id": "qb_realm_test",
        "environment": "sandbox"
    }
    response = client.post("/api/v1/connectors/quickbooks/sync", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["source_type"] == "QUICKBOOKS"
    assert len(data["normalized_invoices"]) >= 1
    assert data["data_source"]["provider_name"] == "QuickBooks Online OAuth2 API"


def test_quickbooks_production_gated_by_feature_flag():
    payload = {
        "tenant_id": TENANT_ID,
        "realm_id": "qb_realm_prod",
        "environment": "production"
    }
    response = client.post("/api/v1/connectors/quickbooks/sync", json=payload)
    assert response.status_code == 403
    assert "gated pending Intuit App Review" in response.json()["detail"]


def test_settings_accounting_provider_selection():
    get_res = client.get(f"/api/v1/settings/accounting-provider?tenant_id={TENANT_ID}")
    assert get_res.status_code == 200
    assert get_res.json()["provider_id"] == "excel"

    post_res = client.post(
        f"/api/v1/settings/accounting-provider?tenant_id={TENANT_ID}",
        json={"provider_id": "zoho_books"}
    )
    assert post_res.status_code == 200
    assert post_res.json()["selection"]["provider_id"] == "zoho_books"
    assert post_res.json()["selection"]["region"] == "INDIA"
