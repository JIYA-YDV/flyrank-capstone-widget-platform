# app/schemas/widget.py
from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Any


VALID_WIDGET_TYPES = ["signup_form", "contact_form", "cta_popover"]


class FieldConfig(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    label: str = Field(..., min_length=1, max_length=200)
    field_type: str = Field(..., pattern="^(text|email|textarea|tel|number|select)$")
    required: bool = True
    placeholder: Optional[str] = None
    options: Optional[List[str]] = None  # for select fields


class WidgetCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    widget_type: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    fields_config: List[FieldConfig] = Field(..., min_length=1, max_length=20)
    button_text: str = Field(default="Submit", max_length=100)
    display_options: Optional[dict] = None
    allowed_origins: Optional[List[str]] = None

    @field_validator("widget_type")
    @classmethod
    def validate_widget_type(cls, v: str) -> str:
        if v not in VALID_WIDGET_TYPES:
            raise ValueError(f"widget_type must be one of: {VALID_WIDGET_TYPES}")
        return v


class WidgetUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    fields_config: Optional[List[FieldConfig]] = None
    button_text: Optional[str] = Field(None, max_length=100)
    display_options: Optional[dict] = None
    is_active: Optional[str] = None
    allowed_origins: Optional[List[str]] = None

    @field_validator("is_active")
    @classmethod
    def validate_is_active(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("active", "inactive"):
            raise ValueError("is_active must be 'active' or 'inactive'")
        return v


class WidgetResponse(BaseModel):
    id: UUID
    owner_id: UUID
    name: str
    widget_type: str
    title: str
    description: Optional[str]
    fields_config: Any
    button_text: str
    display_options: Optional[Any]
    version: int
    is_active: str
    allowed_origins: Optional[Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WidgetConfigResponse(BaseModel):
    """Public config response — no sensitive data."""
    id: UUID
    widget_type: str
    title: str
    description: Optional[str]
    fields_config: Any
    button_text: str
    display_options: Optional[Any]
    version: int

    class Config:
        from_attributes = True


class SnippetResponse(BaseModel):
    widget_id: UUID
    snippet: str