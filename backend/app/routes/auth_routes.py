from fastapi import Depends, APIRouter, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.models.user_model import User
from app.core.security import verify_password, create_access_context, get_password_hash
from app.schemas.user_schema import UserResponse, UserCreate
from typing import Any
import logging

logger = logging.getLogger(__name__)
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    Autenticación de usuario.

    Rate limit: 5 intentos por minuto por IP.
    """
    user = await User.find_one(User.email == form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Failed login attempt for email: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrecta"
        )

    logger.info(f"User {user.email} logged in successfully")
    access_token = create_access_context(subject=user.email)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user.id)
    }

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    """
    Registra un nuevo usuario.

    - Valida que el email no esté en uso
    - Valida fortaleza de contraseña
    - Hashea la contraseña con bcrypt
    """
    user_exists = await User.find_one(User.email == user.email)
    if user_exists:
        logger.warning(f"Registration attempt with existing email: {user.email}")
        raise HTTPException(
            status_code=400,
            detail="Este correo ya está registrado"
        )

    hashed_password = get_password_hash(password=user.password)
    user_data = user.model_dump(exclude={"password"})
    user_data["hashed_password"] = hashed_password

    new_user = User(**user_data)

    await new_user.create()

    logger.info(f"New user registered: {new_user.email}")

    return new_user

# 🔒 ENDPOINT PARA CREAR ADMIN - CONTROLADO POR VARIABLE DE ENTORNO
@router.post("/register-admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_admin_user(user: UserCreate):
    from app.core.config import settings

    # Verificar si el endpoint está activado
    if not settings.ALLOW_ADMIN_CREATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La creación de administradores está desactivada"
        )
    
    # Verificar si el usuario ya existe
    user_exists = await User.find_one(User.email == user.email)
    if user_exists:
        raise HTTPException(
            status_code=400,
            detail="Este correo ya está registrado"
        )
    
    # Crear usuario con rol admin
    hashed_password = get_password_hash(password=user.password)
    user_data = user.model_dump(exclude={"password"})
    user_data["hashed_password"] = hashed_password
    user_data["role"] = "admin"
    
    new_user = User(**user_data)
    await new_user.create()
    
    return new_user