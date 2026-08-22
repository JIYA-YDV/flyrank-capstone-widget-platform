# app/api/submissions.py
import json
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.submission import SubmissionCreate, SubmissionResponse
from app.services.widget_service import WidgetService
from app.services.submission_service import SubmissionService
from app.services.geo_service import geo_service
from app.middleware.rate_limiter import limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/submissions", tags=["submissions"])

MAX_CONTENT_LENGTH = 50_000  # 50KB max request body


@router.post("", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_submission(request: Request, db: Session = Depends(get_db)):
    # 1. Check content length
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_CONTENT_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Payload too large",
        )

    # 2. Parse body
    try:
        body = await request.body()
        if len(body) > MAX_CONTENT_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Payload too large",
            )
        raw_data = json.loads(body)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON",
        )

    # 3. Validate with Pydantic
    try:
        submission_data = SubmissionCreate(**raw_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}",
        )

    # 4. Honeypot spam check — if the hidden field is filled, it's a bot
    honeypot_value = raw_data.get("_hp_field", "")
    if honeypot_value:
        # Silently accept but don't store (or reject) — we'll return 201 to not tip off the bot
        logger.info(f"Honeypot triggered, dropping spam submission for widget {submission_data.widget_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Submission rejected",
        )

    # 5. Check widget exists and is active
    widget_service = WidgetService(db)
    widget = widget_service.get_widget_public(submission_data.widget_id)
    if not widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found or inactive",
        )

    # 6. Validate submitted data against widget's field config
    required_fields = [
        f["name"] for f in widget.fields_config if f.get("required", True)
    ]
    for field_name in required_fields:
        if field_name not in submission_data.data or not submission_data.data[field_name]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field_name}",
            )

    # 7. Idempotency check
    submission_service = SubmissionService(db)
    if submission_data.idempotency_key:
        existing = submission_service.check_idempotency(submission_data.idempotency_key)
        if existing:
            return existing

    # 8. Geo enrichment (with fallback chain — never fails)
    client_ip = request.client.host if request.client else "unknown"
    geo_result = await geo_service.enrich(client_ip)

    # 9. Store submission
    submission = submission_service.create_submission(
        widget=widget,
        data=submission_data.data,
        ip_address=client_ip,
        user_agent=request.headers.get("user-agent"),
        referrer=request.headers.get("referer"),
        geo=geo_result,
        idempotency_key=submission_data.idempotency_key,
    )

    return submission