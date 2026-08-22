# tests/test_submissions.py
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.geo_service import GeoResult


def test_valid_submission(client, sample_widget):
    """POST a valid submission → stored, 201."""
    widget_id = sample_widget["id"]
    response = client.post(
        "/api/submissions",
        json={
            "widget_id": widget_id,
            "data": {
                "name": "John Doe",
                "email": "john@example.com",
                "message": "Hello!",
            },
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["widget_id"] == widget_id
    assert data["data"]["name"] == "John Doe"


def test_cors_preflight(client, sample_widget):
    """OPTIONS request should return CORS headers."""
    response = client.options(
        "/api/submissions",
        headers={
            "Origin": "http://localhost:5500",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers


def test_invalid_json_payload(client):
    """Malformed JSON → 400."""
    response = client.post(
        "/api/submissions",
        content="not valid json{{{",
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400


def test_missing_required_field(client, sample_widget):
    """Missing required field → 400."""
    widget_id = sample_widget["id"]
    response = client.post(
        "/api/submissions",
        json={
            "widget_id": widget_id,
            "data": {
                "message": "No name or email provided",
            },
        },
    )
    assert response.status_code == 400
    assert "required field" in response.json()["detail"].lower() or "Missing" in response.json()["detail"]


def test_oversized_payload(client, sample_widget):
    """Oversized payload → 413."""
    widget_id = sample_widget["id"]
    huge_data = {"name": "x" * 60000}
    response = client.post(
        "/api/submissions",
        json={
            "widget_id": widget_id,
            "data": huge_data,
        },
    )
    # Should be rejected — either 413 or 400 due to validation
    assert response.status_code in (400, 413, 422)


def test_honeypot_spam_rejection(client, sample_widget):
    """Filled honeypot field → submission rejected (spam)."""
    widget_id = sample_widget["id"]
    response = client.post(
        "/api/submissions",
        json={
            "widget_id": widget_id,
            "data": {
                "name": "Bot User",
                "email": "bot@spam.com",
            },
            "_hp_field": "I am a bot filling hidden fields",
        },
    )
    # Honeypot filled = rejected
    assert response.status_code == 400


def test_nonexistent_widget_submission(client):
    """Submission to non-existent widget → 404."""
    response = client.post(
        "/api/submissions",
        json={
            "widget_id": "00000000-0000-0000-0000-000000000000",
            "data": {"name": "Test"},
        },
    )
    assert response.status_code == 404


def test_submission_with_idempotency(client, sample_widget):
    """Same idempotency key → same submission returned, no duplicate."""
    widget_id = sample_widget["id"]
    payload = {
        "widget_id": widget_id,
        "data": {"name": "Idempotent User", "email": "idem@example.com"},
        "idempotency_key": "unique-key-123",
    }

    response1 = client.post("/api/submissions", json=payload)
    assert response1.status_code == 201

    response2 = client.post("/api/submissions", json=payload)
    assert response2.status_code == 200 or response2.status_code == 201
    assert response1.json()["id"] == response2.json()["id"]