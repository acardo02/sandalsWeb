from typing import Optional, List
from datetime import datetime, timezone
from enum import Enum
from beanie import Document, PydanticObjectId
from pydantic import BaseModel, Field
from pymongo import IndexModel, DESCENDING
from app.models.user_model import Address


class OrderStatus(str, Enum):
    """Estados posibles de una orden"""
    PENDING = "PENDING"  # Orden creada, esperando pago
    PAID = "PAID"  # Pago confirmado
    PROCESSING = "PROCESSING"  # En preparación
    SHIPPED = "SHIPPED"  # Enviado
    DELIVERED = "DELIVERED"  # Entregado
    CANCELLED = "CANCELLED"  # Cancelado
    REFUNDED = "REFUNDED"  # Reembolsado
    FAILED = "FAILED"  # Pago fallido


class PaymentMethod(str, Enum):
    """Métodos de pago disponibles"""
    WOMPI_CARD = "wompi_card"  # Tarjeta de crédito/débito vía Wompi
    WOMPI_TRANSFER = "wompi_transfer"  # Transferencia bancaria vía Wompi
    CASH_ON_DELIVERY = "cash_on_delivery"  # Contra entrega


class OrderItem(BaseModel):
    """Item individual en una orden"""
    product_id: PydanticObjectId
    product_name: str
    quantity: int = Field(..., gt=0)
    price: float = Field(..., gt=0)

    # Para productos con variantes
    variant_sku: Optional[str] = Field(None, description="SKU de la variante")
    variant_info: Optional[str] = Field(None, description="Info de la variante (Talla M, Negro)")

    # Imagen del producto al momento de la compra
    product_image: Optional[str] = None

    @property
    def subtotal(self) -> float:
        return self.price * self.quantity


class TrackingEvent(BaseModel):
    """Evento de tracking de una orden"""
    status: OrderStatus
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    location: Optional[str] = None
    notes: Optional[str] = None
    updated_by: Optional[str] = None  # Email del admin/sistema


class Order(Document):
    """
    Orden de compra completa con tracking, shipping y pagos
    """
    # Usuario
    user_id: PydanticObjectId
    user_email: str  # Email para enviar confirmaciones

    # Items
    items: List[OrderItem]

    # Precios
    subtotal: float = Field(..., description="Suma de items sin descuentos ni envío")
    discount_amount: float = Field(default=0, ge=0, description="Descuento aplicado")
    shipping_cost: float = Field(default=0, ge=0, description="Costo de envío")
    total_amount: float = Field(..., description="Total final (subtotal - discount + shipping)")

    # Cupón
    coupon_code: Optional[str] = None
    coupon_discount_type: Optional[str] = None
    coupon_discount_value: Optional[float] = None

    # Envío
    shipping_address: Address
    shipping_method_id: Optional[str] = None
    shipping_method_name: Optional[str] = None
    tracking_number: Optional[str] = None
    carrier: Optional[str] = None
    estimated_delivery: Optional[datetime] = None

    # Tracking history
    tracking_history: List[TrackingEvent] = Field(default_factory=list)

    # Estado
    status: OrderStatus = OrderStatus.PENDING

    # Pago
    payment_method: Optional[PaymentMethod] = None
    wompi_transaction_id: Optional[str] = None
    wompi_payment_link: Optional[str] = None
    paid_at: Optional[datetime] = None

    # Notas
    customer_notes: Optional[str] = None
    admin_notes: Optional[str] = None

    # Metadata
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "orders"
        indexes = [
            IndexModel(
                [("user_id", DESCENDING), ("created_at", DESCENDING)],
                name="user_orders_idx"
            ),
            IndexModel(
                [("status", DESCENDING), ("created_at", DESCENDING)],
                name="status_orders_idx"
            ),
            "wompi_transaction_id",
            "tracking_number"
        ]

    def add_tracking_event(
        self,
        status: OrderStatus,
        location: Optional[str] = None,
        notes: Optional[str] = None,
        updated_by: Optional[str] = None
    ):
        """Agrega un evento al historial de tracking"""
        event = TrackingEvent(
            status=status,
            location=location,
            notes=notes,
            updated_by=updated_by
        )
        self.tracking_history.append(event)
        self.status = status
        self.updated_at = datetime.now(timezone.utc)

    def get_latest_tracking(self) -> Optional[TrackingEvent]:
        """Retorna el último evento de tracking"""
        if not self.tracking_history:
            return None
        return self.tracking_history[-1]
