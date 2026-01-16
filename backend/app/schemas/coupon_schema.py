from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.coupon_model import DiscountType


class CouponCreate(BaseModel):
    """Schema para crear cupón"""
    code: str = Field(..., min_length=3, max_length=50, description="Código del cupón")
    description: str = Field(..., max_length=200)
    discount_type: DiscountType
    discount_value: float = Field(..., gt=0)
    minimum_amount: Optional[float] = Field(None, ge=0)
    maximum_discount: Optional[float] = Field(None, gt=0)
    max_uses: Optional[int] = Field(None, gt=0)
    max_uses_per_user: int = Field(default=1, gt=0)
    applicable_categories: List[str] = Field(default_factory=list)
    excluded_products: List[str] = Field(default_factory=list)
    valid_from: datetime
    valid_until: datetime
    is_active: bool = Field(default=True)

    class Config:
        json_schema_extra = {
            "example": {
                "code": "BIENVENIDA2026",
                "description": "20% de descuento para nuevos clientes",
                "discount_type": "percentage",
                "discount_value": 20,
                "minimum_amount": 30.00,
                "maximum_discount": 50.00,
                "max_uses": 100,
                "max_uses_per_user": 1,
                "applicable_categories": [],
                "excluded_products": [],
                "valid_from": "2026-01-01T00:00:00Z",
                "valid_until": "2026-12-31T23:59:59Z"
            }
        }


class CouponUpdate(BaseModel):
    """Schema para actualizar cupón"""
    description: Optional[str] = None
    discount_value: Optional[float] = Field(None, gt=0)
    minimum_amount: Optional[float] = None
    maximum_discount: Optional[float] = None
    max_uses: Optional[int] = None
    is_active: Optional[bool] = None
    valid_until: Optional[datetime] = None


class CouponResponse(BaseModel):
    """Schema para respuesta de cupón"""
    id: str
    code: str
    description: str
    discount_type: DiscountType
    discount_value: float
    minimum_amount: Optional[float]
    maximum_discount: Optional[float]
    max_uses: Optional[int]
    max_uses_per_user: int
    current_uses: int
    applicable_categories: List[str]
    excluded_products: List[str]
    valid_from: datetime
    valid_until: datetime
    is_active: bool
    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CouponValidationRequest(BaseModel):
    """Schema para validar un cupón"""
    code: str
    subtotal: float = Field(..., gt=0)
    cart_items: Optional[List[dict]] = None  # Para validar categorías/productos

    class Config:
        json_schema_extra = {
            "example": {
                "code": "BIENVENIDA2026",
                "subtotal": 50.00
            }
        }


class CouponValidationResponse(BaseModel):
    """Schema para respuesta de validación de cupón"""
    valid: bool
    code: str
    description: Optional[str] = None
    discount_type: str
    discount_value: float
    discount_amount: float
    new_total: float
    minimum_amount: Optional[float] = None
    message: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "valid": True,
                "code": "BIENVENIDA2026",
                "description": "20% de descuento",
                "discount_type": "percentage",
                "discount_value": 20,
                "discount_amount": 10.00,
                "new_total": 40.00,
                "message": "Cupón aplicado exitosamente"
            }
        }
