# ZenSeva Communication Service

A production-ready microservice for managing all customer communication and notifications in the ZenSeva platform.

## Overview

The **service-communication** microservice handles multi-channel notifications (Email, SMS, WhatsApp), scheduled reminders, emergency alerts, and comprehensive communication logging with retry mechanisms.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    API Gateway                            │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│              service-communication                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  Routes  │→ │ Services │→ │  Models  │              │
│  └──────────┘  └──────────┘  └──────────┘              │
│       │              │              │                    │
│       ▼              ▼              ▼                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  Schemas │  │  Celery  │  │PostgreSQL│              │
│  └──────────┘  └──────────┘  └──────────┘              │
│                      │                                   │
│                      ▼                                   │
│               ┌──────────┐                              │
│               │  Redis   │                              │
│               └──────────┘                              │
└─────────────────────────────────────────────────────────┘
```

## Features

- **Email Notifications** - SMTP integration with HTML support and queue-based sending
- **SMS Notifications** - Provider integration with async delivery
- **WhatsApp Notifications** - Meta/Twilio API simulation with delivery tracking
- **Notification Templates** - Reusable templates with variable substitution
- **Reminder Jobs** - Cron-style scheduled reminders with auto-send
- **Emergency Alerts** - Multi-channel priority alerts with escalation
- **Communication Logs** - Complete audit trail of all communications
- **Retry Mechanism** - Exponential backoff with dead-letter handling
- **JWT Authentication** - Role-based access control (admin, staff, service)
- **Rate Limiting** - Per-IP request throttling

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12 |
| Framework | FastAPI |
| Database | PostgreSQL 16 |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Queue | Celery + Redis |
| Auth | JWT (python-jose) |
| Containerization | Docker + Docker Compose |

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose (optional)

### Local Setup

```bash
# Clone and navigate
cd service-communication

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Seed demo data
python -m app.seed.seed_data

# Start the application
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Docker Setup

```bash
# Build and start all services
docker-compose up --build -d

# Check service health
curl http://localhost:8000/health

# View logs
docker-compose logs -f app
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://postgres:postgres@localhost:5432/zenseva_communication` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | (change in production) |
| `SMTP_HOST` | SMTP server host | `smtp.mailtrap.io` |
| `MAX_RETRY_COUNT` | Maximum retry attempts | `5` |
| `RATE_LIMIT_PER_MINUTE` | API rate limit per IP | `100` |

See `.env.example` for the complete list.

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/token` | Generate JWT token (dev) |

### Notification Templates
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/templates/` | Create template |
| GET | `/api/v1/templates/` | List templates |
| GET | `/api/v1/templates/{id}` | Get template |
| PUT | `/api/v1/templates/{id}` | Update template |
| DELETE | `/api/v1/templates/{id}` | Delete template |

### Email Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/email/send` | Send email |
| GET | `/api/v1/email/history` | Email history |

### SMS Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/sms/send` | Send SMS |
| GET | `/api/v1/sms/history` | SMS history |

### WhatsApp Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/whatsapp/send` | Send WhatsApp |
| GET | `/api/v1/whatsapp/history` | WhatsApp history |

### Reminder Jobs
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/reminders/` | Schedule reminder |
| GET | `/api/v1/reminders/` | List reminders |
| GET | `/api/v1/reminders/{id}` | Get reminder |
| PUT | `/api/v1/reminders/{id}` | Update reminder |
| DELETE | `/api/v1/reminders/{id}` | Cancel reminder |
| POST | `/api/v1/reminders/process-due` | Process due reminders |

### Alert Events
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/alerts/emergency` | Trigger emergency alert |
| GET | `/api/v1/alerts/history` | Alert history |
| POST | `/api/v1/alerts/{id}/escalate` | Escalate alert |

### Communication Logs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/logs/` | List communication logs |

### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Service health check |

## Sample API Requests

### Generate Token
```bash
curl -X POST "http://localhost:8000/auth/token?user_id=admin&role=admin"
```

### Send WhatsApp Notification
```bash
curl -X POST http://localhost:8000/api/v1/whatsapp/send \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_phone": "+919876543210",
    "recipient_name": "Rajesh Kumar",
    "message_body": "Your medical appointment is confirmed for tomorrow at 10 AM."
  }'
```

### Send Email
```bash
curl -X POST http://localhost:8000/api/v1/email/send \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_email": "customer@example.com",
    "recipient_name": "Priya Sharma",
    "subject": "Inspection Report Ready",
    "body_html": "<h1>Report Ready</h1><p>Your inspection report is available.</p>",
    "is_html": true
  }'
```

