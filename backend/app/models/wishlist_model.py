from typing import List
from datetime import datetime, timezone
from beanie import Document, PydanticObjectId, Indexed
from pydantic import Field


class Wishlist(Document):
    """
    Lista de deseos de un usuario
    """
    user_id: Indexed(PydanticObjectId, unique=True) = Field(..., description="ID del usuario")
    products: List[PydanticObjectId] = Field(default_factory=list, description="IDs de productos")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "wishlists"
