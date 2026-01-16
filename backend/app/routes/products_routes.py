"""
Rutas para gestion de productos
"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from datetime import datetime, timezone
from beanie import PydanticObjectId

from app.models.user_model import User
from app.models.product_model import Product, ProductVariant
from app.schemas.product_schema import ProductCreate, ProductUpdate, ProductVariantSchema
from app.core.dependencies import get_current_admin_user

router = APIRouter()


def product_to_response(product: Product) -> dict:
    """Convierte un producto a respuesta con campos calculados"""
    # Convertir variantes a dict
    variants_list = []
    for v in product.variants:
        variants_list.append({
            "sku": v.sku,
            "size": v.size,
            "color": v.color,
            "color_hex": v.color_hex,
            "price_adjustment": v.price_adjustment,
            "stock": v.stock,
            "image_url": v.image_url,
            "is_available": v.is_available
        })

    return {
        "id": str(product.id),
        "name": product.name,
        "description": product.description,
        "category": product.category,
        "base_price": product.base_price,
        "has_variants": product.has_variants,
        "variants": variants_list,
        "sku": product.sku,
        "stock": product.stock,
        "images": product.images,
        "main_image": product.main_image or (product.images[0] if product.images else None),
        "tags": product.tags,
        "average_rating": product.average_rating,
        "review_count": product.review_count,
        "is_featured": product.is_featured,
        "is_active": product.is_active,
        "created_at": product.created_at.isoformat() if product.created_at else None,
        "updated_at": product.updated_at.isoformat() if product.updated_at else None,
        "total_stock": product.get_total_stock(),
        "price_range": list(product.get_price_range())
    }


# ==================== ENDPOINTS PUBLICOS ====================

@router.get("/")
async def get_products(
    category: Optional[str] = Query(None, description="Filtrar por categoria"),
    search: Optional[str] = Query(None, description="Buscar por nombre"),
    min_price: Optional[float] = Query(None, ge=0, description="Precio minimo"),
    max_price: Optional[float] = Query(None, ge=0, description="Precio maximo"),
    in_stock: Optional[bool] = Query(None, description="Solo productos con stock"),
    featured: Optional[bool] = Query(None, description="Solo productos destacados"),
    tags: Optional[str] = Query(None, description="Filtrar por tags (separados por coma)"),
    sort_by: str = Query("recent", description="Ordenar: recent, price_low, price_high, rating, name"),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0),
    random_sample: bool = Query(False, description="Obtener productos aleatorios")
):
    """
    Obtiene lista de productos con filtros y ordenamiento.
    """
    # CASO RANDOM: Para homepage
    if random_sample:
        pipeline = [
            {"$match": {"is_active": True}},
            {"$sample": {"size": limit}}
        ]
        raw_products = await Product.aggregate(pipeline).to_list()
        # Convertir a objetos Product para usar product_to_response
        products = []
        for p in raw_products:
            prod = Product(**p)
            prod.id = p["_id"]
            products.append(product_to_response(prod))
        return products

    # Construir query
    filters = {"is_active": True}

    if category and category != "Todos":
        filters["category"] = category

    if search:
        filters["name"] = {"$regex": search, "$options": "i"}

    if min_price is not None:
        filters["base_price"] = {"$gte": min_price}

    if max_price is not None:
        if "base_price" in filters:
            filters["base_price"]["$lte"] = max_price
        else:
            filters["base_price"] = {"$lte": max_price}

    if featured is True:
        filters["is_featured"] = True

    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        filters["tags"] = {"$in": tag_list}

    query = Product.find(filters)

    # Ordenamiento
    if sort_by == "recent":
        query = query.sort(-Product.created_at)
    elif sort_by == "price_low":
        query = query.sort(Product.base_price)
    elif sort_by == "price_high":
        query = query.sort(-Product.base_price)
    elif sort_by == "rating":
        query = query.sort(-Product.average_rating, -Product.review_count)
    elif sort_by == "name":
        query = query.sort(Product.name)

    products = await query.skip(skip).limit(limit).to_list()

    # Filtrar por stock si es necesario
    if in_stock is True:
        products = [p for p in products if p.get_total_stock() > 0]

    return [product_to_response(p) for p in products]


@router.get("/featured")
async def get_featured_products(limit: int = Query(8, ge=1, le=20)):
    """
    Obtiene productos destacados.
    """
    products = await Product.find(
        Product.is_active == True,
        Product.is_featured == True
    ).sort(-Product.created_at).limit(limit).to_list()

    return [product_to_response(p) for p in products]


@router.get("/categories")
async def get_categories():
    """
    Obtiene todas las categorias disponibles con conteo de productos.
    """
    pipeline = [
        {"$match": {"is_active": True}},
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]

    result = await Product.aggregate(pipeline).to_list()

    categories = [{"name": r["_id"], "count": r["count"]} for r in result]

    return categories


@router.get("/{product_id}")
async def get_product_details(product_id: str):
    """
    Obtiene el detalle de un producto.
    """
    product = await Product.get(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    return product_to_response(product)


@router.get("/{product_id}/variants")
async def get_product_variants(product_id: str):
    """
    Obtiene las variantes disponibles de un producto.
    """
    product = await Product.get(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    if not product.has_variants:
        return {
            "has_variants": False,
            "variants": [],
            "available_sizes": [],
            "available_colors": []
        }

    # Extraer tallas y colores unicos
    sizes = set()
    colors = []
    color_set = set()

    for variant in product.variants:
        if variant.is_available and variant.stock > 0:
            if variant.size:
                sizes.add(variant.size)
            if variant.color and variant.color not in color_set:
                colors.append({
                    "name": variant.color,
                    "hex": variant.color_hex or "#000000"
                })
                color_set.add(variant.color)

    return {
        "has_variants": True,
        "variants": [{"sku": v.sku, "size": v.size, "color": v.color, "stock": v.stock, "is_available": v.is_available, "price_adjustment": v.price_adjustment} for v in product.variants],
        "available_sizes": sorted(list(sizes)),
        "available_colors": colors
    }


@router.get("/{product_id}/variant/{variant_sku}")
async def get_variant_details(product_id: str, variant_sku: str):
    """
    Obtiene detalles de una variante especifica.
    """
    product = await Product.get(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    variant = product.get_variant_by_sku(variant_sku)

    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Variante no encontrada"
        )

    return {
        "product_id": str(product.id),
        "product_name": product.name,
        "base_price": product.base_price,
        "variant": {"sku": variant.sku, "size": variant.size, "color": variant.color, "stock": variant.stock, "is_available": variant.is_available},
        "final_price": product.base_price + variant.price_adjustment,
        "in_stock": variant.stock > 0 and variant.is_available
    }


# ==================== ENDPOINTS DE ADMIN ====================

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Crea un nuevo producto (solo admin).
    """
    # Verificar SKU unico si es producto simple
    if not product_in.has_variants and product_in.sku:
        existing = await Product.find_one(Product.sku == product_in.sku)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un producto con el SKU: {product_in.sku}"
            )

    # Verificar SKUs de variantes
    if product_in.has_variants and product_in.variants:
        skus = [v.sku for v in product_in.variants]
        if len(skus) != len(set(skus)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Los SKUs de las variantes deben ser unicos"
            )

    # Crear producto
    product_data = product_in.model_dump()

    # Establecer imagen principal si no se especifico
    if product_data.get("images") and not product_data.get("main_image"):
        product_data["main_image"] = product_data["images"][0]

    new_product = Product(**product_data)
    await new_product.create()

    return product_to_response(new_product)


