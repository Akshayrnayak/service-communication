# ZenSeva Communication Service - API Flow Documentation

## Notification Lifecycle

```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│ CREATED │ →  │ QUEUED  │ →  │ SENDING │ →  │  SENT   │ →  │DELIVERED│
└─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘
                                    │                              │
                                    ▼                              ▼
                              ┌─────────┐                   ┌─────────┐
                              │ FAILED  │ ←─── retry ────── │ BOUNCED │
                              └─────────┘                   └─────────┘
                                    │
                                    ▼ (retry_count < max)
                              ┌─────────┐
                              │ RETRYING│ → back to SENDING
                              └─────────┘
                                    │
                                    ▼ (retry_count >= max)
                              ┌─────────────┐
                              │ DEAD_LETTER │
                              └─────────────┘
```

## Workflow 1: Inspection Completed

Inter-service communication flow when a property inspection is completed.

```
┌──────────────────┐
│  service-estate  │
│ (Inspection Done)│
└────────┬─────────┘
         │ POST /api/v1/whatsapp/send
         │ POST /api/v1/email/send
         ▼
┌──────────────────────────────────────┐
│       service-communication          │
│                                      │
│  1. Receive notification request     │
│  2. Load template (VISIT_COMPLETE)   │
│  3. Render template with variables   │
│  4. Queue WhatsApp message           │
│  5. Queue Email message              │
│  6. Process via Celery workers       │
│  7. Track delivery status            │
│  8. Log communication events         │
└──────────────────────────────────────┘
         │
         ▼
┌──────────────────┐    ┌──────────────────┐
│  WhatsApp API    │    │    SMTP Server   │
│  (Meta/Twilio)   │    │                  │
└──────────────────┘    └──────────────────┘
         │                       │
         ▼                       ▼
┌──────────────────────────────────────┐
│       communication_logs             │
│  - event_type: SEND                  │
│  - channel: WHATSAPP / EMAIL         │
│  - status: SUCCESS / FAILURE         │
└──────────────────────────────────────┘
```

## Workflow 2: Medical Reminder

Scheduled reminder flow for medical visits.

```
┌──────────────────────┐
│  service-parent-care │
│  (Schedule Reminder) │
└──────────┬───────────┘
           │ POST /api/v1/reminders/
           ▼
┌──────────────────────────────────────┐
│       service-communication          │
│                                      │
│  1. Create reminder_job record       │
│     - status: SCHEDULED              │
│     - scheduled_time: future date    │
│                                      │
│  2. Celery Beat checks every 5 min  │
│     - Query due reminders            │
│     - Process each reminder          │
│                                      │
│  3. When scheduled_time reached:     │
│     - Load reminder details          │
│     - Select delivery channel        │
│     - Send notification              │
│     - Update status: SENT            │
│                                      │
│  4. Track delivery                   │
│     - Monitor delivery callback      │
│     - Update status: DELIVERED       │
│     - Log communication event        │
└──────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│         Celery Beat Schedule         │
│                                      │
│  process-due-reminders: */5 min      │
│  retry-failed-notifications: */10 min│
└──────────────────────────────────────┘
```

## Workflow 3: Emergency Alert

Multi-channel emergency notification with escalation.

```
┌──────────────────────┐
│   Alert Trigger      │
│ (Any ZenSeva Service)│
└──────────┬───────────┘
           │ POST /api/v1/alerts/emergency
           ▼
┌──────────────────────────────────────────────────┐
│            service-communication                  │
│                                                  │
│  1. Create alert_event record                    │
│     - priority: CRITICAL                         │
│     - status: PROCESSING                         │
│                                                  │
│  2. Priority Queue Processing                    │
│     ┌─────────────────────────────────────┐     │
│     │  CRITICAL → Immediate processing    │     │
│     │  HIGH     → Next in queue           │     │
│     │  MEDIUM   → Standard queue          │     │
│     │  LOW      → Batch processing        │     │
│     └─────────────────────────────────────┘     │
│                                                  │
│  3. Multi-Channel Send (parallel)                │
│     ├── SMS    → SMS Provider API                │
│     ├── WhatsApp → Meta/Twilio API               │
│     └── Email  → SMTP Server                     │
│                                                  │
│  4. Result Aggregation                           │
│     - All success → status: SENT                 │
│     - Partial    → status: SENT + escalate       │
│     - All fail   → status: FAILED + escalate     │
│                                                  │
│  5. Escalation (if needed)                       │
│     - Level 1: Retry failed channels             │
│     - Level 2: Notify supervisor                 │
│     - Level 3: System-wide alert                 │
└──────────────────────────────────────────────────┘
```

## Retry Workflow

Exponential backoff retry mechanism for failed notifications.

```
┌─────────────────────────────────────────────────────────┐
│                  Retry Flow                               │
│                                                          │
│  Attempt 1: Send notification                            │
│      │ FAIL                                              │
│      ▼                                                   │
│  Wait 5s (initial_delay * backoff^0)                     │
│      │                                                   │
│  Attempt 2: Retry                                        │
│      │ FAIL                                              │
│      ▼                                                   │
│  Wait 10s (initial_delay * backoff^1)                    │
│      │                                                   │
│  Attempt 3: Retry                                        │
│      │ FAIL                                              │
│      ▼                                                   │
│  Wait 20s (initial_delay * backoff^2)                    │
│      │                                                   │
│  Attempt 4: Retry                                        │
│      │ FAIL                                              │
│      ▼                                                   │
│  Wait 40s (initial_delay * backoff^3)                    │
│      │                                                   │
│  Attempt 5: Final retry                                  │
│      │ FAIL                                              │
│      ▼                                                   │
│  ┌─────────────────────────────────┐                    │
│  │  DEAD LETTER                     │                    │
│  │  - Mark as permanently failed    │                    │
│  │  - Log failure event             │                    │
│  │  - Notify admin (if critical)    │                    │
│  └─────────────────────────────────┘                    │
└─────────────────────────────────────────────────────────┘

Configuration:
  MAX_RETRY_COUNT = 5
  RETRY_BACKOFF_BASE = 2
  RETRY_INITIAL_DELAY = 5 seconds
  MAX_DELAY_CAP = 300 seconds (5 minutes)
```

## Inter-Service Communication

How other ZenSeva services interact with the communication service.

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ service-estate  │  │service-parent-  │  │ service-legal   │
│                 │  │     care        │  │                 │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                     │
         │  REST API calls    │                     │
         ▼                    ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  service-communication                        │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Templates │  │ Channels │  │ Reminders│  │  Alerts  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                      │                                       │
│                      ▼                                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Communication Logs                       │   │
│  │  (Complete audit trail of all communications)         │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Authentication Flow

```
┌──────────┐         ┌──────────────────┐         ┌──────────┐
│  Client  │ ──────→ │  Auth Middleware  │ ──────→ │   API    │
└──────────┘         └──────────────────┘         └──────────┘
     │                       │
     │ Bearer Token          │ Verify JWT
     │                       │ Check Role
     │                       │ Rate Limit
     │                       │
     │                ┌──────▼──────┐
     │                │   Roles:    │
     │                │  - admin    │ Full access
     │                │  - staff    │ Read + Send
     │                │  - service  │ Inter-service
     │                └─────────────┘
```

## API Response Format

### Success Response
```json
{
  "id": "uuid",
  "status": "SENT",
  "created_at": "2026-01-01T00:00:00Z",
  ...
}
```

### Paginated Response
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

### Error Response
```json
{
  "detail": "Error message",
  "error_type": "NotificationDeliveryError"
}
```
