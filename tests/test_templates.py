"""
Tests for Notification Templates API.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_template(client: AsyncClient, auth_headers: dict):
    """Test creating a notification template."""
    payload = {
        "template_name": "Test Template",
        "template_type": "REMINDER",
        "subject": "Test Subject",
        "message_body": "Hello {{name}}, this is a test.",
        "variables": ["name"],
    }
    response = await client.post(
        "/api/v1/templates/", json=payload, headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["template_name"] == "Test Template"
    assert data["template_type"] == "REMINDER"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_templates(client: AsyncClient, auth_headers: dict):
    """Test listing notification templates."""
    # Create a template first
    payload = {
        "template_name": "List Test Template",
        "template_type": "GENERAL",
        "subject": "Test",
        "message_body": "Test body",
    }
    await client.post("/api/v1/templates/", json=payload, headers=auth_headers)

    response = await client.get("/api/v1/templates/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_template(client: AsyncClient, auth_headers: dict):
    """Test getting a single template."""
    # Create first
    payload = {
        "template_name": "Get Test Template",
        "template_type": "ALERT",
        "subject": "Alert Subject",
        "message_body": "Alert body content",
    }
    create_resp = await client.post(
        "/api/v1/templates/", json=payload, headers=auth_headers
    )
    template_id = create_resp.json()["id"]

    response = await client.get(
        f"/api/v1/templates/{template_id}", headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["template_name"] == "Get Test Template"


@pytest.mark.asyncio
async def test_update_template(client: AsyncClient, auth_headers: dict):
    """Test updating a notification template."""
    # Create first
    payload = {
        "template_name": "Update Test Template",
        "template_type": "GENERAL",
        "subject": "Original Subject",
        "message_body": "Original body",
    }
    create_resp = await client.post(
        "/api/v1/templates/", json=payload, headers=auth_headers
    )
    template_id = create_resp.json()["id"]

    # Update
    update_payload = {"subject": "Updated Subject"}
    response = await client.put(
        f"/api/v1/templates/{template_id}", json=update_payload, headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["subject"] == "Updated Subject"


@pytest.mark.asyncio
async def test_delete_template(client: AsyncClient, auth_headers: dict):
    """Test deleting a notification template."""
    # Create first
    payload = {
        "template_name": "Delete Test Template",
        "template_type": "GENERAL",
        "subject": "Delete Subject",
        "message_body": "Delete body",
    }
    create_resp = await client.post(
        "/api/v1/templates/", json=payload, headers=auth_headers
    )
    template_id = create_resp.json()["id"]

    # Delete
    response = await client.delete(
        f"/api/v1/templates/{template_id}", headers=auth_headers
    )
    assert response.status_code == 204

    # Verify deleted
    get_resp = await client.get(
        f"/api/v1/templates/{template_id}", headers=auth_headers
    )
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_template_not_found(client: AsyncClient, auth_headers: dict):
    """Test getting a non-existent template."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(
        f"/api/v1/templates/{fake_id}", headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test accessing templates without authentication."""
    response = await client.get("/api/v1/templates/")
    assert response.status_code == 403
