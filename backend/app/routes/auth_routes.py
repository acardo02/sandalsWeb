from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user_model import User
from app.core.security import verify_password, create_access_context, get_password_hash
from app.schemas.user_schema import UserResponse, UserCreate
from typing import Any

router = APIRouter()

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    user = await User.find_one(User.email == form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrecta"
        )
    
    access_token = create_access_context(subject=user.email)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user.id)
    }

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):

    user_exists = await User.find_one(User.email == user.email)
    if user_exists:
        raise HTTPException(
            status_code=400,
            detail="Este correo a esta registrado"
        )
    
    hashed_password = get_password_hash(password=user.password)
    user_data = user.model_dump(exclude={"password"})
    user_data["hashed_password"] = hashed_password

    new_user = User(**user_data)
    
    await new_user.create()

    return new_user