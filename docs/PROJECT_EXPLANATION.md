# ZenSeva Communication Service — Complete Project Explanation

---

## 1. What Problem This Service Solves

ZenSeva is a platform that manages customers across healthcare, legal, and property services. Those customers need to be notified through multiple channels — appointment reminders, document updates, emergency alerts, etc.

**Without this service**: Each part of the platform would implement its own notification logic — duplicated code, no retry handling, no audit trail, inconsistent delivery.

**With this service**: One centralized microservice handles ALL communication. Any other ZenSeva service just calls one API to send a notification. It provides:

- Multi-channel delivery (Email, SMS, WhatsApp) from a single request
- Automatic retries with exponential backoff
- Complete audit trail of every message
- Template management so messages stay consistent
- Scheduled reminders
- Emergency alerts with escalation

---

## 2. Main Users and Roles

| Role | Who | Permissions |
|------|-----|-------------|
| **admin** | System administrators | Full access — create/delete templates, send notifications, view all logs, manage alerts |
| **staff** | Field workers, support agents | Send notifications, view history, schedule reminders. Cannot delete templates. |
| **service** | Other microservices (machine-to-machine) | Send notifications, trigger alerts. Used for automated inter-service calls. |

Authentication is JWT-based. Each token carries the role, and endpoints enforce access control:

```python
@router.delete("/{template_id}", dependencies=[Depends(require_role("admin"))])
```

---

## 3. Database Models/Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `notification_templates` | Reusable message templates with variables | template_name, template_type, message_body, variables (JSON) |
| `customer_messages` | Master record of all outgoing communications | customer_id, customer_name, mobile_number, email, delivery_channel, status |
| `whatsapp_notifications` | WhatsApp delivery tracking | recipient_phone, message_body, status, provider_message_id, retry_count |
| `email_notifications` | Email delivery tracking | recipient_email, subject, body_html, status, retry_count |
| `sms_notifications` | SMS delivery tracking | recipient_phone, message_body, status, provider_message_id, retry_count |
| `reminder_jobs` | Scheduled future notifications | customer_id, reminder_type, scheduled_time, delivery_channel, status |
| `alert_events` | Emergency multi-channel alerts | alert_type, priority, recipient_phone, recipient_email, channels_used, escalation_level |
| `communication_logs` | Audit trail of ALL events | event_type, channel, recipient, status, notification_id, timestamp |

### ER Diagram

```
notification_templates (1) ──→ (many) whatsapp_notifications
                           ──→ (many) email_notifications
                           ──→ (many) sms_notifications

customer_messages (1) ──→ (many) communication_logs

whatsapp_notifications (1) ──→ (many) communication_logs
email_notifications (1) ──→ (many) communication_logs
sms_notifications (1) ──→ (many) communication_logs

reminder_jobs (1) ──→ (many) communication_logs
alert_events (1) ──→ (many) communication_logs
```

---

## 4. API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/token` | Generate JWT token |
| GET | `/health` | Service health check |

### Notification Templates
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/templates/` | Create template |
| GET | `/api/v1/templates/` | List all templates |
| GET | `/api/v1/templates/{id}` | Get single template |
| PUT | `/api/v1/templates/{id}` | Update template |
| DELETE | `/api/v1/templates/{id}` | Delete template (admin only) |

### Notifications (WhatsApp / Email / SMS)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/whatsapp/send` | Send WhatsApp message |
| GET | `/api/v1/whatsapp/history` | WhatsApp history |
| POST | `/api/v1/email/send` | Send email |
| GET | `/api/v1/email/history` | Email history |
| POST | `/api/v1/sms/send` | Send SMS |
| GET | `/api/v1/sms/history` | SMS history |

### Reminders
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/reminders/` | Schedule reminder |
| GET | `/api/v1/reminders/` | List reminders |
| GET | `/api/v1/reminders/{id}` | Get reminder |
| PUT | `/api/v1/reminders/{id}` | Update reminder |
| DELETE | `/api/v1/reminders/{id}` | Cancel reminder |
| POST | `/api/v1/reminders/process-due` | Process due reminders |

### Alerts
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/alerts/emergency` | Trigger emergency alert |
| POST | `/api/v1/alerts/{id}/escalate` | Escalate alert |
| GET | `/api/v1/alerts/history` | Alert history |

### Logs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/logs/` | View communication logs |

---

## 5. Sample Request/Response

### Send WhatsApp Notification

