"""Tests for Compliance Center, GST Anomaly Detection, Regulatory Change Monitoring, and Audit Report Export."""
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.domain.compliance.gst_engine import GSTComplianceEngine
from app.main import app

client = TestClient(app)
TENANT_ID = str(uuid4())


def test_gst_engine_validations():
    engine = GSTComplianceEngine()
    
    # GSTIN validation
    valid_gstin, msg1 = engine.validate_gstin("27AAACT9876F1Z5")
    assert valid_gstin is True
    assert "Maharashtra" in msg1

    invalid_gstin, msg2 = engine.validate_gstin("INVALID_GSTIN_123")
    assert invalid_gstin is False

    # HSN validation
    valid_hsn, _ = engine.validate_hsn_sac("998313", 100000.0)
    assert valid_hsn is True

    missing_hsn, _ = engine.validate_hsn_sac("", 100000.0)
    assert missing_hsn is False

    # Tax math validation
    tax_ok, _ = engine.validate_tax_math(100.0, 9.0, 9.0, 0.0, 118.0)
    assert tax_ok is True

    tax_bad, _ = engine.validate_tax_math(100.0, 18.0, 0.0, 0.0, 150.0)
    assert tax_bad is False


def test_compliance_center_summary():
    res = client.get(f"/api/v1/compliance/center-summary?tenant_id={TENANT_ID}")
    assert res.status_code == 200
    data = res.json()
    assert data["compliance_health_status"] == "MONITORED_HEALTHY"
    assert "yc_compliance_architecture_split" in data
    assert len(data["yc_compliance_architecture_split"]["live_production"]) >= 4
    assert len(data["yc_compliance_architecture_split"]["demo_beta"]) >= 1
    assert len(data["yc_compliance_architecture_split"]["planned_roadmap"]) >= 1


def test_evaluate_gst_readiness_flags_anomalies():
    sample_invoices = [
        {
            "doc_number": "INV-OK-01",
            "entity_name": "Valid Entity Ltd",
            "total_amount": 11800.0,
            "supplier_gstin": "27AAACT9876F1Z5",
            "hsn_sac_code": "998313",
            "taxable_value_inr": 10000.0,
            "cgst_amount_inr": 900.0,
            "sgst_amount_inr": 900.0
        },
        {
            "doc_number": "INV-FLAG-02",
            "entity_name": "Bad Vendor",
            "total_amount": 100000.0,
            "supplier_gstin": "BAD_GSTIN",
            "hsn_sac_code": "",
            "taxable_value_inr": 80000.0,
            "cgst_amount_inr": 5000.0,
            "sgst_amount_inr": 0.0
        }
    ]
    res = client.post("/api/v1/compliance/evaluate-gst-readiness", json={"tenant_id": TENANT_ID, "invoices": sample_invoices})
    assert res.status_code == 200
    data = res.json()
    assert data["total_invoices_evaluated"] == 2
    assert data["ready_count"] == 1
    assert data["flagged_count"] == 1
    assert len(data["flagged_anomalies"][0]["anomalies"]) >= 2


def test_run_regulatory_check():
    res = client.post("/api/v1/compliance/run-regulatory-check")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "COMPLETED_CLEAN"
    assert "REG-CHK-" in data["check_id"]


def test_export_compliance_report():
    res = client.get(f"/api/v1/compliance/export-report?tenant_id={TENANT_ID}")
    assert res.status_code == 200
    data = res.json()
    assert "SarvaFlow Enterprise AI Compliance" in data["certificate_title"]
    assert "checksum_sha256" in data
    assert len(data["real_audit_trail_events"]) >= 1
    assert len(data["regulatory_monitoring_history"]) >= 1
