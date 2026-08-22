# app/models/__init__.py
from app.models.user import User
from app.models.widget import Widget
from app.models.submission import Submission

__all__ = ["User", "Widget", "Submission"]