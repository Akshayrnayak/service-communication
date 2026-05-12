"""
Email Notifications API routes.
Handles email sending with SMTP simulation and delivery tracking.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token, rate_limiter, CurrentUser
from app.schemas.email_notification import (
    EmailSendRequest,
    EmailNotificationResponse,
    EmailHistoryResponse,
)
from app.services.email_service import EmailService

router = APIRouter(prefix="/email", tags=["Email Notifications"])


@router.post(
    "/send",
    response_model=EmailNotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send an email notification",
)
async def send_email(
    request: EmailSendRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(verify_token),
    _rate_limit=Depends(rate_limiter),
):
    """
    Send an email notification to a recipient.
    Supports HTML emails, queue-based sending, and retry logic.
    """
    service = EmailService(db)
    notification = await service.send_email(request)
    return notification


@router.get(
    "/history",
    response_model=EmailHistoryResponse,
    summary="Get email notification history",
)
async def get_email_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(verify_token),
):
    """Get paginated email notification history."""
    service = EmailService(db)
    result = await service.get_history(page, page_size, status_filter)
    return EmailHistoryResponse(**result)
