from fastapi import APIRouter, Depends

from sqlalchemy.ext.asyncio import AsyncSession

from app.services import AuthService
from app.schemas import UserRead, UserCreate, TokenResponse
from app.core import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead)
async def registration_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):

    auth_service = AuthService(db)

    new_user = await auth_service.register_user(user_data)

    return new_user

@router.post("/login", response_model=TokenResponse)
async def login(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    auth_service = AuthService(db)

    token_data = await auth_service.login_user(user_data)

    return token_data