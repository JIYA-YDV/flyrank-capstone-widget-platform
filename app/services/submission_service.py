# app/services/submission_service.py
import logging
from uuid import UUID
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.submission import Submission
from app.models.widget import Widget
from app.models.user import User
from app.services.geo_service import GeoResult
from app.services.notification_service import notification_service

logger = logging.getLogger(__name__)


class SubmissionService:
    def __init__(self, db: Session):
        self.db = db

    def check_idempotency(self, idempotency_key: str) -> Optional[Submission]:
        """Return existing submission if this key was already used."""
        if not idempotency_key:
            return None
        return (
            self.db.query(Submission)
            .filter(Submission.idempotency_key == idempotency_key)
            .first()
        )

    def create_submission(
        self,
        widget: Widget,
        data: Dict[str, Any],
        ip_address: str,
        user_agent: Optional[str],
        referrer: Optional[str],
        geo: GeoResult,
        idempotency_key: Optional[str] = None,
    ) -> Submission:
        submission = Submission(
            widget_id=widget.id,
            tenant_id=widget.owner_id,
            data=data,
            ip_address=ip_address,
            country=geo.country,
            city=geo.city,
            region=geo.region,
            latitude=geo.latitude,
            longitude=geo.longitude,
            geo_provider=geo.provider,
            user_agent=user_agent,
            referrer=referrer,
            idempotency_key=idempotency_key,
        )
        self.db.add(submission)
        self.db.commit()
        self.db.refresh(submission)

        # Safe side effect: send notification email
        self._send_notification_safe(widget, data)

        return submission

    def _send_notification_safe(self, widget: Widget, data: Dict[str, Any]) -> None:
        """Fire-and-forget notification. Failure is logged, never raised."""
        try:
            owner = self.db.query(User).filter(User.id == widget.owner_id).first()
            if owner:
                success = notification_service.send_submission_notification(
                    owner_email=owner.email,
                    widget_name=widget.name,
                    submission_data=data,
                )
                # We could update the submission's email_sent field here
                # but it's not critical
        except Exception as e:
            logger.error(f"Notification side effect error: {e}")

    def get_submissions_for_owner(
        self,
        owner_id: UUID,
        widget_id: Optional[UUID] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[List[Submission], int]:
        query = self.db.query(Submission).filter(Submission.tenant_id == owner_id)

        if widget_id:
            query = query.filter(Submission.widget_id == widget_id)

        query = query.filter(Submission.is_spam == "no")
        total = query.count()
        submissions = (
            query.order_by(Submission.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
        return submissions, total

    def get_stats_for_owner(self, owner_id: UUID) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)

        base_query = self.db.query(Submission).filter(
            Submission.tenant_id == owner_id,
            Submission.is_spam == "no",
        )

        total = base_query.count()
        today = base_query.filter(Submission.created_at >= today_start).count()
        this_week = base_query.filter(Submission.created_at >= week_start).count()
        this_month = base_query.filter(Submission.created_at >= month_start).count()

        # Per widget
        by_widget_rows = (
            self.db.query(
                Widget.name,
                Widget.id,
                func.count(Submission.id).label("count"),
            )
            .join(Widget, Submission.widget_id == Widget.id)
            .filter(Submission.tenant_id == owner_id, Submission.is_spam == "no")
            .group_by(Widget.id, Widget.name)
            .all()
        )
        by_widget = [
            {"widget_id": str(row[1]), "widget_name": row[0], "count": row[2]}
            for row in by_widget_rows
        ]

        # Per country
        by_country_rows = (
            base_query
            .with_entities(Submission.country, func.count(Submission.id).label("count"))
            .filter(Submission.country.isnot(None))
            .group_by(Submission.country)
            .order_by(func.count(Submission.id).desc())
            .limit(20)
            .all()
        )
        by_country = [{"country": row[0], "count": row[1]} for row in by_country_rows]

        # Recent
        recent_subs = (
            base_query.order_by(Submission.created_at.desc()).limit(10).all()
        )

        return {
            "total_submissions": total,
            "submissions_today": today,
            "submissions_this_week": this_week,
            "submissions_this_month": this_month,
            "by_widget": by_widget,
            "by_country": by_country,
            "recent": recent_subs,
        }