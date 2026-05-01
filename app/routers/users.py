"""Роутеры для управления пользователями: получение, обновление и удаление профилей"""
from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.services import UserService
from app.schemas import UserRead, UserUpdate
from app.core.database import get_db
from app.core import security
from app.models import User

router = APIRouter(prefix="/api", tags=["users"])

@router.get("/me", response_model=UserRead)
async def get_my_profile(
    current_user: User = Depends(security.get_current_user)
):
    """получить профиль текущего авторизированного пользователя"""

    return current_user

@router.put("/me", response_model=UserRead)
async def update_my_profile(
    user_data: UserUpdate,
    current_user: User = Depends(security.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновить данные профиля"""
    users_service = UserService(db)

    updated_user = await users_service.update_user(current_user.id, user_data)
    
    return updated_user

@router.post("/me/update-key", response_model=UserRead)
async def update_my_key(
    current_user: User = Depends(security.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Сгенерировать новый ключ активации и отправить на почту (для личного кабинета)"""
    users_service = UserService(db)
    updated_user = await users_service.update_activation_key(current_user)
    return updated_user
