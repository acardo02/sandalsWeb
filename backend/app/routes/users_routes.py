from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone
from app.models.user_model import User
from app.schemas.user_schema import UserResponse, UserUpdate
from app.core.dependencies import get_current_user, get_current_admin_user

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Obtiene el perfil del usuario actual"""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """Actualiza el perfil del usuario actual"""
    update_data = user_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    current_user.updated_at = datetime.now(timezone.utc)
    await current_user.save()

    return current_user


@router.get("/", response_model=list[UserResponse])
async def get_users(current_user: User = Depends(get_current_admin_user)):
    """Lista todos los usuarios (solo admin)"""
    return await User.find_all().to_list()
