"""Роутеры для аутентификации: регистрация новых пользователей и авторизация (вход)"""
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from app.services import AuthService
from app.schemas import UserRead, UserCreate, TokenResponse
from app.core.database import get_db

router = APIRouter(prefix="/api", tags=["auth"])

@router.post("/register", response_model=UserRead)
async def registration_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Зарегистрировать нового пользователя и отправить ключ активации на почту"""

    auth_service = AuthService(db)

    new_user = await auth_service.register_user(user_data)

    return new_user

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Авторизовать пользователя по email и паролю, выдать JWT-токен доступа"""
    auth_service = AuthService(db)

    token_data = await auth_service.login_user(form_data.username, form_data.password)

    return token_data