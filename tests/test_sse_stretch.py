# tests/test_sse_stretch.py
"""Tests for the real-time dashboard stretch goal."""
import asyncio
import pytest
from app.services.event_broadcaster import EventBroadcaster
import uuid


@pytest.mark.asyncio
async def test_subscriber_receives_published_event():
    broadcaster = EventBroadcaster()
    tenant_id = uuid.uuid4()

    queue = await broadcaster.subscribe(tenant_id)
    await broadcaster.publish(tenant_id, "new_submission", {"name": "Test"})

    event = await asyncio.wait_for(queue.get(), timeout=1.0)
    assert event["event"] == "new_submission"
    assert event["data"]["name"] == "Test"


@pytest.mark.asyncio
async def test_unsubscribed_client_does_not_receive_events():
    broadcaster = EventBroadcaster()
    tenant_id = uuid.uuid4()

    queue = await broadcaster.subscribe(tenant_id)
    await broadcaster.unsubscribe(tenant_id, queue)
    await broadcaster.publish(tenant_id, "new_submission", {"name": "Ghost"})

    assert queue.empty()


@pytest.mark.asyncio
async def test_publish_to_no_subscribers_does_not_raise():
    """Publishing with zero subscribers must never throw."""
    broadcaster = EventBroadcaster()
    tenant_id = uuid.uuid4()

    # No subscribe() call — no one is listening
    await broadcaster.publish(tenant_id, "new_submission", {"name": "NoOne"})
    # If we reach this line without an exception, the test passes
    assert True


def test_stream_endpoint_requires_token(client):
    response = client.get("/api/dashboard/stream")
    assert response.status_code == 401