@router.patch("/{product_id}")
async def update_product(
    product_id: str,
    product_update: ProductUpdate,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Actualiza un producto (solo admin).
    """
    product = await Product.get(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    update_data = product_update.model_dump(exclude_unset=True)

    # Actualizar variantes si se proporcionan
    if "variants" in update_data and update_data["variants"]:
        # Verificar SKUs unicos
        skus = [v["sku"] for v in update_data["variants"]]
        if len(skus) != len(set(skus)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Los SKUs de las variantes deben ser unicos"
            )

        # Convertir a objetos ProductVariant
        update_data["variants"] = [
            ProductVariant(**v) for v in update_data["variants"]
        ]

    for field, value in update_data.items():
        setattr(product, field, value)

    product.updated_at = datetime.now(timezone.utc)
    await product.save()

    return product_to_response(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Elimina un producto (solo admin).
    """
    product = await Product.get(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    await product.delete()


@router.post("/{product_id}/deactivate")
async def deactivate_product(
    product_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Desactiva un producto sin eliminarlo (solo admin).
    """
    product = await Product.get(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    product.is_active = False
    product.updated_at = datetime.now(timezone.utc)
    await product.save()

    return product_to_response(product)


@router.post("/{product_id}/activate")
async def activate_product(
    product_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Activa un producto (solo admin).
    """
    product = await Product.get(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    product.is_active = True
    product.updated_at = datetime.now(timezone.utc)
    await product.save()

    return product_to_response(product)


@router.patch("/{product_id}/variants/{variant_sku}/stock")
async def update_variant_stock(
    product_id: str,
    variant_sku: str,
    stock: int = Query(..., ge=0),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Actualiza el stock de una variante especifica (solo admin).
    """
    product = await Product.get(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    variant_found = False
    for i, v in enumerate(product.variants):
        if v.sku == variant_sku:
            product.variants[i].stock = stock
            variant_found = True
            break

    if not variant_found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Variante no encontrada"
        )

    product.updated_at = datetime.now(timezone.utc)
    await product.save()

    return {"success": True, "sku": variant_sku, "new_stock": stock}
