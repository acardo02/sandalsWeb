"""
Rutas para gestión de wishlists (listas de deseos)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime, timezone
from beanie import PydanticObjectId

from app.models.wishlist_model import Wishlist
from app.models.product_model import Product
from app.models.user_model import User
from app.core.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter()


class WishlistResponse(BaseModel):
    """Respuesta de wishlist"""
    products: List[str]
    count: int


class WishlistProductResponse(BaseModel):
    """Producto en wishlist con detalles"""
    id: str
    name: str
    base_price: float
    main_image: str | None
    is_active: bool
    in_stock: bool


@router.get("/", response_model=WishlistResponse)
async def get_wishlist(current_user: User = Depends(get_current_user)):
    """
    Obtiene la wishlist del usuario actual.
    """
    wishlist = await Wishlist.find_one(Wishlist.user_id == current_user.id)

    if not wishlist:
        return WishlistResponse(products=[], count=0)

    return WishlistResponse(
        products=[str(p) for p in wishlist.products],
        count=len(wishlist.products)
    )


@router.get("/products", response_model=List[WishlistProductResponse])
async def get_wishlist_products(current_user: User = Depends(get_current_user)):
    """
    Obtiene la wishlist con detalles de los productos.
    """
    wishlist = await Wishlist.find_one(Wishlist.user_id == current_user.id)

    if not wishlist or not wishlist.products:
        return []

    products = []
    for product_id in wishlist.products:
        product = await Product.get(product_id)
        if product and product.is_active:
            # Calcular si tiene stock
            if product.has_variants:
                in_stock = any(v.stock > 0 and v.is_available for v in product.variants)
            else:
                in_stock = (product.stock or 0) > 0

            products.append(WishlistProductResponse(
                id=str(product.id),
                name=product.name,
                base_price=product.base_price,
                main_image=product.main_image,
                is_active=product.is_active,
                in_stock=in_stock
            ))

    return products


@router.post("/add/{product_id}")
async def add_to_wishlist(
    product_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Agrega un producto a la wishlist.
    """
    # Verificar que el producto existe
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    product_oid = PydanticObjectId(product_id)

    # Buscar o crear wishlist
    wishlist = await Wishlist.find_one(Wishlist.user_id == current_user.id)

    if not wishlist:
        wishlist = Wishlist(
            user_id=current_user.id,
            products=[product_oid]
        )
        await wishlist.create()
    elif product_oid not in wishlist.products:
        wishlist.products.append(product_oid)
        wishlist.updated_at = datetime.now(timezone.utc)
        await wishlist.save()

    return {
        "success": True,
        "message": "Producto agregado a la wishlist",
        "count": len(wishlist.products)
    }


@router.delete("/remove/{product_id}")
async def remove_from_wishlist(
    product_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Remueve un producto de la wishlist.
    """
    wishlist = await Wishlist.find_one(Wishlist.user_id == current_user.id)

    if not wishlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wishlist no encontrada"
        )

    product_oid = PydanticObjectId(product_id)

    if product_oid in wishlist.products:
        wishlist.products.remove(product_oid)
        wishlist.updated_at = datetime.now(timezone.utc)
        await wishlist.save()

    return {
        "success": True,
        "message": "Producto removido de la wishlist",
        "count": len(wishlist.products)
    }


@router.post("/toggle/{product_id}")
async def toggle_wishlist(
    product_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Alterna un producto en la wishlist (agrega si no está, remueve si está).
    """
    # Verificar que el producto existe
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    product_oid = PydanticObjectId(product_id)

    wishlist = await Wishlist.find_one(Wishlist.user_id == current_user.id)

    if not wishlist:
        wishlist = Wishlist(
            user_id=current_user.id,
            products=[product_oid]
        )
        await wishlist.create()
        added = True
    elif product_oid in wishlist.products:
        wishlist.products.remove(product_oid)
        wishlist.updated_at = datetime.now(timezone.utc)
        await wishlist.save()
        added = False
    else:
        wishlist.products.append(product_oid)
        wishlist.updated_at = datetime.now(timezone.utc)
        await wishlist.save()
        added = True

    return {
        "success": True,
        "added": added,
        "message": "Producto agregado a favoritos" if added else "Producto removido de favoritos",
        "count": len(wishlist.products)
    }


@router.get("/check/{product_id}")
async def check_in_wishlist(
    product_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Verifica si un producto está en la wishlist.
    """
    wishlist = await Wishlist.find_one(Wishlist.user_id == current_user.id)

    if not wishlist:
        return {"in_wishlist": False}

    product_oid = PydanticObjectId(product_id)

    return {"in_wishlist": product_oid in wishlist.products}


@router.delete("/clear")
async def clear_wishlist(current_user: User = Depends(get_current_user)):
    """
    Vacía la wishlist del usuario.
    """
    wishlist = await Wishlist.find_one(Wishlist.user_id == current_user.id)

    if wishlist:
        wishlist.products = []
        wishlist.updated_at = datetime.now(timezone.utc)
        await wishlist.save()

    return {"success": True, "message": "Wishlist vaciada"}
