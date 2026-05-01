"""Роутеры для панели администратора: управление пользователями и виртуальными машинами"""
from fastapi import APIRouter, HTTPException, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.services import UserService, VirtualMachineService
from app.schemas import UserRead, UserUpdate, VirtualMachineRead, VirtualMachineUpdate, VirtualMachineCreate
from app.core.database import get_db
from app.core import security

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(security.verify_admin_key)])

@router.get("/get_users", response_model=list[UserRead])
async def get_users(
    db: AsyncSession = Depends(get_db)
):
    """Получить список всех пользователей системы"""
    users_service = UserService(db)

    users = await users_service.get_all_users()

    return users

@router.get("/get_user/{user_id}", response_model=UserRead)
async def get_users_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить данные конкретного пользователя по его ID"""
    users_service = UserService(db)

    user = await users_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    return user

@router.put("/update_user/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить данные пользователя (email, пароль) по его ID"""
    users_service = UserService(db)

    updated_user = await users_service.update_user(user_id, user_data)

    return updated_user

@router.delete("/delete_user/{user_id}", response_model=UserRead)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удалить пользователя из базы данных по его ID"""
    users_service = UserService(db)
    deleted_user = await users_service.delete_user(user_id)
    return deleted_user

@router.post("/create_vm", response_model=VirtualMachineRead)
async def create_vm(
    vm_data: VirtualMachineCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создать новую виртуальную машину (прокси-сервер) в базе данных"""
    vm_service = VirtualMachineService(db)

    new_vm = await vm_service.vm_create(vm_data)

    return new_vm

@router.put("/update_vm/{vm_id}", response_model=VirtualMachineRead)
async def update_vm(
    vm_id: int,
    vm_data: VirtualMachineUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Обновить настройки существующей виртуальной машины по её ID"""
    vm_service = VirtualMachineService(db)

    updated_vm = await vm_service.vm_update(vm_id, vm_data)

    return updated_vm

@router.delete("/delete_vm/{vm_id}", response_model=VirtualMachineRead)
async def delete_vm(
    vm_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Удалить виртуальную машину из базы данных по её ID"""
    vm_service = VirtualMachineService(db)

    deleted_vm = await vm_service.delete_vm(vm_id)

    return deleted_vm

@router.get("/get_vms", response_model=list[VirtualMachineRead])
async def get_vm(
    db: AsyncSession = Depends(get_db)
):
    """Получить список всех виртуальных машин"""
    vm_service = VirtualMachineService(db)

    vms = await vm_service.get_all_vm()

    return vms

@router.get("/get_vm/{vm_id}", response_model=VirtualMachineRead)
async def get_vm_by_id(
    vm_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Получить данные конкретной виртуальной машины по её ID"""
    vm_service = VirtualMachineService(db)

    vm = await vm_service.get_vm_by_id(vm_id)
    
    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Виртуальная машина не найдена"
        )
    
    return vm
