"""Экспорт всех моделей SQLAlchemy для удобного импорта в других частях проекта и Alembic"""
from .user import User
from .virtual_machine import VirtualMachine

__all__ = ["User", "VirtualMachine"]