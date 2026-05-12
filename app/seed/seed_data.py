"""
Seed Data Script - Populates the database with demo data.
Run with: python -m app.seed.seed_data
"""

import asyncio
import uuid
from datetime import datetime, timezone, timedelta

from app.core.database import AsyncSessionLocal, init_db
from app.models.notification_template import NotificationTemplate, TemplateType
from app.models.customer_message import (
    CustomerMessage, MessageType, DeliveryChannel, MessageStatus
)
from app.models.reminder_job import ReminderJob, ReminderType, ReminderStatus
from app.models.alert_event import AlertEvent, AlertType, AlertPriority, AlertStatus
from app.models.communication_log import (
    CommunicationLog, LogEventType, LogChannel, LogStatus
)


# Demo customer IDs
CUSTOMER_IDS = [
    uuid.UUID("11111111-1111-1111-1111-111111111111"),
    uuid.UUID("22222222-2222-2222-2222-222222222222"),
    uuid.UUID("33333333-3333-3333-3333-333333333333"),
]


async def seed_templates(session):
    """Seed notification templates."""
    templates = [
        NotificationTemplate(
            template_name="Medical Visit Reminder",
            template_type=TemplateType.REMINDER,
            subject="Upcoming Medical Visit Reminder",
            message_body=(
                "Dear {{customer_name}}, this is a reminder for your "
                "medical visit scheduled on {{visit_date}} at {{location}}."
            ),
            variables=["customer_name", "visit_date", "location"],
        ),
        NotificationTemplate(
            template_name="Inspection Complete",
            template_type=TemplateType.VISIT_COMPLETE,
            subject="Property Inspection Completed",
            message_body=(
                "Hi {{customer_name}}, your property inspection at "
                "{{property_address}} has been completed. Report: {{report_link}}"
            ),
            variables=["customer_name", "property_address", "report_link"],
        ),
        NotificationTemplate(
            template_name="Emergency Health Alert",
            template_type=TemplateType.ALERT,
            subject="URGENT: Health Emergency Alert",
            message_body=(
                "EMERGENCY: {{alert_description}}. "
                "Patient: {{patient_name}}. Immediate action required."
            ),
            variables=["alert_description", "patient_name"],
        ),
        NotificationTemplate(
            template_name="Document Update Notification",
            template_type=TemplateType.DOCUMENT_UPDATE,
            subject="Document Updated: {{document_name}}",
            message_body=(
                "Dear {{customer_name}}, the document '{{document_name}}' "
                "has been updated. Please review at: {{document_link}}"
            ),
            variables=["customer_name", "document_name", "document_link"],
        ),
        NotificationTemplate(
            template_name="General Notification",
            template_type=TemplateType.GENERAL,
            subject="ZenSeva Notification",
            message_body="Dear {{customer_name}}, {{message_content}}",
            variables=["customer_name", "message_content"],
        ),
    ]
    session.add_all(templates)
    await session.flush()
    print(f"  ✓ Seeded {len(templates)} notification templates")


async def seed_customer_messages(session):
    """Seed customer messages."""
    messages = [
        CustomerMessage(
            customer_id=CUSTOMER_IDS[0],
            customer_name="Akshay",
            mobile_number="+918197377955",
            email="akshay@example.com",
            message_type=MessageType.REMINDER,
            delivery_channel=DeliveryChannel.WHATSAPP,
            status=MessageStatus.DELIVERED,
            sent_at=datetime.now(timezone.utc) - timedelta(hours=2),
        ),
        CustomerMessage(
            customer_id=CUSTOMER_IDS[1],
            customer_name="Priya Sharma",
            mobile_number="+919876543211",
            email="priya.sharma@example.com",
            message_type=MessageType.NOTIFICATION,
            delivery_channel=DeliveryChannel.EMAIL,
            status=MessageStatus.SENT,
            sent_at=datetime.now(timezone.utc) - timedelta(hours=1),
        ),
        CustomerMessage(
            customer_id=CUSTOMER_IDS[2],
            customer_name="Amit Patel",
            mobile_number="+919876543212",
            email="amit.patel@example.com",
            message_type=MessageType.ALERT,
            delivery_channel=DeliveryChannel.SMS,
            status=MessageStatus.PENDING,
        ),
    ]
    session.add_all(messages)
    await session.flush()
    print(f"  ✓ Seeded {len(messages)} customer messages")


