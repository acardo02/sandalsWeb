from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from beanie import PydanticObjectId
from datetime import datetime
import re


class AddressSchema(BaseModel):
    street: str = Field(..., example="Av. La Capilla 123")
    city: str = Field(..., example="San Salvador")
    state: str = Field(..., example="San Salvador")
    zip_code: Optional[str] = Field(None, example="1101")
    country: str = Field("SV", example="SV")

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Contraseña plana (mínimo 8 caracteres)")

    first_name: str
    last_name: str
    phone_number: str = Field(..., description="Celular para notificaciones")
    document_id: Optional[str] = Field(None, description="DUI o NIT")
    address: Optional[AddressSchema] = None

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Valida que la contraseña cumpla con requisitos de seguridad:
        - Mínimo 8 caracteres
        - Al menos una letra mayúscula
        - Al menos una letra minúscula
        - Al menos un número
        - Al menos un carácter especial
        """
        if len(v) < 8:
            raise ValueError('La contraseña debe tener mínimo 8 caracteres')

        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')

        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')

        if not re.search(r'\d', v):
            raise ValueError('La contraseña debe contener al menos un número')

        if not re.search(r'[!@#$%^&*()_\-+=\[\]{};:\'",.<>?/\\|`~]', v):
            raise ValueError('La contraseña debe contener al menos un carácter especial')

        return v

class UserResponse(BaseModel):
    id: PydanticObjectId
    email: EmailStr  # ← LÍNEA AGREGADA (IMPORTANTE)
    first_name: str
    last_name: str
    phone_number: str
    document_id: Optional[str]
    address: Optional[AddressSchema]
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    document_id: Optional[str] = None
    address: Optional[AddressSchema] = None