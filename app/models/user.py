"""Модель данных пользователя для SQLAlchemy"""
from datetime import datetime

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core import Base

class User(Base):
    """Модель пользователя системы"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    email: Mapped[str] = mapped_column(String(255), unique=True)

    password: Mapped[str] = mapped_column(String(255))

    is_active: Mapped[bool] = mapped_column(default=True)

    activation_key: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)

    activation_key_expires: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
