# app/api/dashboard.py
import asyncio
import json
from fastapi import Request
from fastapi.responses import StreamingResponse
from app.services.event_broadcaster import event_broadcaster
from fastapi import APIRouter, Depends, Query, HTTPException, Request
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.submission import SubmissionListResponse, SubmissionResponse, DashboardStats
from app.services.submission_service import SubmissionService

from fastapi import Query
from app.core.security import decode_access_token
from app.models.user import User as UserModel

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
    token: str = Query(None),
    db: Session = Depends(get_db),
):
    """
    SSE stream. EventSource cannot send Authorization headers, so this
    endpoint accepts the JWT as a query parameter — a documented, narrow
    exception for this one streaming endpoint only.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    payload = decode_access_token(token)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(status_code=401, detail="Invalid token")

    import uuid as uuid_module
    user = db.query(UserModel).filter(UserModel.id == uuid_module.UUID(user_id_str)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    queue = await event_broadcaster.subscribe(user.id)

    async def event_generator():
        try:
            yield f"event: connected\ndata: {json.dumps({'status': 'connected'})}\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"event: {payload['event']}\ndata: {json.dumps(payload['data'])}\n\n"
                except asyncio.TimeoutError:
                    yield f"event: heartbeat\ndata: {{}}\n\n"
        finally:
            await event_broadcaster.unsubscribe(user.id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )