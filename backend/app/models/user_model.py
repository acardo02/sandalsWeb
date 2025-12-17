from beanie import Document
from pydantic import EmailStr, BaseModel, Field
from typing import Optional
from datetime import datetime, timezone


class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: Optional[str] = None
    country: str = "SV"

class User(Document):
    email: EmailStr = Field(unique=True)
    hashed_password: str
    first_name: str
    last_name: str
    phone_number: str
    document_id: Optional[str] = None
    address: Optional[Address] = None
    role: str = "customer"
    is_active: bool = True

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


    class Settings:
        name = "users"  # nombre de la colección
