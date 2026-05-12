"""
Alert Events API routes.
Handles emergency and high-priority alert notifications.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token, rate_limiter, CurrentUser
from app.schemas.alert_event import (
    AlertEventCreate,
    AlertEventResponse,
    AlertEventListResponse,
)
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alert Events"])


@router.post(
    "/emergency",
    response_model=AlertEventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Trigger an emergency alert",
)
async def trigger_emergency_alert(
    request: AlertEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(verify_token),
    _rate_limit=Depends(rate_limiter),
):
    """
    Trigger a high-priority emergency alert.
    Sends notifications via multiple channels (SMS, WhatsApp, Email).
    Includes priority handling, escalation, and fast retry logic.
    """
    service = AlertService(db)
    alert = await service.trigger_emergency_alert(request)
    return alert


@router.get(
    "/history",
    response_model=AlertEventListResponse,
    summary="Get alert event history",
)
async def get_alert_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    priority: str = Query(None, description="Filter by priority"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(verify_token),
):
    """Get paginated alert event history."""
    service = AlertService(db)
    result = await service.get_history(page, page_size, priority)
    return AlertEventListResponse(**result)


@router.post(
    "/{alert_id}/escalate",
    response_model=AlertEventResponse,
    summary="Escalate an alert",
)
async def escalate_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(verify_token),
):
    """Escalate a failed or partially failed alert to next level."""
    service = AlertService(db)
    alert = await service.escalate_alert(alert_id)
    if not alert:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
