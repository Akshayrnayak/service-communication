"""
Alert Service - Handles emergency and high-priority alert notifications.
Supports multi-channel sending, priority handling, and escalation.
"""

import logging
from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.alert_event import AlertEvent, AlertStatus, AlertPriority
from app.models.communication_log import LogEventType, LogChannel, LogStatus
from app.schemas.alert_event import AlertEventCreate
from app.services.logging_service import LoggingService
from app.services.retry_service import RetryService

logger = logging.getLogger(__name__)


class AlertService:
    """Service for managing emergency alerts with multi-channel delivery."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.logging_service = LoggingService(db)
        self.retry_service = RetryService()

    async def trigger_emergency_alert(self, request: AlertEventCreate) -> AlertEvent:
        """
        Trigger an emergency alert with multi-channel notification.
        Sends via SMS, WhatsApp, and Email simultaneously.
        """
        alert = AlertEvent(
            alert_type=request.alert_type,
            priority=request.priority,
            title=request.title,
            description=request.description,
            recipient_id=request.recipient_id,
            recipient_phone=request.recipient_phone,
            recipient_email=request.recipient_email,
            channels_used=request.channels_used,
            status=AlertStatus.PROCESSING,
        )
        self.db.add(alert)
        await self.db.flush()

        # Process multi-channel sending
        channels_success = 0
        channels = request.channels_used.split(",")

        for channel in channels:
            channel = channel.strip()
            try:
                # Simulate sending on each channel
                import random
                if random.random() > 0.05:  # 95% success for emergency
                    channels_success += 1
                    await self.logging_service.log_event(
                        event_type=LogEventType.SEND,
                        channel=LogChannel(channel) if channel in ["EMAIL", "SMS", "WHATSAPP"] else LogChannel.MULTI,
                        recipient=request.recipient_phone or request.recipient_email or str(request.recipient_id),
                        status=LogStatus.SUCCESS,
                        notification_id=alert.id,
                        response_message=f"Emergency alert sent via {channel}",
                    )
                else:
                    raise Exception(f"{channel} delivery failed")
            except Exception as e:
                logger.warning(f"Alert channel {channel} failed: {str(e)}")
                await self.logging_service.log_event(
                    event_type=LogEventType.FAILURE,
                    channel=LogChannel(channel) if channel in ["EMAIL", "SMS", "WHATSAPP"] else LogChannel.MULTI,
                    recipient=request.recipient_phone or request.recipient_email or str(request.recipient_id),
                    status=LogStatus.FAILURE,
                    notification_id=alert.id,
                    response_message=str(e),
                )

        # Update alert status based on results
        if channels_success == len(channels):
            alert.status = AlertStatus.SENT
        elif channels_success > 0:
            alert.status = AlertStatus.SENT
            alert.escalation_level = 1
        else:
            alert.status = AlertStatus.FAILED
            alert.escalation_level = 2

        await self.db.flush()
        logger.info(
            f"Emergency alert {alert.id}: {channels_success}/{len(channels)} channels successful"
        )
        return alert

    async def escalate_alert(self, alert_id: UUID) -> AlertEvent:
        """Escalate a failed or partially failed alert."""
        result = await self.db.execute(
            select(AlertEvent).where(AlertEvent.id == alert_id)
        )
        alert = result.scalar_one_or_none()
        if alert:
            alert.escalation_level += 1
            alert.status = AlertStatus.ESCALATED
            alert.retry_count += 1
            await self.db.flush()
        return alert

    async def get_history(
        self, page: int = 1, page_size: int = 20, priority_filter: str = None
    ) -> dict:
        """Get alert event history with pagination."""
        query = select(AlertEvent).order_by(AlertEvent.created_at.desc())
        if priority_filter:
            query = query.where(AlertEvent.priority == priority_filter)

        count_query = select(func.count()).select_from(AlertEvent)
        if priority_filter:
            count_query = count_query.where(AlertEvent.priority == priority_filter)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await self.db.execute(query)
        items = result.scalars().all()

        return {"items": items, "total": total, "page": page, "page_size": page_size}
