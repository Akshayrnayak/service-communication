"""
API v1 Router - Aggregates all route modules.
"""

from fastapi import APIRouter

from app.api.v1.routes import (
    notification_templates,
    customer_messages,
    whatsapp_notifications,
    email_notifications,
    sms_notifications,
    reminder_jobs,
    communication_logs,
    alert_events,
)

api_router = APIRouter(prefix="/api/v1")

# Include all route modules
api_router.include_router(notification_templates.router)
api_router.include_router(customer_messages.router)
api_router.include_router(whatsapp_notifications.router)
api_router.include_router(email_notifications.router)
api_router.include_router(sms_notifications.router)
api_router.include_router(reminder_jobs.router)
api_router.include_router(communication_logs.router)
api_router.include_router(alert_events.router)
