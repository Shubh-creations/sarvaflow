from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

TENANT_ID = "de7995f6-42a5-4048-bc4e-db5a2d17d594"


def test_list_scenarios() -> None:
    response = client.get("/api/v1/sample-data/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 16
    assert data[0]["id"] == "aws-cloud-invoice"


def test_get_individual_scenario() -> None:
    response = client.get("/api/v1/sample-data/scenarios/jpm-mt940-statement")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "3. JPMorgan Chase SWIFT MT940 Bank Statement"
    assert "auto_recon_rate" in data["key_metrics"]


def test_health_scorecard() -> None:
    response = client.get(f"/api/v1/sample-data/health-scorecard?tenant_id={TENANT_ID}")
    assert response.status_code == 200
    data = response.json()
    assert data["overall_health_score"] == 94
    assert data["rating"] == "EXCELLENT"


def test_master_optimization() -> None:
    response = client.post(f"/api/v1/sample-data/master-optimize?tenant_id={TENANT_ID}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "MASTER_OPTIMIZATION_SUCCESSFUL"
    assert len(data["executed_actions"]) == 4


def test_ingest_custom_document_classification() -> None:
    # Test Manufacturing BOM Classification
    payload_bom = {
        "file_name": "bom_assembly.csv",
        "file_content": "Component_Part_ID,Description,Quantity_Required,Unit_Cost_USD\nCMP-8819,Anodized Casing,1,18.50"
    }
    res_bom = client.post("/api/v1/sample-data/ingest-document", json=payload_bom)
    assert res_bom.status_code == 200
    data_bom = res_bom.json()
    assert data_bom["industry_domain"] == "MANUFACTURING / HARDWARE"
    assert len(data_bom["fields"]) == 4
    assert len(data_bom["bounding_box_legend"]) == 4

    # Test AI Compute Classification
    payload_gpu = {
        "file_name": "gpu_cluster.json",
        "file_content": "10,240x H100 SXM5 GPU Hours (Model Fine-Tuning) @ $2.40/hour = $24,576.00"
    }
    res_gpu = client.post("/api/v1/sample-data/ingest-document", json=payload_gpu)
    assert res_gpu.status_code == 200
    data_gpu = res_gpu.json()
    assert data_gpu["industry_domain"] == "AI / COMPUTE-INTENSIVE"


def test_log_user_field_correction() -> None:
    payload_corr = {
        "document_type": "Manufacturing Supplier Invoice",
        "field_key": "vendor_name",
        "original_ai_value": "Global Precision Comp",
        "corrected_value": "Global Precision Components Corp",
        "confidence_at_extraction": 0.82
    }
    res_corr = client.post("/api/v1/sample-data/log-correction", json=payload_corr)
    assert res_corr.status_code == 200
    data_corr = res_corr.json()
    assert data_corr["status"] == "CORRECTION_LOGGED"
    assert data_corr["total_corrections_recorded"] >= 1


def test_accuracy_dashboard() -> None:
    res = client.get("/api/v1/sample-data/accuracy-dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "overall_accuracy_rate_pct" in data
    assert "recalibrated_field_weights" in data
    assert len(data["accuracy_by_category"]) == 4
