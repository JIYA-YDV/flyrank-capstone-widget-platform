# app/schemas/submission.py
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional, Any, Dict


MAX_PAYLOAD_SIZE = 10_000  # characters


class SubmissionCreate(BaseModel):
    widget_id: UUID
    data: Dict[str, Any] = Field(...)
    honeypot: Optional[str] = Field(default="", alias="_hp_field")
    idempotency_key: Optional[str] = Field(None, max_length=255)

    @field_validator("data")
    @classmethod
    def validate_data_size(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        import json
        serialized = json.dumps(v)
        if len(serialized) > MAX_PAYLOAD_SIZE:
            raise ValueError(f"Payload too large. Maximum {MAX_PAYLOAD_SIZE} characters.")
        return v


class SubmissionResponse(BaseModel):
    id: UUID
    widget_id: UUID
    data: Any
    country: Optional[str]
    city: Optional[str]
    region: Optional[str]
    geo_provider: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class SubmissionListResponse(BaseModel):
    submissions: list[SubmissionResponse]
    total: int
    page: int
    page_size: int


class DashboardStats(BaseModel):
    total_submissions: int
    submissions_today: int
    submissions_this_week: int
    submissions_this_month: int
    by_widget: list[dict]
    by_country: list[dict]
    recent: list[SubmissionResponse]