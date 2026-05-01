"""Сервисный слой для управления виртуально машиной: реализациия проверки ключа активации и назначения пользователя на виртуальную машину"""
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fastapi import HTTPException, status

from app.models import VirtualMachine, User
from app.schemas import VirtualMachineUpdate, VirtualMachineCreate

class VirtualMachineService:
    def __init__(self, db: AsyncSession):
        """Инициализация сервиса с сессией базы данных"""
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
        if user.activation_key_expires and user.activation_key_expires < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Срок действия ключа активации истёк"
            )
        user.activation_key = None
        user.activation_key_expires = None

        await self.db.commit()

        return user.id
    
    async def get_free_vm(self, user_id: int):
        """Находит свободную виртуалку и привязывает к ней юзера"""
        query = select(VirtualMachine).where(
            VirtualMachine.current_user_id.is_(None),
            VirtualMachine.is_active.is_(True)
        ).limit(1)

        result = await self.db.execute(query)
        vm = result.scalar_one_or_none()


        if not vm:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Все виртуальные машины заняты"
            )
        
        vm.current_user_id = user_id
        vm.last_used_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(vm)

        return vm
    
    async def get_all_vm(self):
        """Получить список всех виртуальных машин в базе"""
        query = select(VirtualMachine).order_by(VirtualMachine.id)
        result = await self.db.execute(query)

        return result.scalars().all()
    
    async def get_vm_by_id(self, id: int):
        """Получить данные виртуальной машины по её ID"""
        query = select(VirtualMachine).where(VirtualMachine.id == id)
        result = await self.db.execute(query)

        return result.scalar_one_or_none()
        
    async def vm_create(self, vm_data: VirtualMachineCreate):
        """Функция создания виртуальной машины"""
        query = select(VirtualMachine).where(VirtualMachine.name == vm_data.name)
        result = await self.db.execute(query)
        existing_vm = result.scalar_one_or_none()

        if existing_vm:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Виртуальная машина с таким именем уже существует"
            )
        
        new_vm = VirtualMachine(
            name = vm_data.name,
            host = vm_data.host,
            port = vm_data.port,
            protocol = vm_data.protocol,
            is_active = True,
            current_user_id = None,
        )

        self.db.add(new_vm)
        await self.db.commit()
        await self.db.refresh(new_vm)
        
        return new_vm

    async def vm_update(self, id: int, vm_data: VirtualMachineUpdate):
        """Обновить настройки существующей виртуальной машины"""
        vm = await self.get_vm_by_id(id)

        if not vm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Виртуальная машина не найдена"
            )
        
        update_dict = vm_data.model_dump(exclude_unset=True, exclude_none=True)

        for key, value in update_dict.items():
            setattr(vm, key, value)
        
        await self.db.commit()
        await self.db.refresh(vm)

        return vm
    
    async def delete_vm(self, id: int):
        """Удалить виртуальную машину из базы данных"""
        vm = await self.get_vm_by_id(id)

        if not vm:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Виртуальная машина не найдена"
            )
        await self.db.delete(vm)
        await self.db.commit()

        return vm