"""
Email Service - Handles email notification sending with SMTP simulation.
Supports HTML emails, queue-based sending, and retry logic.
"""

import logging
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.email_notification import EmailNotification, EmailStatus
from app.models.communication_log import LogEventType, LogChannel, LogStatus
from app.schemas.email_notification import EmailSendRequest
from app.services.logging_service import LoggingService
from app.services.retry_service import RetryService

logger = logging.getLogger(__name__)


class EmailService:
    """Service for managing email notifications."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.logging_service = LoggingService(db)
        self.retry_service = RetryService()

    async def _simulate_smtp_send(self, recipient: str, subject: str) -> dict:
        """Simulate SMTP email sending (replace with real SMTP in production)."""
        # Simulated success response
        import random
        success = random.random() > 0.1  # 90% success rate simulation
        if success:
            return {
                "success": True,
                "message_id": f"smtp_{uuid.uuid4().hex[:12]}",
            }
        raise Exception("SMTP connection timeout - simulated failure")

    async def send_email(self, request: EmailSendRequest) -> EmailNotification:
        """Send an email notification with retry support."""
        # Create notification record
        notification = EmailNotification(
            recipient_email=request.recipient_email,
            recipient_name=request.recipient_name,
            subject=request.subject,
            body_html=request.body_html,
            body_text=request.body_text,
            is_html=request.is_html,
            template_id=request.template_id,
            status=EmailStatus.QUEUED,
        )
        self.db.add(notification)
        await self.db.flush()

        # Attempt to send with retry
        result = await self.retry_service.execute_with_retry(
            self._simulate_smtp_send,
            request.recipient_email,
            request.subject,
        )

        if result["success"]:
            notification.status = EmailStatus.SENT
            notification.sent_at = datetime.now(timezone.utc)
            notification.retry_count = result["attempts"] - 1

            await self.logging_service.log_event(
                event_type=LogEventType.SEND,
                channel=LogChannel.EMAIL,
                recipient=request.recipient_email,
                status=LogStatus.SUCCESS,
                notification_id=notification.id,
                response_message=f"Email sent successfully after {result['attempts']} attempt(s)",
            )
        else:
            notification.status = EmailStatus.FAILED
            notification.error_message = result.get("error", "Unknown error")
            notification.retry_count = result["attempts"] - 1

            await self.logging_service.log_event(
                event_type=LogEventType.FAILURE,
                channel=LogChannel.EMAIL,
                recipient=request.recipient_email,
                status=LogStatus.FAILURE,
                notification_id=notification.id,
                response_message=result.get("error"),
            )

        await self.db.flush()
        return notification

    async def get_history(
        self, page: int = 1, page_size: int = 20, status_filter: str = None
    ) -> dict:
        """Get email notification history with pagination."""
        query = select(EmailNotification).order_by(
            EmailNotification.created_at.desc()
        )
        if status_filter:
            query = query.where(EmailNotification.status == status_filter)

        # Count total
        count_query = select(func.count()).select_from(EmailNotification)
        if status_filter:
            count_query = count_query.where(EmailNotification.status == status_filter)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Paginate
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await self.db.execute(query)
        items = result.scalars().all()

        return {"items": items, "total": total, "page": page, "page_size": page_size}
