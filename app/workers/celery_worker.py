"""
Celery Worker - Background task processing for notifications.
Handles async sending, retry logic, and scheduled reminder processing.
"""

from celery import Celery
from celery.schedules import crontab
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "zenseva_communication",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_default_retry_delay=30,
    task_max_retries=5,
)

# Periodic task schedule (beat)
celery_app.conf.beat_schedule = {
    "process-due-reminders": {
        "task": "app.workers.celery_worker.process_due_reminders",
        "schedule": crontab(minute="*/5"),  # Every 5 minutes
    },
    "retry-failed-notifications": {
        "task": "app.workers.celery_worker.retry_failed_notifications",
        "schedule": crontab(minute="*/10"),  # Every 10 minutes
    },
}


@celery_app.task(bind=True, max_retries=5)
def send_email_task(self, recipient: str, subject: str, body: str):
    """Background task to send email notification."""
    try:
        logger.info(f"Sending email to {recipient}: {subject}")
        # Simulate email sending
        import random
        if random.random() < 0.1:
            raise Exception("SMTP timeout")
        return {"status": "sent", "recipient": recipient}
    except Exception as exc:
        logger.warning(f"Email task failed, retrying: {str(exc)}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 5)


@celery_app.task(bind=True, max_retries=5)
def send_sms_task(self, recipient: str, message: str):
    """Background task to send SMS notification."""
    try:
        logger.info(f"Sending SMS to {recipient}")
        import random
        if random.random() < 0.1:
            raise Exception("SMS provider error")
        return {"status": "sent", "recipient": recipient}
    except Exception as exc:
        logger.warning(f"SMS task failed, retrying: {str(exc)}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 5)


@celery_app.task(bind=True, max_retries=5)
def send_whatsapp_task(self, recipient: str, message: str):
    """Background task to send WhatsApp notification."""
    try:
        logger.info(f"Sending WhatsApp to {recipient}")
        import random
        if random.random() < 0.1:
            raise Exception("WhatsApp API rate limit")
        return {"status": "sent", "recipient": recipient}
    except Exception as exc:
        logger.warning(f"WhatsApp task failed, retrying: {str(exc)}")
        raise self.retry(exc=exc, countdown=2 ** self.request.retries * 5)


@celery_app.task
def process_due_reminders():
    """Periodic task to process all due reminder notifications."""
    logger.info("Processing due reminders...")
    # In production, this would query the database and trigger sends
    return {"status": "processed", "message": "Due reminders processed"}


@celery_app.task
def retry_failed_notifications():
    """Periodic task to retry failed notifications."""
    logger.info("Retrying failed notifications...")
    # In production, this would query failed notifications and retry them
    return {"status": "processed", "message": "Failed notifications retried"}


@celery_app.task(bind=True, max_retries=3)
def send_emergency_alert_task(
    self, recipient_phone: str, recipient_email: str, title: str, description: str
):
    """Background task for emergency multi-channel alert."""
    try:
        logger.info(f"Emergency alert: {title}")
        # Send via all channels
        results = {
            "sms": "sent" if recipient_phone else "skipped",
            "whatsapp": "sent" if recipient_phone else "skipped",
            "email": "sent" if recipient_email else "skipped",
        }
        return {"status": "sent", "channels": results}
    except Exception as exc:
        logger.error(f"Emergency alert failed: {str(exc)}")
        raise self.retry(exc=exc, countdown=5)  # Fast retry for emergencies