async def seed_reminder_jobs(session):
    """Seed reminder jobs."""
    reminders = [
        ReminderJob(
            customer_id=CUSTOMER_IDS[0],
            reminder_type=ReminderType.MEDICAL_VISIT,
            title="Annual Health Checkup",
            message="Reminder: Your annual health checkup is tomorrow at 10:00 AM.",
            delivery_channel="WHATSAPP",
            scheduled_time=datetime.now(timezone.utc) + timedelta(days=1),
            status=ReminderStatus.SCHEDULED,
        ),
        ReminderJob(
            customer_id=CUSTOMER_IDS[1],
            reminder_type=ReminderType.LEGAL_DOCUMENT,
            title="Document Submission Deadline",
            message="Your legal document submission deadline is in 3 days.",
            delivery_channel="EMAIL",
            scheduled_time=datetime.now(timezone.utc) + timedelta(days=3),
            status=ReminderStatus.SCHEDULED,
        ),
        ReminderJob(
            customer_id=CUSTOMER_IDS[2],
            reminder_type=ReminderType.INSPECTION,
            title="Property Inspection Scheduled",
            message="Your property inspection is scheduled for next week.",
            delivery_channel="SMS",
            scheduled_time=datetime.now(timezone.utc) + timedelta(days=7),
            status=ReminderStatus.SCHEDULED,
        ),
    ]
    session.add_all(reminders)
    await session.flush()
    print(f"  ✓ Seeded {len(reminders)} reminder jobs")


async def seed_alert_events(session):
    """Seed alert events."""
    alerts = [
        AlertEvent(
            alert_type=AlertType.EMERGENCY_HEALTH,
            priority=AlertPriority.CRITICAL,
            title="Patient Critical Condition",
            description="Patient Rajesh Kumar showing critical vital signs.",
            recipient_id=CUSTOMER_IDS[0],
            recipient_phone="+919876543210",
            recipient_email="rajesh.kumar@example.com",
            channels_used="SMS,WHATSAPP,EMAIL",
            status=AlertStatus.SENT,
        ),
        AlertEvent(
            alert_type=AlertType.LEGAL_DEADLINE,
            priority=AlertPriority.HIGH,
            title="Legal Filing Deadline Tomorrow",
            description="Court filing deadline for case #12345 is tomorrow.",
            recipient_id=CUSTOMER_IDS[1],
            recipient_phone="+919876543211",
            recipient_email="priya.sharma@example.com",
            channels_used="EMAIL,SMS",
            status=AlertStatus.SENT,
        ),
    ]
    session.add_all(alerts)
    await session.flush()
    print(f"  ✓ Seeded {len(alerts)} alert events")


async def seed_communication_logs(session):
    """Seed communication logs."""
    logs = [
        CommunicationLog(
            event_type=LogEventType.SEND,
            channel=LogChannel.WHATSAPP,
            recipient="+919876543210",
            status=LogStatus.SUCCESS,
            response_message="WhatsApp message delivered successfully",
        ),
        CommunicationLog(
            event_type=LogEventType.FAILURE,
            channel=LogChannel.EMAIL,
            recipient="test@example.com",
            status=LogStatus.FAILURE,
            response_message="SMTP connection timeout",
        ),
        CommunicationLog(
            event_type=LogEventType.RETRY,
            channel=LogChannel.SMS,
            recipient="+919876543212",
            status=LogStatus.RETRYING,
            response_message="Retry attempt 2/5",
        ),
    ]
    session.add_all(logs)
    await session.flush()
    print(f"  ✓ Seeded {len(logs)} communication logs")


async def run_seed():
    """Run all seed functions."""
    print("\n🌱 Seeding ZenSeva Communication Service database...\n")
    await init_db()

    async with AsyncSessionLocal() as session:
        try:
            await seed_templates(session)
            await seed_customer_messages(session)
            await seed_reminder_jobs(session)
            await seed_alert_events(session)
            await seed_communication_logs(session)
            await session.commit()
            print("\n✅ Database seeded successfully!\n")
        except Exception as e:
            await session.rollback()
            print(f"\n❌ Seeding failed: {str(e)}\n")
            raise


if __name__ == "__main__":
    asyncio.run(run_seed())
