"""Сервисный слой для управления виртуально машиной: реализациия проверки ключа активации и назначения пользователя на виртуальную машину"""
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import HTTPException, status

from app.models import VirtualMachine, User
from app.schemas import VirtualMachineUpdate

class VirtualMachineService():
    def __init__(self, db: AsyncSession):
        self.db = db

    async def activate_key(self, key: str):
        """Проверяет ключ и возвращает ID пользователя"""
        query = select(User).where(User.activation_key == key)
        result = await self.db.execute(query)

        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Такого ключа не существует"
            )
        if user.activation_key_expires and user.activation_key_expires < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Срок действия ключа активации истёк"
            )
        return user.id
    
    async def get_free_vm(self, user_id: int):
        """Находит свободную виртуалку и привязывает к ней юзера"""
        query = select(VirtualMachine).where(
            VirtualMachine.current_user_id == None,
            VirtualMachine.is_active == True
        ).limit(1)

        result = await self.db.execute(query)
        vm = result.scalar_one_or_none()


        if not vm:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Все виртуальные машины заняты"
            )
        
        vm.current_user_id = user_id
        vm.last_used_at = datetime.now()

        await self.db.commit()
        await self.db.refresh(vm)

        return vm
        
        