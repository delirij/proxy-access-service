from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.services import VirtualMachineService
from app.schemas import VirtualMachineCreate, VirtualMachineRead, VirtualMachineUpdate
from app.core import get_db

router = APIRouter(prefix="/vm", tags=["vm"])

