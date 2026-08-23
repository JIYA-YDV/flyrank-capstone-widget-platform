# app/api/dashboard.py
import asyncio
import json
from fastapi import Request
from fastapi.responses import StreamingResponse
from app.services.event_broadcaster import event_broadcaster

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.submission import SubmissionListResponse, SubmissionResponse, DashboardStats
from app.services.submission_service import SubmissionService

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/submissions", response_model=SubmissionListResponse)
def list_submissions(
    widget_id: Optional[UUID] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = SubmissionService(db)
    submissions, total = service.get_submissions_for_owner(
        owner_id=current_user.id,
        widget_id=widget_id,
        page=page,
        page_size=page_size,
    )
    return SubmissionListResponse(
        submissions=[SubmissionResponse.model_validate(s) for s in submissions],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/stats", response_model=DashboardStats)
def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = SubmissionService(db)
    stats = service.get_stats_for_owner(owner_id=current_user.id)
    return DashboardStats(
        total_submissions=stats["total_submissions"],
        submissions_today=stats["submissions_today"],
        submissions_this_week=stats["submissions_this_week"],
        submissions_this_month=stats["submissions_this_month"],
        by_widget=stats["by_widget"],
        by_country=stats["by_country"],
        recent=[SubmissionResponse.model_validate(s) for s in stats["recent"]],
    )
    
@router.get("/stream")
async def dashboard_event_stream(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """
    Server-Sent Events stream. The dashboard UI opens this connection once
    and receives a push the instant a new submission arrives for this
    tenant — no polling required.

    STRETCH GOAL: Real-time dashboard.
    """
    queue = await event_broadcaster.subscribe(current_user.id)

    async def event_generator():
        try:
            # Initial "connected" event so the client knows the stream is live
            yield f"event: connected\ndata: {json.dumps({'status': 'connected'})}\n\n"

            while True:
                if await request.is_disconnected():
                    break
                try:
                    # Wait up to 15s for an event, otherwise send a heartbeat
                    payload = await asyncio.wait_for(queue.get(), timeout=15.0)
                    event_name = payload["event"]
                    data = json.dumps(payload["data"])
                    yield f"event: {event_name}\ndata: {data}\n\n"
                except asyncio.TimeoutError:
                    # Heartbeat keeps the connection alive through proxies
                    yield f"event: heartbeat\ndata: {json.dumps({'ts': None})}\n\n"
        finally:
            await event_broadcaster.unsubscribe(current_user.id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # disable buffering on nginx-style proxies
        },
    )