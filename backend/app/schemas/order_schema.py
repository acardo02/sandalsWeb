from pydantic import BaseModel, Field
from typing import Optional, List
from beanie import PydanticObjectId
from datetime import datetime
from app.models.orders_model import OrderItem, OrderStatus, TrackingEvent, PaymentMethod
from app.models.user_model import Address


class OrderItemInput(BaseModel):
    """Input para un item en una orden"""
    product_id: PydanticObjectId
    quantity: int = Field(..., gt=0, example=1)
    variant_sku: Optional[str] = Field(None, description="SKU de la variante seleccionada")


class OrderCreate(BaseModel):
    """Schema para crear una orden"""
    items: List[OrderItemInput]
    shipping_address: Optional[Address] = None
    shipping_method_id: Optional[str] = Field(None, description="ID del método de envío")
    coupon_code: Optional[str] = Field(None, description="Código de cupón de descuento")
    customer_notes: Optional[str] = Field(None, max_length=500, description="Notas del cliente")

    class Config:
        json_schema_extra = {
            "example": {
                "items": [
                    {"product_id": "507f1f77bcf86cd799439011", "quantity": 2, "variant_sku": "SAND-001-38-BLACK"}
                ],
                "shipping_method_id": "standard_ss",
                "coupon_code": "BIENVENIDO10"
            }
        }


class OrderStatusUpdate(BaseModel):
    """Schema para actualizar estado de una orden"""
    status: OrderStatus
    notes: Optional[str] = Field(None, description="Notas sobre el cambio de estado")
    location: Optional[str] = Field(None, description="Ubicación (para tracking)")


class ShippingUpdate(BaseModel):
    """Schema para actualizar información de envío"""
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    estimated_delivery: Optional[datetime] = None


class TrackingEventResponse(BaseModel):
    """Respuesta de un evento de tracking"""
    status: OrderStatus
    timestamp: datetime
    location: Optional[str]
    notes: Optional[str]
    updated_by: Optional[str]

    class Config:
        from_attributes = True


class OrderItemResponse(BaseModel):
    """Respuesta de un item en una orden"""
    product_id: PydanticObjectId
    product_name: str
    quantity: int
    price: float
    variant_sku: Optional[str]
    variant_info: Optional[str]
    product_image: Optional[str]

    @property
    def subtotal(self) -> float:
        return self.price * self.quantity

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Respuesta completa de una orden"""
    id: PydanticObjectId
    user_id: PydanticObjectId
    user_email: str

    # Items
    items: List[OrderItem]

    # Precios
    subtotal: float
    discount_amount: float
    shipping_cost: float
    total_amount: float

    # Cupón
    coupon_code: Optional[str]

    # Envío
    shipping_address: Address
    shipping_method_name: Optional[str]
    tracking_number: Optional[str]
    carrier: Optional[str]
    estimated_delivery: Optional[datetime]

    # Tracking
    tracking_history: List[TrackingEventResponse]

    # Estado
    status: OrderStatus

    # Pago
    payment_method: Optional[PaymentMethod]
    wompi_payment_link: Optional[str]
    paid_at: Optional[datetime]

    # Notas
    customer_notes: Optional[str]

    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaymentLinkResponse(BaseModel):
    """Respuesta al crear un link de pago"""
    order_id: str
    payment_link: str
    expires_at: Optional[str]


class CouponValidationResponse(BaseModel):
    """Respuesta de validación de cupón"""
    valid: bool
    code: str
    discount_type: str
    discount_value: float
    discount_amount: float
    new_total: float
