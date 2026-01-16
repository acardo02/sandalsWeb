from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ReviewCreate(BaseModel):
    """Schema para crear review"""
    product_id: str
    order_id: Optional[str] = Field(None, description="ID de la orden (para compra verificada)")
    rating: int = Field(..., ge=1, le=5, description="Calificación 1-5 estrellas")
    title: str = Field(..., min_length=3, max_length=100)
    comment: str = Field(..., min_length=10, max_length=2000)
    images: List[str] = Field(default_factory=list, description="URLs de imágenes subidas")

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "507f1f77bcf86cd799439011",
                "order_id": "507f1f77bcf86cd799439012",
                "rating": 5,
                "title": "¡Excelente calidad!",
                "comment": "Las sandalias son hermosas y muy cómodas. Totalmente recomendadas.",
                "variant_sku": "SAND-001-38-BLACK",
                "images": []
            }
        }


class ReviewUpdate(BaseModel):
    """Schema para actualizar review"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    comment: Optional[str] = Field(None, min_length=10, max_length=2000)
    images: Optional[List[str]] = None


class ReviewResponse(BaseModel):
    """Schema para respuesta de review"""
    id: str
    product_id: str
    user_id: str
    order_id: str
    rating: int
    title: str
    comment: str
    variant_sku: Optional[str]
    variant_info: Optional[str]
    verified_purchase: bool
    helpful_count: int
    images: List[str]
    is_approved: bool
    is_featured: bool
    created_at: datetime
    updated_at: datetime

    # Info del usuario (agregado desde join)
    user_name: Optional[str] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439013",
                "product_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439014",
                "rating": 5,
                "title": "Excelente producto",
                "comment": "Me encantó",
                "verified_purchase": True,
                "helpful_count": 5,
                "is_approved": True,
                "created_at": "2026-01-13T12:00:00Z",
                "user_name": "María G."
            }
        }


class ReviewSummary(BaseModel):
    """Schema para resumen de reviews de un producto"""
    product_id: str
    average_rating: float
    total_reviews: int
    rating_distribution: dict  # {1: 0, 2: 1, 3: 2, 4: 5, 5: 10}
    verified_purchase_count: int

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "507f1f77bcf86cd799439011",
                "average_rating": 4.5,
                "total_reviews": 18,
                "rating_distribution": {
                    1: 0,
                    2: 1,
                    3: 2,
                    4: 5,
                    5: 10
                },
                "verified_purchase_count": 18
            }
        }
