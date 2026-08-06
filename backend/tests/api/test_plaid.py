"""Tests for Plaid Direct Sync Integration Endpoints."""
from __future__ import annotations

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_plaid_create_link_token() -> None:
    """Test Plaid Link token generation."""
    response = client.post("/api/v1/plaid/create-link-token?user_id=usr_cfo_sarah")
    assert response.status_code == 200
    data = response.json()
    assert "link_token" in data
    assert data["link_token"].startswith("link-sandbox-usr_cfo_sarah")
    assert data["environment"] == "sandbox"


def test_plaid_get_accounts() -> None:
    """Test retrieving connected Plaid accounts and cash telemetry."""
    response = client.get("/api/v1/plaid/accounts")
    assert response.status_code == 200
    data = response.json()
    assert data["total_connected_institutions"] >= 2
    assert data["total_liquid_cash_usd"] > 0
    assert len(data["connected_accounts"]) >= 2


def test_plaid_exchange_public_token() -> None:
    """Test public_token exchange."""
    payload = {
        "public_token": "public-sandbox-test-token-12345",
        "institution_name": "Silicon Valley Bank (SVB)"
    }
    response = client.post("/api/v1/plaid/exchange-public-token", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert "item_id" in data
    assert data["account"]["institution_name"] == "Silicon Valley Bank (SVB)"


def test_plaid_sync_transactions() -> None:
    """Test live transaction streaming sync."""
    response = client.post("/api/v1/plaid/sync-transactions")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SYNCED"
    assert data["synced_count"] >= 3
    assert "transactions" in data


def test_plaid_webhook() -> None:
    """Test receiving inbound Plaid settlement webhooks."""
    payload = {
        "webhook_type": "TRANSACTIONS",
        "webhook_code": "SYNC_UPDATES_AVAILABLE",
        "item_id": "item_chase_main"
    }
    response = client.post("/api/v1/plaid/webhook", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["webhook_received"] is True
    assert data["item_id"] == "item_chase_main"
    assert len(data["triggered_actions"]) >= 3
