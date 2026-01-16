from typing import Optional, List
from datetime import datetime, timezone
from beanie import Document, Indexed
from pydantic import Field
from enum import Enum


class DiscountType(str, Enum):
    """Tipo de descuento"""
    PERCENTAGE = "percentage"  # Porcentaje (ej: 20%)
    FIXED = "fixed"  # Monto fijo (ej: $5)


class Coupon(Document):
    """
    Cupón de descuento
    """
    code: Indexed(str, unique=True) = Field(..., description="Código del cupón (BIENVENIDA2026)")
    description: str = Field(..., description="Descripción del cupón")

    # Tipo y valor de descuento
    discount_type: DiscountType = Field(..., description="Tipo de descuento")
    discount_value: float = Field(..., gt=0, description="Valor del descuento")

    # Restricciones
    minimum_amount: Optional[float] = Field(None, description="Compra mínima requerida")
    maximum_discount: Optional[float] = Field(None, description="Descuento máximo permitido")

    # Límites de uso
    max_uses: Optional[int] = Field(None, description="Máximo de usos totales")
    max_uses_per_user: int = Field(default=1, description="Máximo de usos por usuario")
    current_uses: int = Field(default=0, ge=0, description="Usos actuales")

    # Aplicabilidad
    applicable_categories: List[str] = Field(
        default_factory=list,
        description="Categorías donde aplica (vacío = todas)"
    )
    excluded_products: List[str] = Field(
        default_factory=list,
        description="IDs de productos excluidos"
    )

    # Vigencia
    valid_from: datetime = Field(..., description="Fecha de inicio")
    valid_until: datetime = Field(..., description="Fecha de expiración")

    # Estado
    is_active: bool = Field(default=True, description="Si el cupón está activo")

    # Metadata
    created_by: Optional[str] = Field(None, description="Email del admin que lo creó")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "coupons"
        indexes = [
            "code",
            "is_active",
            "valid_until"
        ]

    def is_valid(self, current_time: Optional[datetime] = None) -> tuple[bool, str]:
        """
        Verifica si el cupón es válido
        Returns: (is_valid, error_message)
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)

        if not self.is_active:
            return (False, "Cupón inactivo")

        # Normalizar fechas para comparación (remover timezone si es necesario)
        try:
            valid_from = self.valid_from.replace(tzinfo=None) if self.valid_from.tzinfo else self.valid_from
            valid_until = self.valid_until.replace(tzinfo=None) if self.valid_until.tzinfo else self.valid_until
            current = current_time.replace(tzinfo=None) if current_time.tzinfo else current_time

            if current < valid_from:
                return (False, "Cupón aún no válido")

            if current > valid_until:
                return (False, "Cupón expirado")
        except Exception as e:
            # Si hay error en fechas, asumir válido y continuar
            pass

        if self.max_uses is not None and self.current_uses >= self.max_uses:
            return (False, "Cupón sin usos disponibles")

        return (True, "")

    def calculate_discount(self, subtotal: float) -> float:
        """Calcula el monto de descuento para un subtotal dado"""
        if self.discount_type == DiscountType.PERCENTAGE:
            discount = subtotal * (self.discount_value / 100)
        else:  # FIXED
            discount = self.discount_value

        # Aplicar descuento máximo si existe
        if self.maximum_discount is not None:
            discount = min(discount, self.maximum_discount)

        # El descuento no puede ser mayor al subtotal
        return min(discount, subtotal)
