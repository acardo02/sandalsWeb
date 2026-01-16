"""
Rutas para gestión de cupones de descuento
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime, timezone
from beanie import PydanticObjectId

from app.models.coupon_model import Coupon, DiscountType
from app.models.user_model import User
from app.core.dependencies import get_current_admin_user
from app.schemas.coupon_schema import (
    CouponCreate,
    CouponUpdate,
    CouponResponse,
    CouponValidationRequest,
    CouponValidationResponse
)

router = APIRouter()


def coupon_to_response(coupon: Coupon) -> dict:
    """Convierte un cupón a respuesta con id como string"""
    return {
        "id": str(coupon.id),
        "code": coupon.code,
        "description": coupon.description,
        "discount_type": coupon.discount_type.value,
        "discount_value": coupon.discount_value,
        "minimum_amount": coupon.minimum_amount,
        "maximum_discount": coupon.maximum_discount,
        "max_uses": coupon.max_uses,
        "max_uses_per_user": coupon.max_uses_per_user,
        "current_uses": coupon.current_uses,
        "applicable_categories": coupon.applicable_categories,
        "excluded_products": coupon.excluded_products,
        "valid_from": coupon.valid_from.isoformat() if coupon.valid_from else None,
        "valid_until": coupon.valid_until.isoformat() if coupon.valid_until else None,
        "is_active": coupon.is_active,
        "created_by": coupon.created_by,
        "created_at": coupon.created_at.isoformat() if coupon.created_at else None,
        "updated_at": coupon.updated_at.isoformat() if coupon.updated_at else None
    }


# ==================== ENDPOINTS PÚBLICOS ====================

@router.post("/validate")
async def validate_coupon(request: CouponValidationRequest):
    """
    Valida un cupón y calcula el descuento (público).

    - Verifica que el cupón exista y esté activo
    - Verifica fechas de validez
    - Verifica límites de uso
    - Calcula el descuento aplicable
    """
    coupon = await Coupon.find_one(Coupon.code == request.code.upper().strip())

    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cupón no encontrado"
        )

    # Validar cupón
    is_valid, error_msg = coupon.is_valid()
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    # Verificar monto mínimo
    if coupon.minimum_amount and request.subtotal < coupon.minimum_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Compra mínima requerida: ${coupon.minimum_amount:.2f}"
        )

    # Calcular descuento
    discount_amount = coupon.calculate_discount(request.subtotal)
    new_total = request.subtotal - discount_amount

    return {
        "valid": True,
        "code": coupon.code,
        "description": coupon.description,
        "discount_type": coupon.discount_type.value,
        "discount_value": coupon.discount_value,
        "discount_amount": round(discount_amount, 2),
        "new_total": round(new_total, 2),
        "minimum_amount": coupon.minimum_amount
    }


# ==================== ENDPOINTS DE ADMIN ====================

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_coupon(
    coupon_in: CouponCreate,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Crea un nuevo cupón de descuento (solo admin).
    """
    # Verificar que no exista un cupón con el mismo código
    existing = await Coupon.find_one(Coupon.code == coupon_in.code.upper().strip())
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un cupón con ese código"
        )

    # Validar fechas
    if coupon_in.valid_until <= coupon_in.valid_from:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de expiración debe ser posterior a la fecha de inicio"
        )

    coupon = Coupon(
        code=coupon_in.code.upper().strip(),
        description=coupon_in.description,
        discount_type=coupon_in.discount_type,
        discount_value=coupon_in.discount_value,
        minimum_amount=coupon_in.minimum_amount,
        maximum_discount=coupon_in.maximum_discount,
        max_uses=coupon_in.max_uses,
        max_uses_per_user=coupon_in.max_uses_per_user,
        applicable_categories=coupon_in.applicable_categories,
        excluded_products=coupon_in.excluded_products,
        valid_from=coupon_in.valid_from,
        valid_until=coupon_in.valid_until,
        is_active=coupon_in.is_active,
        created_by=current_user.email
    )

    await coupon.create()

    return coupon_to_response(coupon)


@router.get("/")
async def list_coupons(
    active_only: bool = Query(False, description="Solo cupones activos"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Lista todos los cupones (solo admin).
    """
    query = Coupon.find()

    if active_only:
        now = datetime.now(timezone.utc)
        query = Coupon.find(
            Coupon.is_active == True,
            Coupon.valid_from <= now,
            Coupon.valid_until >= now
        )

    coupons = await query.sort(-Coupon.created_at).skip(skip).limit(limit).to_list()

    return [coupon_to_response(c) for c in coupons]


@router.get("/{code}")
async def get_coupon(
    code: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Obtiene un cupón por su código (solo admin).
    """
    coupon = await Coupon.find_one(Coupon.code == code.upper().strip())

    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cupón no encontrado"
        )

    return coupon_to_response(coupon)


@router.patch("/{code}")
async def update_coupon(
    code: str,
    coupon_update: CouponUpdate,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Actualiza un cupón existente (solo admin).
    """
    coupon = await Coupon.find_one(Coupon.code == code.upper().strip())

    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cupón no encontrado"
        )

    # Actualizar campos proporcionados
    update_data = coupon_update.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(coupon, field, value)

    coupon.updated_at = datetime.now(timezone.utc)
    await coupon.save()

    return coupon_to_response(coupon)


@router.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_coupon(
    code: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Elimina un cupón (solo admin).
    """
    coupon = await Coupon.find_one(Coupon.code == code.upper().strip())

    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cupón no encontrado"
        )

    await coupon.delete()


@router.post("/{code}/deactivate")
async def deactivate_coupon(
    code: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Desactiva un cupón sin eliminarlo (solo admin).
    """
    coupon = await Coupon.find_one(Coupon.code == code.upper().strip())

    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cupón no encontrado"
        )

    coupon.is_active = False
    coupon.updated_at = datetime.now(timezone.utc)
    await coupon.save()

    return coupon_to_response(coupon)
