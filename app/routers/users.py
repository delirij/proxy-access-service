from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.services import UserService
from app.schemas import UserRead, UserUpdate
from app.core import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/get_users", response_model=list[UserRead])
async def get_users(
    db: AsyncSession = Depends(get_db)
):
    users_service = UserService(db)

    users = await users_service.get_all_users()

    return users

@router.get("/get_user/{user_id}", response_model=UserRead)
async def get_users_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    
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
    users_service = UserService(db)

    updated_user = await users_service.update_user(user_id, user_data)

    return updated_user

@router.delete("/delete_user/{user_id}", response_model=UserRead)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    users_service = UserService(db)
    deleted_user = await users_service.delete_user(user_id)
    return deleted_user