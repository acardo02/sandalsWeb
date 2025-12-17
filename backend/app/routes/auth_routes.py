from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user_model import User
from app.core.security import verify_password, create_access_context
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