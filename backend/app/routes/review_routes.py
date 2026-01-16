"""
Rutas para gestión de reviews de productos
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime, timezone
from beanie import PydanticObjectId

from app.models.review_model import ProductReview
from app.models.product_model import Product
from app.models.orders_model import Order, OrderStatus
from app.models.user_model import User
from app.core.dependencies import get_current_user, get_current_admin_user
from app.schemas.review_schema import (
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
    ReviewSummary
)

router = APIRouter()


async def update_product_rating(product_id: PydanticObjectId):
    """Actualiza el rating promedio de un producto"""
    reviews = await ProductReview.find(
        ProductReview.product_id == product_id,
        ProductReview.is_approved == True
    ).to_list()

    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        product = await Product.get(product_id)
        if product:
            product.average_rating = round(avg_rating, 2)
            product.review_count = len(reviews)
            await product.save()


# ==================== ENDPOINTS PÚBLICOS ====================

@router.get("/product/{product_id}", response_model=List[ReviewResponse])
async def get_product_reviews(
    product_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    sort_by: str = Query("recent", description="Ordenar por: recent, rating_high, rating_low, helpful")
):
    """
    Obtiene las reviews de un producto.

    Solo muestra reviews aprobadas.
    """
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    query = ProductReview.find(
        ProductReview.product_id == PydanticObjectId(product_id),
        ProductReview.is_approved == True
    )

    # Ordenamiento
    if sort_by == "recent":
        query = query.sort(-ProductReview.created_at)
    elif sort_by == "rating_high":
        query = query.sort(-ProductReview.rating, -ProductReview.created_at)
    elif sort_by == "rating_low":
        query = query.sort(ProductReview.rating, -ProductReview.created_at)
    elif sort_by == "helpful":
        query = query.sort(-ProductReview.helpful_count, -ProductReview.created_at)

    reviews = await query.skip(skip).limit(limit).to_list()

    return reviews


@router.get("/product/{product_id}/summary", response_model=ReviewSummary)
async def get_product_review_summary(product_id: str):
    """
    Obtiene un resumen de las reviews de un producto.

    Incluye: promedio, total de reviews, distribución por estrellas.
    """
    product = await Product.get(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    reviews = await ProductReview.find(
        ProductReview.product_id == PydanticObjectId(product_id),
        ProductReview.is_approved == True
    ).to_list()

    if not reviews:
        return ReviewSummary(
            product_id=product_id,
            average_rating=0,
            total_reviews=0,
            rating_distribution={1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
            verified_purchase_count=0
        )

    # Calcular distribución
    distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    verified_count = 0
    for review in reviews:
        distribution[review.rating] += 1
        if review.verified_purchase:
            verified_count += 1

    avg_rating = sum(r.rating for r in reviews) / len(reviews)

    return ReviewSummary(
        product_id=product_id,
        average_rating=round(avg_rating, 2),
        total_reviews=len(reviews),
        rating_distribution=distribution,
        verified_purchase_count=verified_count
    )


# ==================== ENDPOINTS DE USUARIO ====================

@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_in: ReviewCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Crea una nueva review.

    El usuario debe haber comprado el producto para dejar una review verificada.
    """
    # Verificar que el producto existe
    product = await Product.get(review_in.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado"
        )

    # Verificar que el usuario no haya dejado una review para este producto
    existing_review = await ProductReview.find_one(
        ProductReview.product_id == PydanticObjectId(review_in.product_id),
        ProductReview.user_id == current_user.id
    )
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya has dejado una review para este producto"
        )

    # Verificar compra verificada
    verified_purchase = False
    variant_sku = None
    variant_info = None

    if review_in.order_id:
        order = await Order.get(review_in.order_id)
        if order and order.user_id == current_user.id and order.status in [OrderStatus.DELIVERED, OrderStatus.SHIPPED]:
            # Verificar que el producto está en la orden
            for item in order.items:
                if str(item.product_id) == review_in.product_id:
                    verified_purchase = True
                    variant_sku = item.variant_sku
                    variant_info = item.variant_info
                    break

    review = ProductReview(
        product_id=PydanticObjectId(review_in.product_id),
        user_id=current_user.id,
        order_id=PydanticObjectId(review_in.order_id) if review_in.order_id else None,
        rating=review_in.rating,
        title=review_in.title,
        comment=review_in.comment,
        variant_sku=variant_sku,
        variant_info=variant_info,
        verified_purchase=verified_purchase,
        images=review_in.images or [],
        is_approved=True  # Auto-aprobar por ahora
    )

    await review.create()

    # Actualizar rating del producto
    await update_product_rating(PydanticObjectId(review_in.product_id))

    return review


@router.get("/my-reviews", response_model=List[ReviewResponse])
async def get_my_reviews(
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50)
):
    """
    Obtiene las reviews del usuario actual.
    """
    reviews = await ProductReview.find(
        ProductReview.user_id == current_user.id
    ).sort(-ProductReview.created_at).skip(skip).limit(limit).to_list()

    return reviews


@router.patch("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: str,
    review_update: ReviewUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Actualiza una review propia.
    """
    review = await ProductReview.get(review_id)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review no encontrada"
        )

    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes editar esta review"
        )

    update_data = review_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)

    review.updated_at = datetime.now(timezone.utc)
    await review.save()

    # Actualizar rating si cambió
    if "rating" in update_data:
        await update_product_rating(review.product_id)

    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Elimina una review propia.
    """
    review = await ProductReview.get(review_id)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review no encontrada"
        )

    if review.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes eliminar esta review"
        )

    product_id = review.product_id
    await review.delete()

    # Actualizar rating del producto
    await update_product_rating(product_id)


@router.post("/{review_id}/helpful")
async def mark_review_helpful(
    review_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Marca una review como útil.
    """
    review = await ProductReview.get(review_id)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review no encontrada"
        )

    review.helpful_count += 1
    await review.save()

    return {"success": True, "helpful_count": review.helpful_count}


# ==================== ENDPOINTS DE ADMIN ====================

@router.get("/admin/pending", response_model=List[ReviewResponse])
async def get_pending_reviews(
    current_user: User = Depends(get_current_admin_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50)
):
    """
    Obtiene reviews pendientes de aprobación (solo admin).
    """
    reviews = await ProductReview.find(
        ProductReview.is_approved == False
    ).sort(-ProductReview.created_at).skip(skip).limit(limit).to_list()

    return reviews


@router.post("/admin/{review_id}/approve", response_model=ReviewResponse)
async def approve_review(
    review_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Aprueba una review (solo admin).
    """
    review = await ProductReview.get(review_id)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review no encontrada"
        )

    review.is_approved = True
    review.updated_at = datetime.now(timezone.utc)
    await review.save()

    # Actualizar rating del producto
    await update_product_rating(review.product_id)

    return review


@router.post("/admin/{review_id}/feature", response_model=ReviewResponse)
async def feature_review(
    review_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Marca una review como destacada (solo admin).
    """
    review = await ProductReview.get(review_id)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review no encontrada"
        )

    review.is_featured = not review.is_featured
    review.updated_at = datetime.now(timezone.utc)
    await review.save()

    return review
