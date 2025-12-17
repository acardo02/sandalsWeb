from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.user_model import User
from app.schemas.user_schema import UserCreate, UserResponse
from app.core.security import get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])



@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):

    user_exists = await User.find_one(User.email == user.email)
    if user_exists:
        raise HTTPException(
            status_code=400,
            detail="Este correo a esta registrado"
        )
    hashed_password = get_password_hash(user.password)
    user_data = user.model_dump(exclude={"password"})
    user_data["hashed_password"] = hashed_password

    new_user = User(**user_data)
    await new_user.create()
    return new_user

@router.get("/")
async def get_users():
    return await User.find_all().to_list()