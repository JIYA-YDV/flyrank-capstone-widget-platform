# app/api/widgets.py
from uuid import UUID
from typing import List
from fastapi.responses import JSONResponse

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.widget import (
    WidgetCreate, WidgetUpdate, WidgetResponse,
    WidgetConfigResponse, SnippetResponse,
)
from app.services.widget_service import WidgetService

router = APIRouter(prefix="/api/widgets", tags=["widgets"])


@router.post("", response_model=WidgetResponse, status_code=status.HTTP_201_CREATED)
def create_widget(
    data: WidgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = WidgetService(db)
    widget = service.create_widget(owner_id=current_user.id, data=data)
    return widget


@router.get("", response_model=List[WidgetResponse])
def list_widgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = WidgetService(db)
    return service.get_widgets_for_owner(owner_id=current_user.id)


@router.get("/{widget_id}", response_model=WidgetResponse)
def get_widget(
    widget_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = WidgetService(db)
    widget = service.get_widget_by_id(widget_id, owner_id=current_user.id)
    if not widget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget not found")
    return widget


@router.put("/{widget_id}", response_model=WidgetResponse)
def update_widget(
    widget_id: UUID,
    data: WidgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = WidgetService(db)
    widget = service.update_widget(widget_id, owner_id=current_user.id, data=data)
    if not widget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget not found")
    return widget


@router.delete("/{widget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_widget(
    widget_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = WidgetService(db)
    deleted = service.delete_widget(widget_id, owner_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget not found")


@router.get("/{widget_id}/snippet", response_model=SnippetResponse)
def get_snippet(
    widget_id: UUID,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = WidgetService(db)
    widget = service.get_widget_by_id(widget_id, owner_id=current_user.id)
    if not widget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget not found")

    base_url = str(request.base_url).rstrip("/")
    snippet = service.generate_snippet(widget_id, base_url)
    return SnippetResponse(widget_id=widget_id, snippet=snippet)


@router.get("/{widget_id}/config", response_model=WidgetConfigResponse)
@router.get("/{widget_id}/config", response_model=WidgetConfigResponse)
def get_widget_config(
    widget_id: UUID,
    db: Session = Depends(get_db),
):
    """Public endpoint — no auth required. Serves widget config with short-lived cache headers."""
    service = WidgetService(db)
    widget = service.get_widget_public(widget_id)
    if not widget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Widget not found")

    config = WidgetConfigResponse.model_validate(widget)
    response = JSONResponse(
        content=config.model_dump(mode="json"),
        headers={
            "Cache-Control": "public, max-age=60, stale-while-revalidate=30",
            "X-Widget-Version": str(widget.version),
        },
    )
    return response