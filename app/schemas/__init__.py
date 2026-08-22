# app/schemas/__init__.py
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.schemas.widget import (
    WidgetCreate, WidgetUpdate, WidgetResponse,
    WidgetConfigResponse, SnippetResponse,
)
from app.schemas.submission import (
    SubmissionCreate, SubmissionResponse,
    SubmissionListResponse, DashboardStats,
)