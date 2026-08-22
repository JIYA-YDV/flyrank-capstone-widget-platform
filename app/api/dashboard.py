# app/api/dashboard.py
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