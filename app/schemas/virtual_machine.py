"""Pydantic-схемы для виртуальных машин (прокси): структура данных для выдачи свободных серверов и проверки их статуса"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class VirtualMachineCreate(BaseModel):
    """Схема для создания виртуальной машины"""
    name: str = Field(..., min_length=5, max_length=255)
    host: str = Field(..., min_length=3)
    port: int = Field(..., ge=1, le=65535)
    protocol: str = Field(..., pattern="^(socks5|http|https)$")

class VirtualMachineRead(BaseModel):
    """Схема получения данных виртуальной машины"""
    id: int
    name: str
    host: str
    port: int
    protocol: str
    is_active: bool
    current_user_id: int | None
    last_used_at: datetime | None

    model_config = ConfigDict(from_attributes=True)

class VirtualMachineUpdate(BaseModel):
    """Схема обновления данных виртуальной машины"""
    name: str | None = None
    host: str | None = None
    port: int | None = None
    protocol: str | None = None
    
    model_config = ConfigDict(from_attributes=True)