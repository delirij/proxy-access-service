"""Сервисный слой для аутентификации: логика регистрации пользователей, генерации ключей активации и проверки учетных данных"""
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.models import User
from app.schemas import UserCreate
from app.core import get_password_hash, verify_password, create_access_token
from app.tasks.email_tasks import send_message

class AuthService():
    """Сервис для регистрации пользователя и логина"""
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, user_data: UserCreate):
        """Функция регистрации пользователя"""

        # Проверка, существует ли пользователь с таким email
        query = select(User).where(User.email == user_data.email)
        result = await self.db.execute(query)
        existing_user = result.scalar_one_or_none()

        # Если существует, вызываем ошибку с кодом 400
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )
        
        # Хеширование пароля
        hashed_password = get_password_hash(user_data.password)

        #Генерация ключа активации (который будет отправлен на почту), время жизни ключа 30 минут (потом придется запрашивать новый)
        activation_key = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)

        # Собираем данные нового пользователя
        new_user = User(
            email=user_data.email,
            password=hashed_password,
            activation_key=activation_key,
            activation_key_expires=expires_at,
            is_active=True
        )

        # Добавляем, коммитим и обновляем бд
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        # Отправляем сообщение с ключем активации на почту пользователю
        send_message.delay(new_user.email, activation_key)

        return new_user
    
    async def login_user(self, user_data: UserCreate):
        """Функция входа пользователя"""

        query = select(User).where(User.email == user_data.email)
        result = await self.db.execute(query)
        existing_user = result.scalar_one_or_none()

        if not existing_user or not verify_password(user_data.password, existing_user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль"
            )
        
        access_token = create_access_token(data={"sub": existing_user.email})

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

            
