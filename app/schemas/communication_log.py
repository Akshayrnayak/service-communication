"""
Pydantic schemas for Communication Log API validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.models.communication_log import LogEventType, LogChannel, LogStatus


class CommunicationLogCreate(BaseModel):
    """Schema for creating a communication log entry."""
    event_type: LogEventType
    channel: LogChannel
    recipient: str = Field(..., min_length=1, max_length=255)
    notification_id: Optional[UUID] = None
    status: LogStatus
    response_message: Optional[str] = None
    metadata_json: Optional[str] = None


class CommunicationLogResponse(BaseModel):
    """Schema for communication log response."""
    id: UUID
    event_type: LogEventType
    channel: LogChannel
    recipient: str
    notification_id: Optional[UUID]
    status: LogStatus
    response_message: Optional[str]
    metadata_json: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


class CommunicationLogListResponse(BaseModel):
    """Paginated list response for communication logs."""
    items: List[CommunicationLogResponse]
    total: int
    page: int
    page_size: int
