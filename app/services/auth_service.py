from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from app.models import User
from app.schemas import UserCreate
from app.core import get_settings

settings = get_settings()
   
    
class AuthService():
    pass


