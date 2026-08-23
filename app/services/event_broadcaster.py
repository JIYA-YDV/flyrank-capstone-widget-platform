# app/services/event_broadcaster.py
"""
A simple in-process pub/sub broadcaster for Server-Sent Events.

Each connected dashboard client gets its own asyncio.Queue. When a new
submission is stored, we push it to every queue belonging to that tenant.

This is intentionally in-memory (single-process) — the same honest
limitation pattern as the in-memory rate limiter. Documented in README.
"""
import asyncio
import json
import logging
from typing import Dict, Set
from uuid import UUID

logger = logging.getLogger(__name__)


class EventBroadcaster:
    def __init__(self):
        # tenant_id -> set of subscriber queues
        self._subscribers: Dict[str, Set[asyncio.Queue]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, tenant_id: UUID) -> asyncio.Queue:
        """Register a new SSE client for this tenant. Returns their queue."""
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        key = str(tenant_id)
        async with self._lock:
            self._subscribers.setdefault(key, set()).add(queue)
        logger.info(f"SSE client subscribed for tenant {key}")
        return queue

    async def unsubscribe(self, tenant_id: UUID, queue: asyncio.Queue) -> None:
        """Remove a client when they disconnect."""
        key = str(tenant_id)
        async with self._lock:
            if key in self._subscribers:
                self._subscribers[key].discard(queue)
                if not self._subscribers[key]:
                    del self._subscribers[key]
        logger.info(f"SSE client unsubscribed for tenant {key}")

    async def publish(self, tenant_id: UUID, event_type: str, data: dict) -> None:
        """Push an event to every subscriber of this tenant. Never raises."""
        key = str(tenant_id)
        payload = {"event": event_type, "data": data}

        async with self._lock:
            queues = list(self._subscribers.get(key, set()))

        for queue in queues:
            try:
                queue.put_nowait(payload)
            except asyncio.QueueFull:
                logger.warning(f"SSE queue full for tenant {key}, dropping event")
            except Exception as e:
                # Safe side-effect pattern again: broadcasting must never
                # break the submission flow that triggered it.
                logger.error(f"Failed to publish SSE event: {e}")


# Singleton — shared across the whole app
event_broadcaster = EventBroadcaster()