"""Экспорт Pydantic-схем валидации для удобного импорта"""
from app.schemas.user import UserCreate, UserRead, UserUpdate, TokenResponse
from app.schemas.virtual_machine import VirtualMachineCreate, VirtualMachineRead, VirtualMachineUpdate

__all__ = (
    "UserCreate", "UserRead", "UserUpdate", "TokenResponse",
    "VirtualMachineCreate", "VirtualMachineRead", "VirtualMachineUpdate"
)