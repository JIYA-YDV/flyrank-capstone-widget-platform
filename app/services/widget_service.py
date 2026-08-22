# app/services/widget_service.py
from uuid import UUID
from typing import Optional, List

from sqlalchemy.orm import Session

from app.models.widget import Widget
from app.schemas.widget import WidgetCreate, WidgetUpdate


class WidgetService:
    def __init__(self, db: Session):
        self.db = db

    def create_widget(self, owner_id: UUID, data: WidgetCreate) -> Widget:
        widget = Widget(
            owner_id=owner_id,
            name=data.name,
            widget_type=data.widget_type,
            title=data.title,
            description=data.description,
            fields_config=[f.model_dump() for f in data.fields_config],
            button_text=data.button_text,
            display_options=data.display_options or {},
            allowed_origins=data.allowed_origins or [],
        )
        self.db.add(widget)
        self.db.commit()
        self.db.refresh(widget)
        return widget

    def get_widgets_for_owner(self, owner_id: UUID) -> List[Widget]:
        return self.db.query(Widget).filter(Widget.owner_id == owner_id).all()

    def get_widget_by_id(self, widget_id: UUID, owner_id: UUID) -> Optional[Widget]:
        return (
            self.db.query(Widget)
            .filter(Widget.id == widget_id, Widget.owner_id == owner_id)
            .first()
        )

    def get_widget_public(self, widget_id: UUID) -> Optional[Widget]:
        """Public access — no owner check, but only active widgets."""
        return (
            self.db.query(Widget)
            .filter(Widget.id == widget_id, Widget.is_active == "active")
            .first()
        )

    def update_widget(self, widget_id: UUID, owner_id: UUID, data: WidgetUpdate) -> Optional[Widget]:
        widget = self.get_widget_by_id(widget_id, owner_id)
        if not widget:
            return None

        update_data = data.model_dump(exclude_unset=True)

        if "fields_config" in update_data and update_data["fields_config"] is not None:
            update_data["fields_config"] = [f.model_dump() if hasattr(f, "model_dump") else f for f in update_data["fields_config"]]

        for key, value in update_data.items():
            setattr(widget, key, value)

        widget.version += 1
        self.db.commit()
        self.db.refresh(widget)
        return widget

    def delete_widget(self, widget_id: UUID, owner_id: UUID) -> bool:
        widget = self.get_widget_by_id(widget_id, owner_id)
        if not widget:
            return False
        self.db.delete(widget)
        self.db.commit()
        return True

    def generate_snippet(self, widget_id: UUID, base_url: str) -> str:
        return f'<script src="{base_url}/widget.js?id={widget_id}"></script>'