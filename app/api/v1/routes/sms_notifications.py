"""
SMS Notifications API routes.
Handles SMS sending with provider simulation and delivery tracking.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token, rate_limiter, CurrentUser
from app.schemas.sms_notification import (
    SMSSendRequest,
    SMSNotificationResponse,
    SMSHistoryResponse,
)
from app.services.sms_service import SMSService

router = APIRouter(prefix="/sms", tags=["SMS Notifications"])


@router.post(
    "/send",
    response_model=SMSNotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send an SMS notification",
)
async def send_sms(
    request: SMSSendRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(verify_token),
    _rate_limit=Depends(rate_limiter),
):
    """
    Send an SMS notification to a recipient.
    Supports async queue handling with failure retry and delivery logs.
    """
    service = SMSService(db)
    notification = await service.send_sms(request)
    return notification


@router.get(
    "/history",
    response_model=SMSHistoryResponse,
    summary="Get SMS notification history",
)
async def get_sms_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(verify_token),
):
    """Get paginated SMS notification history."""
    service = SMSService(db)
    result = await service.get_history(page, page_size, status_filter)
    return SMSHistoryResponse(**result)
