from typing import Optional, List
from datetime import datetime, timezone
from enum import Enum
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from app.models.user_model import Address

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    fAILED = "FAILED"
    SHIPPED = "SHIPPED"
    CANCELLED = "CANCELLED"

class OrderItem(BaseModel):
    product_id: PydanticObjectId
    product_name: str
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)

    @property
    def subtotal(self) -> float:
        return self.price * self.quantity
    

class Order(Document):
    user_id: PydanticObjectId
    items: List[OrderItem]
    total_amount: float
    status: OrderStatus = OrderStatus.PENDING
    shipping_address: Address

    wompi_transaction_id: Optional[str] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "orders"