from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """Схема для регистрации пользователя"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Минимум 8 символов")

class UserRead(BaseModel):
    """Схема для чтения данных пользователя"""
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    email: EmailStr | None = None

    model_config = ConfigDict(from_attributes=True)

