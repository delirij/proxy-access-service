"""Роутеры для управления пользователями: получение, обновление и удаление профилей"""
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.services import UserService
from app.schemas import UserRead, UserUpdate
from app.core import get_db

router = APIRouter(prefix="/api", tags=["users"])