```json
// POST /api/v1/whatsapp/send
// Header: Authorization: Bearer <token>

// REQUEST:
{
  "recipient_phone": "+918197377955",
  "recipient_name": "Akshay",
  "message_body": "Your appointment is confirmed for tomorrow at 10 AM."
}

// RESPONSE (201 Created):
{
  "id": "9d1075ca-2113-4f3f-8b9d-abc123def456",
  "recipient_phone": "+918197377955",
  "recipient_name": "Akshay",
  "message_body": "Your appointment is confirmed for tomorrow at 10 AM.",
  "status": "SENT",
  "provider_message_id": "wamid.64b82f327ee345d5a9d5",
  "retry_count": 0,
  "error_message": null,
  "sent_at": "2026-05-12T10:30:00Z",
  "delivered_at": null,
  "created_at": "2026-05-12T10:30:00Z"
}
```

### Send Email

```json
// POST /api/v1/email/send

// REQUEST:
{
  "recipient_email": "akshayrnayak72@gmail.com",
  "recipient_name": "Akshay",
  "subject": "Inspection Report Ready",
  "body_html": "<h1>Report Ready</h1><p>Your inspection report is available.</p>",
  "is_html": true
}

// RESPONSE (201 Created):
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "recipient_email": "akshayrnayak72@gmail.com",
  "recipient_name": "Akshay",
  "subject": "Inspection Report Ready",
  "status": "SENT",
  "retry_count": 0,
  "sent_at": "2026-05-12T10:31:00Z"
}
```

### Trigger Emergency Alert

```json
// POST /api/v1/alerts/emergency

// REQUEST:
{
  "alert_type": "EMERGENCY_HEALTH",
  "priority": "CRITICAL",
  "title": "Patient Critical Condition",
  "description": "Patient showing critical vital signs. BP: 180/120.",
  "recipient_id": "33333333-3333-3333-3333-333333333333",
  "recipient_phone": "+918197377955",
  "recipient_email": "akshayrnayak72@gmail.com",
  "channels_used": "SMS,WHATSAPP,EMAIL"
}

// RESPONSE (201 Created):
{
  "id": "74bf8767-965d-4c76-9b9b-d5d4ab563302",
  "alert_type": "EMERGENCY_HEALTH",
  "priority": "CRITICAL",
  "title": "Patient Critical Condition",
  "status": "SENT",
  "escalation_level": 0,
  "channels_used": "SMS,WHATSAPP,EMAIL",
  "created_at": "2026-05-12T10:31:00Z"
}
```

---

## 6. End-to-End Notification Workflow

```
┌──────────────────────────────────────────────────────────────────┐
│  1. Client sends POST /api/v1/whatsapp/send                      │
│     with JWT token + recipient details                           │
└──────────────────────┬───────────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  2. Middleware checks:                                           │
│     • JWT token valid? → 401 if not                              │
│     • Role allowed? → 403 if not                                 │
│     • Rate limit exceeded? → 429 if yes                          │
└──────────────────────┬───────────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  3. Pydantic schema validates request body                       │
│     • Phone format valid? → 422 if not                           │
│     • Required fields present? → 422 if not                      │
└──────────────────────┬───────────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  4. Service creates notification record (status: QUEUED)         │
│     → INSERT into whatsapp_notifications                         │
└──────────────────────┬───────────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  5. RetryService attempts delivery:                              │
│     • Attempt 1: Call WhatsApp API                               │
│     • If fails: Wait 1s, retry                                   │
│     • Attempt 2: Wait 2s, retry                                  │
│     • Attempt 3: Wait 4s, retry (max)                            │
│     • All failed? → Mark as FAILED (dead letter)                 │
└──────────────────────┬───────────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  6. Update notification record:                                  │
│     • Success → status=SENT, store provider_message_id           │
│     • Failure → status=FAILED, store error_message               │
└──────────────────────┬───────────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  7. LoggingService creates audit entry:                          │
│     → INSERT into communication_logs                             │
│     (event_type, channel, recipient, status, timestamp)          │
└──────────────────────┬───────────────────────────────────────────┘
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│  8. Return response to client with notification details          │
└──────────────────────────────────────────────────────────────────┘
```

---

## 7. Edge Cases Handled

