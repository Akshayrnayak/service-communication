"""
Reminder Service - Manages scheduled reminder notifications.
Handles cron-style processing, auto-send, and delivery tracking.
"""

import logging
from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.reminder_job import ReminderJob, ReminderStatus
from app.schemas.reminder_job import ReminderJobCreate, ReminderJobUpdate

logger = logging.getLogger(__name__)


class ReminderService:
    """Service for managing reminder jobs."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_reminder(self, request: ReminderJobCreate) -> ReminderJob:
        """Create a new scheduled reminder job."""
        reminder = ReminderJob(
            customer_id=request.customer_id,
            reminder_type=request.reminder_type,
            title=request.title,
            message=request.message,
            delivery_channel=request.delivery_channel,
            scheduled_time=request.scheduled_time,
            max_retries=request.max_retries,
            status=ReminderStatus.SCHEDULED,
        )
        self.db.add(reminder)
        await self.db.flush()
        logger.info(f"Reminder created: {reminder.id} scheduled for {reminder.scheduled_time}")
        return reminder

    async def update_reminder(self, reminder_id: UUID, request: ReminderJobUpdate) -> ReminderJob:
        """Update an existing reminder job."""
        result = await self.db.execute(
            select(ReminderJob).where(ReminderJob.id == reminder_id)
        )
        reminder = result.scalar_one_or_none()
        if not reminder:
            return None

        update_data = request.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(reminder, field, value)

        await self.db.flush()
        return reminder

    async def get_due_reminders(self) -> list:
        """Get all reminders that are due for processing."""
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(ReminderJob)
            .where(ReminderJob.status == ReminderStatus.SCHEDULED)
            .where(ReminderJob.scheduled_time <= now)
            .order_by(ReminderJob.scheduled_time.asc())
        )
        return result.scalars().all()

    async def get_reminder(self, reminder_id: UUID) -> ReminderJob:
        """Get a single reminder by ID."""
        result = await self.db.execute(
            select(ReminderJob).where(ReminderJob.id == reminder_id)
        )
        return result.scalar_one_or_none()

    async def cancel_reminder(self, reminder_id: UUID) -> ReminderJob:
        """Cancel a scheduled reminder."""
        reminder = await self.get_reminder(reminder_id)
        if reminder and reminder.status == ReminderStatus.SCHEDULED:
            reminder.status = ReminderStatus.CANCELLED
            await self.db.flush()
        return reminder

    async def get_reminders(
        self, page: int = 1, page_size: int = 20, status_filter: str = None
    ) -> dict:
        """Get reminder jobs with pagination."""
        query = select(ReminderJob).order_by(ReminderJob.scheduled_time.desc())
        if status_filter:
            query = query.where(ReminderJob.status == status_filter)

        count_query = select(func.count()).select_from(ReminderJob)
        if status_filter:
            count_query = count_query.where(ReminderJob.status == status_filter)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        result = await self.db.execute(query)
        items = result.scalars().all()

        return {"items": items, "total": total, "page": page, "page_size": page_size}
