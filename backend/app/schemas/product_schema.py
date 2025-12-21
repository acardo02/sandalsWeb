from pydantic import BaseModel, Field
from typing import Optional
from beanie import PydanticObjectId
from datetime import datetime

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    sku: str
    image_url: Optional[str] = None
    category:str

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: PydanticObjectId
    created_at: datetime

    class Config:
        from_attributes = True

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    sku: Optional[str] = None
    image_url: Optional[str] = None