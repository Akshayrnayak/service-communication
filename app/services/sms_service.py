"""
SMS Service - Handles SMS notification sending with provider simulation.
Supports async queue handling, failure retry, and delivery logs.
"""

import logging
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.sms_notification import SMSNotification, SMSStatus
from app.models.communication_log import LogEventType, LogChannel, LogStatus
from app.schemas.sms_notification import SMSSendRequest
from app.services.logging_service import LoggingService
from app.services.retry_service import RetryService

logger = logging.getLogger(__name__)


class SMSService:
    """Service for managing SMS notifications."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.logging_service = LoggingService(db)
        self.retry_service = RetryService()

    async def _simulate_sms_provider(self, phone: str, message: str) -> dict:
        """Simulate SMS provider API call."""
        import random
        success = random.random() > 0.1  # 90% success rate
        if success:
            return {
                "success": True,
                "message_id": f"sms_{uuid.uuid4().hex[:12]}",
            }
        raise Exception("SMS provider API error - simulated failure")

    async def send_sms(self, request: SMSSendRequest) -> SMSNotification:
        """Send an SMS notification with retry support."""
        notification = SMSNotification(
            recipient_phone=request.recipient_phone,
            recipient_name=request.recipient_name,
            message_body=request.message_body,
            template_id=request.template_id,
            status=SMSStatus.QUEUED,
        )
        self.db.add(notification)
        await self.db.flush()

        # Attempt to send with retry
        result = await self.retry_service.execute_with_retry(
            self._simulate_sms_provider,
            request.recipient_phone,
            request.message_body,
        )

        if result["success"]:
            notification.status = SMSStatus.SENT
            notification.sent_at = datetime.now(timezone.utc)
            notification.provider_message_id = result["result"]["message_id"]
            notification.retry_count = result["attempts"] - 1

            await self.logging_service.log_event(
                event_type=LogEventType.SEND,
                channel=LogChannel.SMS,
                recipient=request.recipient_phone,
                status=LogStatus.SUCCESS,
                notification_id=notification.id,
                response_message=f"SMS sent after {result['attempts']} attempt(s)",
            )
        else:
            notification.status = SMSStatus.FAILED
            notification.error_message = result.get("error", "Unknown error")
            notification.retry_count = result["attempts"] - 1

            await self.logging_service.log_event(
                event_type=LogEventType.FAILURE,
                channel=LogChannel.SMS,
                recipient=request.recipient_phone,
                status=LogStatus.FAILURE,
                notification_id=notification.id,
                response_message=result.get("error"),
            )

        await self.db.flush()
        return notification

    async def get_history(
        self, page: int = 1, page_size: int = 20, status_filter: str = None
    ) -> dict:
        """Get SMS notification history with pagination."""
        query = select(SMSNotification).order_by(SMSNotification.created_at.desc())
        if status_filter:
            query = query.where(SMSNotification.status == status_filter)

        count_query = select(func.count()).select_from(SMSNotification)
        if status_filter:
            count_query = count_query.where(SMSNotification.status == status_filter)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await self.db.execute(query)
        items = result.scalars().all()

        return {"items": items, "total": total, "page": page, "page_size": page_size}
