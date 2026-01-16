from pydantic import BaseModel, Field
from typing import Optional, List
from beanie import PydanticObjectId
from datetime import datetime


class ProductVariantSchema(BaseModel):
    """Schema para una variante de producto"""
    sku: str = Field(..., description="SKU único de la variante")
    size: Optional[str] = Field(None, description="Talla (35-43, S-XL, etc)")
    color: Optional[str] = Field(None, description="Color")
    color_hex: Optional[str] = Field(None, description="Código hexadecimal del color (#000000)")
    price_adjustment: float = Field(default=0, description="Ajuste sobre precio base (+/-)")
    stock: int = Field(default=0, ge=0, description="Stock disponible")
    image_url: Optional[str] = Field(None, description="Imagen específica de la variante")
    is_available: bool = Field(default=True, description="Disponible para venta")

    class Config:
        json_schema_extra = {
            "example": {
                "sku": "SAND-001-M-BLACK",
                "size": "M",
                "color": "Negro",
                "color_hex": "#000000",
                "price_adjustment": 0,
                "stock": 15,
                "image_url": "https://...",
                "is_available": True
            }
        }


class ProductCreate(BaseModel):
    """Schema para crear un producto"""
    name: str = Field(..., max_length=150)
    description: Optional[str] = None
    category: str = Field(default="General", max_length=50)
    base_price: float = Field(..., gt=0, description="Precio base")

    # Sistema de variantes
    has_variants: bool = Field(default=False)
    variants: List[ProductVariantSchema] = Field(default_factory=list)

    # Para productos simples (sin variantes)
    sku: Optional[str] = Field(None, description="SKU si es producto simple")
    stock: Optional[int] = Field(None, ge=0, description="Stock si es producto simple")

    # Imágenes
    images: List[str] = Field(default_factory=list, description="URLs de imágenes")

    # SEO
    tags: List[str] = Field(default_factory=list)
    is_featured: bool = Field(default=False)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Sandalias Artesanales",
                "description": "Sandalias de cuero hechas a mano",
                "category": "Calzado",
                "base_price": 45.00,
                "has_variants": True,
                "variants": [
                    {
                        "sku": "SAND-001-38-BLACK",
                        "size": "38",
                        "color": "Negro",
                        "color_hex": "#000000",
                        "price_adjustment": 0,
                        "stock": 10
                    }
                ],
                "images": ["https://..."],
                "tags": ["artesanal", "cuero"],
                "is_featured": False
            }
        }


class ProductUpdate(BaseModel):
    """Schema para actualizar un producto"""
    name: Optional[str] = Field(None, max_length=150)
    description: Optional[str] = None
    category: Optional[str] = None
    base_price: Optional[float] = Field(None, gt=0)
    variants: Optional[List[ProductVariantSchema]] = None
    stock: Optional[int] = Field(None, ge=0)
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    """Schema para respuesta de producto"""
    id: str
    name: str
    description: Optional[str]
    category: str
    base_price: float

    has_variants: bool
    variants: List[ProductVariantSchema]

    sku: Optional[str]
    stock: Optional[int]

    images: List[str]
    main_image: Optional[str]

    tags: List[str]
    average_rating: float
    review_count: int

    is_featured: bool
    is_active: bool

    created_at: datetime
    updated_at: datetime

    # Campos calculados
    total_stock: Optional[int] = None
    price_range: Optional[tuple[float, float]] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "Sandalias Artesanales",
                "description": "Sandalias de cuero",
                "category": "Calzado",
                "base_price": 45.00,
                "has_variants": True,
                "variants": [],
                "images": ["https://..."],
                "average_rating": 4.5,
                "review_count": 10,
                "total_stock": 50,
                "price_range": [45.00, 50.00]
            }
        }
