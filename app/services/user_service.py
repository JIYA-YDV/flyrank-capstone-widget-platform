# app/services/user_service.py
from uuid import UUID
from typing import Optional

from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import hash_password, verify_password


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, email: str, password: str, company_name: Optional[str] = None) -> User:
        existing = self.db.query(User).filter(User.email == email).first()
        if existing:
            raise ValueError("Email already registered")

        user = User(
            email=email,
            hashed_password=hash_password(password),
            company_name=company_name,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> Optional[User]:
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()