from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from beanie import PydanticObjectId
from datetime import datetime


class AddressSchema(BaseModel):
    street: str = Field(..., example="Av. La Capilla 123")
    city: str = Field(..., example="San Salvador")
    state: str = Field(..., example="San Salvador")
    zip_code: Optional[str] = Field(None, example="1101")
    country: str = Field("SV", example="SV")

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Contraseña plana")

    first_name: str
    last_name: str
    phone_number: str = Field(..., description="Celular para notificaciones")
    document_id: Optional[str] = Field(None, description="DUI o NIT")
    address: Optional[AddressSchema] = None

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