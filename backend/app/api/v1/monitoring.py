"""API endpoints for Realtime Financial Risk & Anomaly Alerts and SSE Event Streaming."""
from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse

from app.domain.monitoring.service import FinancialRiskAlert, RealtimeMonitoringService

router = APIRouter(prefix="/monitoring", tags=["Realtime Monitoring & Alerts"])
monitoring_service = RealtimeMonitoringService()


@router.post("/check-duplicates", response_model=List[FinancialRiskAlert], status_code=status.HTTP_200_OK)
async def check_duplicate_invoices(
    tenant_id: UUID,
    new_bills: List[Dict[str, Any]],
    existing_bills: List[Dict[str, Any]],
) -> List[FinancialRiskAlert]:
    """Check inbound bills for duplicate invoice anomalies."""
    return monitoring_service.check_duplicate_invoices(tenant_id=tenant_id, new_bills=new_bills, existing_bills=existing_bills)


@router.post("/check-expense-spike", response_model=List[FinancialRiskAlert], status_code=status.HTTP_200_OK)
async def check_expense_spike(
    tenant_id: UUID,
    gl_category: str,
    current_spend: float,
    baseline_mean: float,
    std_dev: float,
) -> List[FinancialRiskAlert]:
    """Audit GL account spend against 3-sigma statistical baseline for expense spikes."""
    alert = monitoring_service.check_expense_spikes(
        tenant_id=tenant_id,
        gl_category=gl_category,
        current_spend=current_spend,
        historical_baseline_mean=baseline_mean,
        std_dev=std_dev,
    )
    return [alert] if alert else []


@router.get("/stream-events")
async def stream_live_status_events():
    """Server-Sent Events (SSE) stream for real-time status updates (Server -> Client)."""
    async def event_generator():
        initial_data = json.dumps({
            "type": "SSE_CONNECTED",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "message": "Realtime SSE status stream active"
        })
        yield f"data: {initial_data}\n\n"

        while True:
            await asyncio.sleep(3.0)
            status_data = json.dumps({
                "type": "STATUS_UPDATE",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "agent_status": "ACTIVE",
                "recon_match_rate": 98.4,
                "health_score": 94
            })
            yield f"data: {status_data}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
