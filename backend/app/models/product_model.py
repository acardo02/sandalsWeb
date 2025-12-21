from typing import Optional
from datetime import datetime, timezone
from beanie import Document, Indexed
from pydantic import Field

class Product(Document):
    name: str = Field(..., max_length=150)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    stock: int = Field(default=0, ge=0)
    sku: Indexed(str, unique=True)
    image_url: Optional[str] = None
    category: str = Field(default="General", max_length=50)


    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "products"        