"""
Logging Service - Centralized communication logging for all channels.
Records success, failure, and retry events for audit and debugging.
"""

import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.communication_log import (
    CommunicationLog,
    LogEventType,
    LogChannel,
    LogStatus,
)

logger = logging.getLogger(__name__)


class LoggingService:
    """Service for managing communication logs."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_event(
        self,
        event_type: LogEventType,
        channel: LogChannel,
        recipient: str,
        status: LogStatus,
        notification_id: UUID = None,
        response_message: str = None,
        metadata_json: str = None,
    ) -> CommunicationLog:
        """Create a new communication log entry."""
        log_entry = CommunicationLog(
            event_type=event_type,
            channel=channel,
            recipient=recipient,
            notification_id=notification_id,
            status=status,
            response_message=response_message,
            metadata_json=metadata_json,
        )
        self.db.add(log_entry)
        await self.db.flush()
        logger.info(
            f"Communication log: {event_type.value} | {channel.value} | "
            f"{recipient} | {status.value}"
        )
        return log_entry
