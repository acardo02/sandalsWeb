from typing import Optional, List
from datetime import datetime, timezone
from beanie import Document, Indexed
from pydantic import Field, BaseModel
from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT


class ProductVariant(BaseModel):
    """
    Representa una variante de un producto (ej: Talla M, Color Negro)
    """
    sku: str = Field(..., description="SKU único de la variante")
    size: Optional[str] = Field(None, description="Talla: 35-43 o S-XL")
    color: Optional[str] = Field(None, description="Color de la variante")
    color_hex: Optional[str] = Field(None, description="Código hexadecimal del color")
    price_adjustment: float = Field(default=0, description="Ajuste de precio (+/-) sobre precio base")
    stock: int = Field(default=0, ge=0, description="Stock disponible de esta variante")
    image_url: Optional[str] = Field(None, description="Imagen específica de esta variante")
    is_available: bool = Field(default=True, description="Si la variante está disponible para venta")


class Product(Document):
    """
    Modelo de producto mejorado con soporte para variantes
    """
    # Información básica
    name: str = Field(..., max_length=150)
    description: Optional[str] = None
    category: Indexed(str) = Field(default="General", max_length=50)

    # Pricing
    base_price: float = Field(..., gt=0, description="Precio base del producto")

    # Sistema de variantes
    has_variants: bool = Field(default=False, description="Si el producto tiene variantes")
    variants: List[ProductVariant] = Field(default_factory=list, description="Lista de variantes")

    # Para productos SIN variantes (compatibilidad hacia atrás)
    sku: Optional[Indexed(str, unique=True)] = Field(None, description="SKU para producto simple")
    stock: Optional[int] = Field(None, ge=0, description="Stock para producto simple")

    # Imágenes (múltiples imágenes soportadas)
    images: List[str] = Field(default_factory=list, description="URLs de imágenes del producto")
    main_image: Optional[str] = Field(None, description="Imagen principal (primera por defecto)")

    # SEO y metadata
    slug: Optional[str] = Field(None, description="URL-friendly name")
    tags: List[str] = Field(default_factory=list, description="Tags para búsqueda")

    # Reviews (agregados)
    average_rating: float = Field(default=0, ge=0, le=5, description="Rating promedio")
    review_count: int = Field(default=0, ge=0, description="Cantidad de reviews")

    # Metadata
    is_featured: bool = Field(default=False, description="Producto destacado")
    is_active: bool = Field(default=True, description="Producto activo")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "products"
        indexes = [
            # Índice compuesto para consultas de categoría y fecha
            IndexModel(
                [("category", ASCENDING), ("created_at", DESCENDING)],
                name="category_created_idx"
            ),
            # Índice de texto para búsqueda en nombre, descripción y tags
            IndexModel(
                [("name", TEXT), ("description", TEXT), ("tags", TEXT)],
                name="search_text_idx"
            ),
            # Índice para productos destacados
            IndexModel(
                [("is_featured", DESCENDING), ("created_at", DESCENDING)],
                name="featured_idx"
            ),
        ]

    def get_total_stock(self) -> int:
        """Retorna el stock total del producto (suma de variantes o stock simple)"""
        if self.has_variants:
            return sum(v.stock for v in self.variants if v.is_available)
        return self.stock or 0

    def get_price_range(self) -> tuple[float, float]:
        """Retorna el rango de precios (min, max) considerando variantes"""
        if not self.has_variants or not self.variants:
            return (self.base_price, self.base_price)

        prices = [self.base_price + v.price_adjustment for v in self.variants if v.is_available]
        if not prices:
            return (self.base_price, self.base_price)

        return (min(prices), max(prices))

    def get_variant_by_sku(self, sku: str) -> Optional[ProductVariant]:
        """Busca una variante por su SKU"""
        if not self.has_variants:
            return None

        for variant in self.variants:
            if variant.sku == sku:
                return variant
        return None
