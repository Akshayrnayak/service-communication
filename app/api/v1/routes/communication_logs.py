"""
Communication Logs API routes.
Tracks ALL communication activity including success, failure, and retry logs.
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.security import verify_token, CurrentUser
from app.models.communication_log import CommunicationLog
from app.schemas.communication_log import (
    CommunicationLogResponse,
    CommunicationLogListResponse,
)

router = APIRouter(prefix="/logs", tags=["Communication Logs"])


@router.get(
    "/",
    response_model=CommunicationLogListResponse,
    summary="List communication logs",
)
async def list_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    channel: str = Query(None, description="Filter by channel"),
    event_type: str = Query(None, description="Filter by event type"),
    status_filter: str = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(verify_token),
):
    """Get paginated communication logs with filtering."""
    query = select(CommunicationLog).order_by(CommunicationLog.timestamp.desc())

    if channel:
        query = query.where(CommunicationLog.channel == channel)
    if event_type:
        query = query.where(CommunicationLog.event_type == event_type)
    if status_filter:
        query = query.where(CommunicationLog.status == status_filter)

    # Count total
    count_query = select(func.count()).select_from(CommunicationLog)
    if channel:
        count_query = count_query.where(CommunicationLog.channel == channel)
    if event_type:
        count_query = count_query.where(CommunicationLog.event_type == event_type)
    if status_filter:
        count_query = count_query.where(CommunicationLog.status == status_filter)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return CommunicationLogListResponse(
        items=items, total=total, page=page, page_size=page_size
    )
