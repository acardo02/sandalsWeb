from pydantic import BaseModel, Field
from typing import Optional, List
from beanie import PydanticObjectId
from datetime import datetime
from app.models.orders_model import OrderItem, OrderStatus
from app.models.user_model import Address

class OrderItemInput(BaseModel):
    product_id: PydanticObjectId
    quantity: int = Field(..., gt=0, example=1)

class OrderCreate(BaseModel):
    items: List[OrderItemInput]
    shipping_address: Optional[Address] = None

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

class OrderResponse(BaseModel):
    id: PydanticObjectId
    status: OrderStatus
    total_amount: float
    items: List[OrderItem]
    created_at: datetime
    shipping_address: Address

    class Config:
        from_attributes = True