### Trigger Emergency Alert
```bash
curl -X POST http://localhost:8000/api/v1/alerts/emergency \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "alert_type": "EMERGENCY_HEALTH",
    "priority": "CRITICAL",
    "title": "Patient Critical Condition",
    "description": "Patient showing critical vital signs.",
    "recipient_id": "11111111-1111-1111-1111-111111111111",
    "recipient_phone": "+919876543210",
    "recipient_email": "doctor@hospital.com",
    "channels_used": "SMS,WHATSAPP,EMAIL"
  }'
```

### Schedule Reminder
```bash
curl -X POST http://localhost:8000/api/v1/reminders/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "11111111-1111-1111-1111-111111111111",
    "reminder_type": "MEDICAL_VISIT",
    "title": "Annual Health Checkup",
    "message": "Your annual checkup is scheduled for tomorrow at 10 AM.",
    "delivery_channel": "WHATSAPP",
    "scheduled_time": "2026-06-01T10:00:00Z"
  }'
```

## Testing

```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_notifications.py -v

# Run with coverage
pytest --cov=app tests/ -v
```

## Celery Workers

```bash
# Start Celery worker
celery -A app.workers.celery_worker worker --loglevel=info

# Start Celery beat (scheduler)
celery -A app.workers.celery_worker beat --loglevel=info
```

## ER Diagram

```
┌──────────────────────┐     ┌──────────────────────┐
│ notification_templates│     │   customer_messages   │
├──────────────────────┤     ├──────────────────────┤
│ id (UUID, PK)        │     │ id (UUID, PK)        │
│ template_name        │     │ customer_id (UUID)   │
│ template_type        │     │ customer_name        │
│ subject              │     │ mobile_number        │
│ message_body         │     │ email                │
│ variables (JSON)     │     │ message_type         │
│ created_at           │     │ delivery_channel     │
│ updated_at           │     │ status               │
└──────────────────────┘     │ sent_at              │
                             └──────────────────────┘

┌──────────────────────┐     ┌──────────────────────┐
│whatsapp_notifications│     │ email_notifications   │
├──────────────────────┤     ├──────────────────────┤
│ id (UUID, PK)        │     │ id (UUID, PK)        │
│ recipient_phone      │     │ recipient_email      │
│ message_body         │     │ subject              │
│ status               │     │ body_html            │
│ provider_message_id  │     │ status               │
│ retry_count          │     │ retry_count          │
│ sent_at              │     │ sent_at              │
└──────────────────────┘     └──────────────────────┘

┌──────────────────────┐     ┌──────────────────────┐
│  sms_notifications   │     │    reminder_jobs      │
├──────────────────────┤     ├──────────────────────┤
│ id (UUID, PK)        │     │ id (UUID, PK)        │
│ recipient_phone      │     │ customer_id (UUID)   │
│ message_body         │     │ reminder_type        │
│ status               │     │ scheduled_time       │
│ retry_count          │     │ status               │
│ sent_at              │     │ retry_count          │
└──────────────────────┘     └──────────────────────┘

┌──────────────────────┐     ┌──────────────────────┐
│  communication_logs  │     │    alert_events       │
├──────────────────────┤     ├──────────────────────┤
│ id (UUID, PK)        │     │ id (UUID, PK)        │
│ event_type           │     │ alert_type           │
│ channel              │     │ priority             │
│ recipient            │     │ title                │
│ notification_id      │     │ recipient_id (UUID)  │
│ status               │     │ channels_used        │
│ response_message     │     │ status               │
│ timestamp            │     │ escalation_level     │
└──────────────────────┘     └──────────────────────┘
```

## Git Commit Messages

```
feat: added whatsapp notification service
feat: implemented retry mechanism with exponential backoff
feat: added emergency alert multi-channel flow
feat: implemented reminder job scheduling
feat: added communication logging service
fix: corrected communication log tracking
fix: resolved retry count overflow issue
docs: added API workflow documentation
docs: updated README with setup instructions
chore: added Docker and docker-compose configuration
test: added notification API test cases
test: added alert escalation tests
```

## Future Improvements

- [ ] WebSocket support for real-time delivery status updates
- [ ] Push notification channel (FCM/APNs)
- [ ] Template versioning and A/B testing
- [ ] Analytics dashboard for delivery metrics
- [ ] Webhook callbacks for delivery status
- [ ] Message scheduling with timezone support
- [ ] Batch notification sending
- [ ] DLQ (Dead Letter Queue) management UI
- [ ] Multi-tenant support
- [ ] OpenTelemetry tracing integration
- [ ] GraphQL API layer
- [ ] Message content encryption at rest
