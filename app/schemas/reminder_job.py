"""
Pydantic schemas for Reminder Job API validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.models.reminder_job import ReminderType, ReminderStatus


class ReminderJobCreate(BaseModel):
    """Schema for creating a reminder job."""
    customer_id: UUID
    reminder_type: ReminderType
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    delivery_channel: Optional[str] = "WHATSAPP"
    scheduled_time: datetime
    max_retries: Optional[int] = Field(default=3, ge=1, le=10)


class ReminderJobUpdate(BaseModel):
    """Schema for updating a reminder job."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    message: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    status: Optional[ReminderStatus] = None


class ReminderJobResponse(BaseModel):
    """Schema for reminder job response."""
    id: UUID
    customer_id: UUID
    reminder_type: ReminderType
    title: str
    message: str
    delivery_channel: str
    scheduled_time: datetime
    status: ReminderStatus
    retry_count: int
    max_retries: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ReminderJobListResponse(BaseModel):
    """Paginated list response for reminder jobs."""
    items: List[ReminderJobResponse]
    total: int
    page: int
    page_size: int
