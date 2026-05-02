"""Сервисный слой для управления пользователями: реализация CRUD-операций в базе данных"""
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import HTTPException, status

from app.models import User
from app.schemas import UserUpdate
from app.core.security import get_password_hash
from app.tasks.email_tasks import send_message

class UserService:
    """Сервис для бизнес-логики пользователей"""
    def __init__(self, db: AsyncSession):
        """Инициализация сервиса с сессией базы данных"""
        self.db = db
    
    async def get_all_users(self):
        """Получить всех пользователей"""
        query = select(User).order_by(User.id)
        result = await self.db.execute(query)

        return result.scalars().all()
    
    async def get_user_by_id(self, user_id: int):
        """Получить пользователя по id"""
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)

        return result.scalar_one_or_none()
    
    async def update_user(self, user_id: int, user_data: UserUpdate):
        """Обновить данные пользователя"""
        user = await self.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        update_dict = user_data.model_dump(exclude_unset=True)

        for key, value in update_dict.items():
            if key == "password":
                setattr(user, key, get_password_hash(value))
            else:
                setattr(user, key, value)
        
        await self.db.commit()
        await self.db.refresh(user)

        return user
    
    async def update_activation_key(self, user: User):
        """Сгенерировать новый ключ активации и отправить на почту"""
        new_key = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
        
        user.activation_key = new_key
        user.activation_key_expires = expires_at
        
        await self.db.commit()
        await self.db.refresh(user)
        
        send_message.delay(user.email, new_key)
        return user

    async def delete_user(self, user_id: int):
        """Удалить пользователя"""
        user = await self.get_user_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        await self.db.delete(user)
        await self.db.commit()

        return True
