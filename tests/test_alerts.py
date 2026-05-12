"""
Tests for Alert Events and Emergency Notification APIs.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_trigger_emergency_alert(client: AsyncClient, auth_headers: dict):
    """Test triggering an emergency alert."""
    payload = {
        "alert_type": "EMERGENCY_HEALTH",
        "priority": "CRITICAL",
        "title": "Patient Critical Condition",
        "description": "Patient showing critical vital signs. Immediate attention needed.",
        "recipient_id": "11111111-1111-1111-1111-111111111111",
        "recipient_phone": "+919876543210",
        "recipient_email": "patient@example.com",
        "channels_used": "SMS,WHATSAPP,EMAIL",
    }
    response = await client.post(
        "/api/v1/alerts/emergency", json=payload, headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["alert_type"] == "EMERGENCY_HEALTH"
    assert data["priority"] == "CRITICAL"
    assert data["status"] in ["SENT", "FAILED", "PROCESSING"]


@pytest.mark.asyncio
async def test_alert_history(client: AsyncClient, auth_headers: dict):
    """Test getting alert event history."""
    response = await client.get("/api/v1/alerts/history", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_escalate_alert(client: AsyncClient, auth_headers: dict):
    """Test escalating an alert."""
    # Create alert first
    payload = {
        "alert_type": "CRITICAL_INSPECTION",
        "priority": "HIGH",
        "title": "Inspection Failure",
        "description": "Critical safety inspection failure detected.",
        "recipient_id": "22222222-2222-2222-2222-222222222222",
        "recipient_phone": "+919876543211",
    }
    create_resp = await client.post(
        "/api/v1/alerts/emergency", json=payload, headers=auth_headers
    )
    alert_id = create_resp.json()["id"]

    # Escalate
    response = await client.post(
        f"/api/v1/alerts/{alert_id}/escalate", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["escalation_level"] >= 1
    assert data["status"] == "ESCALATED"


@pytest.mark.asyncio
async def test_create_reminder(client: AsyncClient, auth_headers: dict):
    """Test creating a reminder job."""
    payload = {
        "customer_id": "11111111-1111-1111-1111-111111111111",
        "reminder_type": "MEDICAL_VISIT",
        "title": "Annual Checkup Reminder",
        "message": "Your annual checkup is scheduled for tomorrow.",
        "delivery_channel": "WHATSAPP",
        "scheduled_time": "2026-06-01T10:00:00Z",
    }
    response = await client.post(
        "/api/v1/reminders/", json=payload, headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["reminder_type"] == "MEDICAL_VISIT"
    assert data["status"] == "SCHEDULED"


@pytest.mark.asyncio
async def test_list_reminders(client: AsyncClient, auth_headers: dict):
    """Test listing reminder jobs."""
    response = await client.get("/api/v1/reminders/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


@pytest.mark.asyncio
async def test_communication_logs(client: AsyncClient, auth_headers: dict):
    """Test getting communication logs."""
    response = await client.get("/api/v1/logs/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_generate_token(client: AsyncClient):
    """Test token generation endpoint."""
    response = await client.post("/auth/token?user_id=test&role=admin")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
