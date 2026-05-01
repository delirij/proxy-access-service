"""Роутеры для работы с виртуальными машинами (прокси): активация ключей и выдача серверов"""
from fastapi import APIRouter, Depends, Body

from sqlalchemy.ext.asyncio import AsyncSession

from app.services import VirtualMachineService
from app.schemas import  VirtualMachineRead
from app.core.database import get_db

router = APIRouter(prefix="/api", tags=["vm"])

@router.post("/activate-key", response_model=VirtualMachineRead)
async def activate_and_get_proxy(
    activate_key: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
):
    """Активировать ключ из письма и получить настройки свободного прокси-сервера"""
    vm_service = VirtualMachineService(db)

    user_id = await vm_service.activate_key(activate_key)

    vm = await vm_service.get_free_vm(user_id)

    return vm

    