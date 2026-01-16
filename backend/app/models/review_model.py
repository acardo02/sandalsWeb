from typing import Optional, List
from datetime import datetime, timezone
from beanie import Document, PydanticObjectId
from pydantic import Field
from pymongo import IndexModel, DESCENDING


class ProductReview(Document):
    """
    Review/Calificación de un producto
    """
    product_id: PydanticObjectId = Field(..., description="ID del producto")
    user_id: PydanticObjectId = Field(..., description="ID del usuario")
    order_id: PydanticObjectId = Field(..., description="ID de la orden (compra verificada)")

    # Rating y contenido
    rating: int = Field(..., ge=1, le=5, description="Calificación de 1 a 5 estrellas")
    title: str = Field(..., max_length=100, description="Título de la review")
    comment: str = Field(..., max_length=2000, description="Comentario detallado")

    # Variante específica (si aplica)
    variant_sku: Optional[str] = Field(None, description="SKU de la variante comprada")
    variant_info: Optional[str] = Field(None, description="Info de variante (ej: 'Talla M, Negro')")

    # Metadata
    verified_purchase: bool = Field(default=True, description="Compra verificada")
    helpful_count: int = Field(default=0, ge=0, description="Cantidad de 'útil'")
    images: List[str] = Field(default_factory=list, description="Fotos subidas por el usuario")

    # Moderación
    is_approved: bool = Field(default=True, description="Si la review está aprobada")
    is_featured: bool = Field(default=False, description="Review destacada")

    # Timestamps
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "product_reviews"
        indexes = [
            IndexModel(
                [("product_id", DESCENDING), ("is_approved", DESCENDING), ("created_at", DESCENDING)],
                name="product_reviews_idx"
            ),
            IndexModel(
                [("user_id", DESCENDING), ("created_at", DESCENDING)],
                name="user_reviews_idx"
            ),
        ]
