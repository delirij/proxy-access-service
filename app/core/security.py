"""Утилиты безопасности: функции для криптографического хэширования паролей и безопасной верификации данных"""
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from passlib.context import CryptContext

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core import get_settings, get_db
from app.models import User

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Берет сырой пароль и хеширует его"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Сверяет сырой пароль с хешированным"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Создает  JWT токен доступа"""
    to_encode = data.copy()

    # Определяем время жизни токена
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})

    encode_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encode_jwt


admin_api_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=True)

def verify_admin_key(api_key: str = Security(admin_api_key_header)) -> str:
    """Проверяет статический ключ администратора из заголовка X-Admin-Key"""
    if api_key != settings.ADMIN_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неверный ключ администратора"
        )
    return api_key

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> User:
    """Расшифровыывает токен и возвращает модель текущего авторизованного пользователя"""
    pass
    
