"""Plaid Direct Sync & Webhook API Endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Body, Query, status
from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

from app.domain.connectors.plaid_connector import PlaidConnectorEngine

router = APIRouter(prefix="/plaid", tags=["Plaid Direct Sync Integration"])
_plaid_engine = PlaidConnectorEngine()


class PublicTokenExchangeRequest(BaseModel):
    public_token: str = Field(..., description="Plaid Link public_token received from frontend modal")
    institution_name: Optional[str] = Field("JPMorgan Chase Bank", description="Name of connected bank institution")


class WebhookPayload(BaseModel):
    webhook_type: str = Field("TRANSACTIONS", description="Plaid webhook event type")
    webhook_code: str = Field("SYNC_UPDATES_AVAILABLE", description="Plaid webhook event code")
    item_id: str = Field("item_chase_main", description="Plaid item ID")


@router.post("/create-link-token", status_code=status.HTTP_200_OK)
def create_plaid_link_token(user_id: str = Query("usr_cfo_sarah")) -> Dict[str, Any]:
    """Generates official Plaid Link initialization token for frontend OAuth bank connection."""
    return _plaid_engine.create_link_token(user_id=user_id)


@router.post("/exchange-public-token", status_code=status.HTTP_200_OK)
def exchange_public_token(payload: PublicTokenExchangeRequest) -> Dict[str, Any]:
    """Exchanges public_token for access_token and initializes connected account."""
    return _plaid_engine.exchange_public_token(
        public_token=payload.public_token,
        institution_name=payload.institution_name or "JPMorgan Chase Bank"
    )


@router.get("/accounts", status_code=status.HTTP_200_OK)
def get_connected_accounts() -> Dict[str, Any]:
    """Returns connected bank accounts, liquid cash reserves, and sync health telemetry."""
    return _plaid_engine.get_accounts()


@router.post("/sync-transactions", status_code=status.HTTP_200_OK)
def sync_transactions(item_id: Optional[str] = Query(None)) -> Dict[str, Any]:
    """Triggers real-time transaction streaming and auto-categorization."""
    return _plaid_engine.sync_transactions(item_id=item_id)


import logging

logger = logging.getLogger(__name__)

@router.post("/webhook", status_code=status.HTTP_200_OK)
def receive_plaid_webhook(payload: WebhookPayload) -> Dict[str, Any]:
    """Inbound webhook endpoint for real-time bank settlement and balance notifications."""
    logger.info(f"[PLAID_WEBHOOK_RECEIVED] type={payload.webhook_type} code={payload.webhook_code} item_id={payload.item_id}")
    print(f"INFO: [PLAID_WEBHOOK_RECEIVED] type={payload.webhook_type} code={payload.webhook_code} item_id={payload.item_id}")
    return _plaid_engine.handle_webhook(
        webhook_type=payload.webhook_type,
        webhook_code=payload.webhook_code,
        item_id=payload.item_id
    )
