"""Утилиты безопасности: функции для криптографического хэширования паролей и безопасной верификации данных"""
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

from fastapi import Security, HTTPException, status, Depends
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
import bcrypt

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import get_db
from app.models import User

settings = get_settings()

def get_password_hash(password: str) -> str:
    """Берет сырой пароль и хеширует его"""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Сверяет сырой пароль с хешированным"""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        return False

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
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось подтвердить учетные данные",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credential_exception
    except JWTError:
        raise credential_exception
    
    query = select(User).where(User.email==email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if user is None:
        raise credential_exception
    return user 
