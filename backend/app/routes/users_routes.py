from fastapi import APIRouter, HTTPException, status, Depends
from app.models.user_model import User
from app.schemas.user_schema import UserResponse
from app.core.dependencies import get_current_user

router = APIRouter()
 
@router.get("/")
async def get_users():
    return await User.find_all().to_list()

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user