| Edge Case | How It's Handled |
|-----------|-----------------|
| **Provider down** | Exponential backoff retry (1s → 2s → 4s), max 3 attempts |
| **All retries exhausted** | Marked as FAILED, logged as dead letter for manual review |
| **Invalid phone/email** | Pydantic validation rejects with 422 + clear error message |
| **Expired JWT token** | Returns 401 Unauthorized |
| **Wrong role accessing endpoint** | Returns 403 Forbidden |
| **Rate limit exceeded** | Returns 429 Too Many Requests (100 req/min per IP) |
| **Duplicate template name** | Database constraint prevents duplicates |
| **Emergency alert unacknowledged** | Escalation endpoint increases level, notifies higher authority |
| **Database connection failure** | Global exception handler catches and returns 500 with logging |
| **Concurrent requests** | Async engine handles multiple requests without blocking |
| **Backoff delay too long** | Capped at 5 minutes maximum regardless of retry count |
| **Missing optional fields** | Pydantic uses Optional[] with defaults, no crash |
| **Large message body** | Field max_length validation (4096 chars for WhatsApp) |

---

## 8. How to Run the Project Locally

```bash
# 1. Navigate to project
cd service-communication

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. The .env is already configured for SQLite (no PostgreSQL needed locally)
#    DATABASE_URL=sqlite+aiosqlite:///./zenseva_communication.db

# 5. Start the server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# 6. (Optional) Seed demo data
python -m app.seed.seed_data

# 7. Run the full demo
python demo.py              # Auto mode
python demo.py --step       # Presentation mode (pauses between steps)

# 8. Open Swagger UI in browser
# http://127.0.0.1:8000/docs
```

### No external dependencies needed for local dev:
- SQLite instead of PostgreSQL
- Simulated providers instead of real Twilio/SendGrid
- In-memory rate limiting instead of Redis

---

## 9. How This Service Connects with Other ZenSeva Services

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│  service-customer   │     │  service-inspection  │     │  service-billing    │
│  (Customer CRUD)    │     │  (Property visits)   │     │  (Payments)         │
└────────┬────────────┘     └────────┬─────────────┘     └────────┬────────────┘
         │                           │                             │
         │  "Send reminder to        │  "Notify customer           │  "Payment
         │   customer X"             │   inspection done"          │   receipt"
         │                           │                             │
         ▼                           ▼                             ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                      service-communication                                    │
│                                                                              │
│   POST /api/v1/whatsapp/send    (WhatsApp messages)                          │
│   POST /api/v1/email/send       (Email notifications)                        │
│   POST /api/v1/sms/send         (SMS messages)                               │
│   POST /api/v1/alerts/emergency (Emergency multi-channel)                    │
│   POST /api/v1/reminders/       (Scheduled notifications)                    │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
   External Providers (Twilio, SendGrid, Meta WhatsApp API)
```

### How other services call it:

1. They get a JWT token with `role=service`
2. They call the REST API endpoints directly over HTTP
3. In production, this could also be event-driven via Redis/RabbitMQ

### Example — service-inspection completes a visit:

```python
import httpx

# Get service token
token_resp = httpx.post("http://service-communication:8000/auth/token?user_id=inspection-svc&role=service")
token = token_resp.json()["access_token"]

# Send notification
httpx.post(
    "http://service-communication:8000/api/v1/email/send",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "recipient_email": "customer@example.com",
        "recipient_name": "Akshay",
        "subject": "Property Inspection Complete",
        "body_html": "<p>Your inspection report is ready to download.</p>",
        "is_html": True,
    }
)
```

---

## 10. Future Improvements

| Priority | Improvement | Why |
|----------|-------------|-----|
| **High** | Real provider integration (Twilio, SendGrid) | Actually deliver messages |
| **High** | WebSocket for real-time delivery status | Clients get instant status updates |
| **High** | Push notifications (FCM/APNs) | Mobile app support |
| **Medium** | Dead Letter Queue management UI | Review and retry failed messages |
| **Medium** | Message scheduling with timezone support | Send at recipient's local time |
| **Medium** | Batch notification sending | Send to 1000+ recipients efficiently |
| **Medium** | Webhook callbacks for delivery status | External systems get notified on delivery |
| **Medium** | Template versioning + A/B testing | Test which messages perform better |
| **Low** | OpenTelemetry tracing | Distributed tracing across microservices |
| **Low** | GraphQL API layer | Flexible querying for frontend |
| **Low** | Multi-tenant support | Serve multiple organizations |
| **Low** | Message encryption at rest | Compliance for healthcare/legal data |
| **Low** | Analytics dashboard | Delivery metrics, channel performance |

---

## Quick Reference — Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12 |
| Framework | FastAPI |
| Database | PostgreSQL 16 (prod) / SQLite (dev) |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Queue | Celery + Redis |
| Auth | JWT (python-jose) |
| Validation | Pydantic v2 |
| HTTP Client | httpx |
| Containerization | Docker + Docker Compose |
| Testing | pytest + pytest-asyncio |
