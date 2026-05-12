"""
WhatsApp Notifications API routes.
Handles WhatsApp message sending and delivery tracking.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token, rate_limiter, CurrentUser
from app.schemas.whatsapp_notification import (
    WhatsAppSendRequest,
    WhatsAppNotificationResponse,
    WhatsAppHistoryResponse,
)
from app.services.whatsapp_service import WhatsAppService

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp Notifications"])


@router.post(
    "/send",
    response_model=WhatsAppNotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send a WhatsApp notification",
)
async def send_whatsapp(
    request: WhatsAppSendRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(verify_token),
    _rate_limit=Depends(rate_limiter),
):
    """
    Send a WhatsApp notification to a recipient.
    Supports async background sending with delivery tracking and retry.
    """
    service = WhatsAppService(db)
    notification = await service.send_whatsapp(request)
    return notification


@router.get(
    "/history",
    response_model=WhatsAppHistoryResponse,
    summary="Get WhatsApp notification history",
)
async def get_whatsapp_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(verify_token),
):
    """Get paginated WhatsApp notification history."""
    service = WhatsAppService(db)
    result = await service.get_history(page, page_size, status_filter)
    return WhatsAppHistoryResponse(**result)
