"""Сервисный слой для управления пользователями: реализация CRUD-операций в базе данных"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import HTTPException, status

from app.models import User
from app.schemas import UserUpdate

class UserService():
    """Сервис для бизнес-логики пользователей"""
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_all_users(self):
        """Получить всех пользователей"""
        query = select(User).order_by(User.id)
        result = await self.db.execute(query)

        return result.scalars().all()
    
    async def get_user_by_id(self, id: int):
        """Получить пользователя по id"""
        query = select(User).where(User.id == id)
        result = await self.db.execute(query)

        return result.scalar_one_or_none()
    
    async def update_user(self, id: int, user_data: UserUpdate):
        """Обновить данные пользователя"""
        user = await self.get_user_by_id(id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        update_dict = user_data.model_dump(exclude_unset=True)

        for key, value in update_dict.items():
            setattr(user, key, value)
        
        await self.db.commit()
        await self.db.refresh(user)

        return user
    
    async def delete_user(self, id: int):
        """Удалить пользователя"""
        user = await self.get_user_by_id(id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        await self.db.delete(user)
        await self.db.commit()

        return True
