from typing import Optional
from datetime import datetime, timezone
from beanie import Document
from pydantic import Field, BaseModel


class ShippingMethod(BaseModel):
    """
    Método de envío disponible
    """
    id: str = Field(..., description="ID único del método")
    name: str = Field(..., description="Nombre del método (Estándar, Express)")
    description: str = Field(..., description="Descripción del servicio")
    base_price: float = Field(..., ge=0, description="Precio base del envío")
    estimated_days_min: int = Field(..., ge=1, description="Días mínimos de entrega")
    estimated_days_max: int = Field(..., ge=1, description="Días máximos de entrega")
    carrier: str = Field(..., description="Transportista (Correos SV, DHL)")
    is_active: bool = Field(default=True, description="Si el método está activo")

    # Restricciones
    free_shipping_threshold: Optional[float] = Field(None, description="Monto para envío gratis")
    max_weight_kg: Optional[float] = Field(None, description="Peso máximo permitido")


class ShippingZone(Document):
    """
    Zona de envío con sus precios específicos
    """
    name: str = Field(..., description="Nombre de la zona (San Salvador, La Libertad)")
    department: str = Field(..., description="Departamento")
    shipping_methods: list[ShippingMethod] = Field(default_factory=list)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "shipping_zones"


# Métodos de envío predefinidos para El Salvador
DEFAULT_SHIPPING_METHODS = {
    "standard_ss": ShippingMethod(
        id="standard_ss",
        name="Envío Estándar San Salvador",
        description="Entrega en San Salvador metropolitano",
        base_price=3.00,
        estimated_days_min=2,
        estimated_days_max=4,
        carrier="Correos de El Salvador",
        free_shipping_threshold=50.00
    ),
    "standard_national": ShippingMethod(
        id="standard_national",
        name="Envío Estándar Nacional",
        description="Entrega a todo el país",
        base_price=5.00,
        estimated_days_min=3,
        estimated_days_max=7,
        carrier="Correos de El Salvador",
        free_shipping_threshold=75.00
    ),
    "express": ShippingMethod(
        id="express",
        name="Envío Express",
        description="Entrega rápida (1-2 días)",
        base_price=10.00,
        estimated_days_min=1,
        estimated_days_max=2,
        carrier="DHL Express",
        max_weight_kg=10.0
    )
}
