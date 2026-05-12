"""
Tests for Notification APIs (Email, SMS, WhatsApp).
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_send_email(client: AsyncClient, auth_headers: dict):
    """Test sending an email notification."""
    payload = {
        "recipient_email": "test@example.com",
        "recipient_name": "Test User",
        "subject": "Test Email",
        "body_html": "<h1>Hello</h1><p>This is a test email.</p>",
        "is_html": True,
    }
    response = await client.post(
        "/api/v1/email/send", json=payload, headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["recipient_email"] == "test@example.com"
    assert data["status"] in ["SENT", "FAILED", "QUEUED"]


@pytest.mark.asyncio
async def test_email_history(client: AsyncClient, auth_headers: dict):
    """Test getting email notification history."""
    response = await client.get("/api/v1/email/history", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_send_sms(client: AsyncClient, auth_headers: dict):
    """Test sending an SMS notification."""
    payload = {
        "recipient_phone": "+919876543210",
        "recipient_name": "Test User",
        "message_body": "This is a test SMS message.",
    }
    response = await client.post(
        "/api/v1/sms/send", json=payload, headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["recipient_phone"] == "+919876543210"
    assert data["status"] in ["SENT", "FAILED", "QUEUED"]


@pytest.mark.asyncio
async def test_sms_history(client: AsyncClient, auth_headers: dict):
    """Test getting SMS notification history."""
    response = await client.get("/api/v1/sms/history", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data


@pytest.mark.asyncio
async def test_send_whatsapp(client: AsyncClient, auth_headers: dict):
    """Test sending a WhatsApp notification."""
    payload = {
        "recipient_phone": "+919876543210",
        "recipient_name": "Test User",
        "message_body": "This is a test WhatsApp message.",
    }
    response = await client.post(
        "/api/v1/whatsapp/send", json=payload, headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["recipient_phone"] == "+919876543210"
    assert data["status"] in ["SENT", "FAILED", "QUEUED"]


@pytest.mark.asyncio
async def test_whatsapp_history(client: AsyncClient, auth_headers: dict):
    """Test getting WhatsApp notification history."""
    response = await client.get("/api/v1/whatsapp/history", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_email_validation_error(client: AsyncClient, auth_headers: dict):
    """Test email validation with missing required fields."""
    payload = {
        "recipient_email": "test@example.com",
        # Missing subject and body_html
    }
    response = await client.post(
        "/api/v1/email/send", json=payload, headers=auth_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_sms_validation_error(client: AsyncClient, auth_headers: dict):
    """Test SMS validation with invalid phone number."""
    payload = {
        "recipient_phone": "123",  # Too short
        "message_body": "Test",
    }
    response = await client.post(
        "/api/v1/sms/send", json=payload, headers=auth_headers
    )
    assert response.status_code == 422
