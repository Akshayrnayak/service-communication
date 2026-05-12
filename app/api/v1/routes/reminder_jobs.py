"""
Reminder Jobs API routes.
Manages scheduled reminder notifications with cron-style processing.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import verify_token, require_role, CurrentUser
from app.schemas.reminder_job import (
    ReminderJobCreate,
    ReminderJobUpdate,
    ReminderJobResponse,
    ReminderJobListResponse,
)
from app.services.reminder_service import ReminderService

router = APIRouter(prefix="/reminders", tags=["Reminder Jobs"])


@router.post(
    "/",
    response_model=ReminderJobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Schedule a reminder notification",
)
async def create_reminder(
    request: ReminderJobCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(verify_token),
):
    """
    Schedule a new reminder notification.
    Examples: Medical visit reminder, legal document reminder, inspection reminder.
    """
    service = ReminderService(db)
    reminder = await service.create_reminder(request)
    return reminder


@router.get(
    "/",
    response_model=ReminderJobListResponse,
    summary="List reminder jobs",
)
async def list_reminders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status_filter: str = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(verify_token),
):
    """Get paginated list of reminder jobs."""
    service = ReminderService(db)
    result = await service.get_reminders(page, page_size, status_filter)
    return ReminderJobListResponse(**result)


@router.get(
    "/{reminder_id}",
    response_model=ReminderJobResponse,
    summary="Get a reminder job",
)
async def get_reminder(
    reminder_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(verify_token),
):
    """Get a single reminder job by ID."""
    service = ReminderService(db)
    reminder = await service.get_reminder(reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder


@router.put(
    "/{reminder_id}",
    response_model=ReminderJobResponse,
    summary="Update a reminder job",
)
async def update_reminder(
    reminder_id: UUID,
    request: ReminderJobUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(verify_token),
):
    """Update an existing reminder job."""
    service = ReminderService(db)
    reminder = await service.update_reminder(reminder_id, request)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder


@router.delete(
    "/{reminder_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel a reminder job",
)
async def cancel_reminder(
    reminder_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(verify_token),
):
    """Cancel a scheduled reminder job."""
    service = ReminderService(db)
    reminder = await service.cancel_reminder(reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")


@router.post(
    "/process-due",
    summary="Process all due reminders",
    status_code=status.HTTP_200_OK,
)
async def process_due_reminders(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(require_role("admin", "service")),
):
    """Trigger processing of all due reminder jobs (used by scheduler)."""
    service = ReminderService(db)
    due_reminders = await service.get_due_reminders()
    return {
        "message": f"Found {len(due_reminders)} due reminders for processing",
        "count": len(due_reminders),
    }
