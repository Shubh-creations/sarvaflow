def test_health_and_live_are_process_only(client):
    for path in ("/api/v1/health", "/api/v1/live"):
        response = client.get(path)
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
        assert response.headers["X-Request-ID"]


def test_ready_reports_dependency_state(client):
    response = client.get("/api/v1/ready")
    assert response.status_code in {200, 503}
    if response.status_code == 200:
        assert response.json()["status"] == "ok"
    else:
        assert response.json()["error"]["code"] == "dependency_unavailable"


def test_invalid_tenant_id_returns_422(client):
    """Confirm missing or malformed tenant_id context fails explicitly with 422 validation error."""
    response = client.get("/api/v1/sample-data/health-scorecard?tenant_id=invalid-uuid-12345")
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "validation_error"
