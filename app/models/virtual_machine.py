"""Модель данных виртуальной машины (прокси)"""
from datetime import datetime

from sqlalchemy import String, DateTime, func, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core import Base


class VirtualMachine(Base):
    """Модель виртуальной машины (прокси-сервера)"""
    __tablename__ = 'virtual_machines'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(255), unique=True)

    host: Mapped[str] = mapped_column(String(255))

    port: Mapped[int] = mapped_column(Integer)

    protocol: Mapped[str] = mapped_column(String(50))

    is_active: Mapped[bool] = mapped_column(default=True)

    current_user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)