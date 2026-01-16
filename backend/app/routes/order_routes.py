"""
Rutas para gestión de órdenes de compra
"""
from fastapi import HTTPException, APIRouter, status, Depends, Query, BackgroundTasks
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from beanie import PydanticObjectId

from app.models.user_model import User
from app.models.product_model import Product
from app.models.orders_model import Order, OrderItem, OrderStatus, PaymentMethod
from app.models.coupon_model import Coupon
from app.models.shipping_model import DEFAULT_SHIPPING_METHODS
from app.schemas.order_schema import (
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
    ShippingUpdate,
    PaymentLinkResponse
)
from app.core.dependencies import get_current_user, get_current_admin_user
from app.services.wompi_service import wompi_service
from app.services.email_service import email_service

router = APIRouter()


def get_shipping_method(method_id: str):
    """Obtiene un método de envío por su ID"""
    return DEFAULT_SHIPPING_METHODS.get(method_id)


def calculate_shipping_cost(method_id: str, subtotal: float) -> tuple[float, str]:
    """
    Calcula el costo de envío.
    Returns: (costo, nombre del método)
    """
    method = get_shipping_method(method_id)
    if not method:
        return (0.0, "Envío estándar")

    # Verificar si aplica envío gratis
    if method.free_shipping_threshold and subtotal >= method.free_shipping_threshold:
        return (0.0, method.name)

    return (method.base_price, method.name)


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in: OrderCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """
    Crea una nueva orden de compra.

    - Valida stock disponible (incluyendo variantes)
    - Aplica cupón de descuento si se proporciona
    - Calcula costo de envío
    - Descuenta del inventario de forma atómica
    - Envía email de confirmación
    """
    final_items = []
    subtotal = 0.0

    # Validar dirección
    if order_in.shipping_address:
        final_address = order_in.shipping_address
    elif current_user.address:
        final_address = current_user.address
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requiere una dirección de envío"
        )

    # Validar todos los productos y stock
    for item_in in order_in.items:
        product = await Product.get(item_in.product_id)

        if not product or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID: {item_in.product_id} no encontrado o no disponible"
            )

        # Determinar precio y stock según si tiene variantes
        if product.has_variants and item_in.variant_sku:
            variant = product.get_variant_by_sku(item_in.variant_sku)
            if not variant:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Variante '{item_in.variant_sku}' no encontrada para '{product.name}'"
                )

            if not variant.is_available or variant.stock < item_in.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stock insuficiente para '{product.name}' ({variant.size}/{variant.color}). Disponibles: {variant.stock}"
                )

            item_price = product.base_price + variant.price_adjustment
            variant_info = f"{variant.size or ''} {variant.color or ''}".strip()

            new_item = OrderItem(
                product_id=product.id,
                product_name=product.name,
                quantity=item_in.quantity,
                price=item_price,
                variant_sku=variant.sku,
                variant_info=variant_info if variant_info else None,
                product_image=variant.image_url or product.main_image
            )

        else:
            # Producto simple sin variantes
            stock = product.stock or 0
            if stock < item_in.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stock insuficiente para '{product.name}'. Disponibles: {stock}"
                )

            new_item = OrderItem(
                product_id=product.id,
                product_name=product.name,
                quantity=item_in.quantity,
                price=product.base_price,
                product_image=product.main_image
            )

        final_items.append(new_item)
        subtotal += new_item.price * new_item.quantity

    # Calcular envío
    shipping_method_id = order_in.shipping_method_id or "standard_ss"
    shipping_cost, shipping_method_name = calculate_shipping_cost(shipping_method_id, subtotal)

    # Aplicar cupón si se proporciona
    discount_amount = 0.0
    coupon_code = None
    coupon_discount_type = None
    coupon_discount_value = None

    if order_in.coupon_code:
        coupon = await Coupon.find_one(Coupon.code == order_in.coupon_code.upper().strip())

        if coupon:
            is_valid, error_msg = coupon.is_valid()

            if is_valid:
                if not coupon.minimum_amount or subtotal >= coupon.minimum_amount:
                    discount_amount = coupon.calculate_discount(subtotal)
                    coupon_code = coupon.code
                    coupon_discount_type = coupon.discount_type.value
                    coupon_discount_value = coupon.discount_value

                    # Incrementar uso del cupón
                    coupon.current_uses += 1
                    await coupon.save()

    # Calcular total
    total_amount = subtotal - discount_amount + shipping_cost

    # Actualizar stock de forma atómica
    for item_in in order_in.items:
        product = await Product.get(item_in.product_id)

        if product.has_variants and item_in.variant_sku:
            # Actualizar stock de variante
            for i, v in enumerate(product.variants):
                if v.sku == item_in.variant_sku:
                    product.variants[i].stock -= item_in.quantity
                    break
            await product.save()
        else:
            # Actualización atómica para producto simple
            result = await Product.find_one(
                Product.id == item_in.product_id,
                Product.stock >= item_in.quantity
            ).update({"$inc": {"stock": -item_in.quantity}})

            if not result:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El stock cambió durante la transacción. Por favor, intenta de nuevo."
                )

    # Estimar fecha de entrega
    shipping_method = get_shipping_method(shipping_method_id)
    estimated_delivery = None
    if shipping_method:
        estimated_delivery = datetime.now(timezone.utc) + timedelta(days=shipping_method.estimated_days_max)

    # Crear orden
    new_order = Order(
        user_id=current_user.id,
        user_email=current_user.email,
        items=final_items,
        subtotal=round(subtotal, 2),
        discount_amount=round(discount_amount, 2),
        shipping_cost=round(shipping_cost, 2),
        total_amount=round(total_amount, 2),
        coupon_code=coupon_code,
        coupon_discount_type=coupon_discount_type,
        coupon_discount_value=coupon_discount_value,
        shipping_address=final_address,
        shipping_method_id=shipping_method_id,
        shipping_method_name=shipping_method_name,
        estimated_delivery=estimated_delivery,
        customer_notes=order_in.customer_notes,
        status=OrderStatus.PENDING
    )

    # Agregar evento inicial de tracking
    new_order.add_tracking_event(
        status=OrderStatus.PENDING,
        notes="Orden creada, pendiente de pago",
        updated_by="system"
    )

    await new_order.create()

    # Enviar email de confirmación de orden en background
    background_tasks.add_task(
        email_service.send_order_confirmation,
        new_order,
        current_user.first_name
    )

    return new_order


@router.post("/{order_id}/payment-link", response_model=PaymentLinkResponse)
async def create_payment_link(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Crea un link de pago de Wompi para una orden pendiente.
    """
    order = await Order.get(order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )

    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para esta orden"
        )

    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La orden no está pendiente de pago. Estado actual: {order.status.value}"
        )

    # Convertir a centavos
    amount_in_cents = int(order.total_amount * 100)

    try:
        result = await wompi_service.create_payment_link(
            order_id=str(order.id),
            amount_in_cents=amount_in_cents,
            currency="USD",
            customer_email=order.user_email,
            reference=str(order.id)
        )

        # Guardar link en la orden
        order.wompi_payment_link = result["payment_link"]
        order.payment_method = PaymentMethod.WOMPI_CARD
        await order.save()

        return PaymentLinkResponse(
            order_id=str(order.id),
            payment_link=result["payment_link"],
            expires_at=result.get("expires_at")
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear link de pago: {str(e)}"
        )


@router.get("/me", response_model=List[OrderResponse])
async def get_my_orders(
    current_user: User = Depends(get_current_user),
    status_filter: Optional[OrderStatus] = Query(None, description="Filtrar por estado"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50)
):
    """
    Obtiene las órdenes del usuario actual.
    """
    query = Order.find(Order.user_id == current_user.id)

    if status_filter:
        query = Order.find(
            Order.user_id == current_user.id,
            Order.status == status_filter
        )

    orders = await query.sort(-Order.created_at).skip(skip).limit(limit).to_list()

    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene los detalles de una orden específica.
    """
    order = await Order.get(order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )

    # Solo el dueño o admin puede ver la orden
    if order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver esta orden"
        )

    return order


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Cancela una orden pendiente y restaura el stock.
    """
    order = await Order.get(order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )

    if order.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para cancelar esta orden"
        )

    if order.status not in [OrderStatus.PENDING, OrderStatus.FAILED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden cancelar órdenes pendientes o fallidas"
        )

    # Restaurar stock
    for item in order.items:
        product = await Product.get(item.product_id)
        if product:
            if item.variant_sku and product.has_variants:
                for i, v in enumerate(product.variants):
                    if v.sku == item.variant_sku:
                        product.variants[i].stock += item.quantity
                        break
                await product.save()
            else:
                await Product.find_one(Product.id == item.product_id).update(
                    {"$inc": {"stock": item.quantity}}
                )

    # Restaurar uso de cupón si se usó
    if order.coupon_code:
        coupon = await Coupon.find_one(Coupon.code == order.coupon_code)
        if coupon and coupon.current_uses > 0:
            coupon.current_uses -= 1
            await coupon.save()

    order.add_tracking_event(
        status=OrderStatus.CANCELLED,
        notes="Orden cancelada por el usuario",
        updated_by=current_user.email
    )

    await order.save()

    return order


# ==================== ENDPOINTS DE ADMIN ====================

@router.get("/", response_model=List[OrderResponse])
async def get_all_orders(
    status_filter: Optional[OrderStatus] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    limit: int = Query(20, ge=1, le=100),
    skip: int = Query(0, ge=0)
):
    """
    Obtiene todas las órdenes (solo admin).
    """
    query = Order.find()

    if status_filter:
        query = Order.find(Order.status == status_filter)

    orders = await query.sort(-Order.created_at).skip(skip).limit(limit).to_list()

    return orders


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Actualiza el estado de una orden (solo admin).
    """
    order = await Order.get(order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )

    old_status = order.status

    order.add_tracking_event(
        status=status_update.status,
        location=status_update.location,
        notes=status_update.notes,
        updated_by=current_user.email
    )

    await order.save()

    # Enviar notificación de envío si cambió a SHIPPED
    if status_update.status == OrderStatus.SHIPPED and old_status != OrderStatus.SHIPPED:
        user = await User.get(order.user_id)
        if user:
            background_tasks.add_task(
                email_service.send_shipping_notification,
                order,
                user.first_name,
                None  # tracking_url
            )

    return order


@router.patch("/{order_id}/shipping", response_model=OrderResponse)
async def update_shipping_info(
    order_id: str,
    shipping_update: ShippingUpdate,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Actualiza información de envío de una orden (solo admin).
    """
    order = await Order.get(order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )

    if shipping_update.tracking_number:
        order.tracking_number = shipping_update.tracking_number
    if shipping_update.carrier:
        order.carrier = shipping_update.carrier
    if shipping_update.estimated_delivery:
        order.estimated_delivery = shipping_update.estimated_delivery

    order.updated_at = datetime.now(timezone.utc)
    await order.save()

    return order


@router.post("/{order_id}/refund", response_model=OrderResponse)
async def refund_order(
    order_id: str,
    notes: str = Query(..., description="Razón del reembolso"),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Marca una orden como reembolsada y restaura el stock (solo admin).
    """
    order = await Order.get(order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Orden no encontrada"
        )

    if order.status == OrderStatus.REFUNDED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La orden ya fue reembolsada"
        )

    # Restaurar stock
    for item in order.items:
        product = await Product.get(item.product_id)
        if product:
            if item.variant_sku and product.has_variants:
                for i, v in enumerate(product.variants):
                    if v.sku == item.variant_sku:
                        product.variants[i].stock += item.quantity
                        break
                await product.save()
            else:
                await Product.find_one(Product.id == item.product_id).update(
                    {"$inc": {"stock": item.quantity}}
                )

    order.add_tracking_event(
        status=OrderStatus.REFUNDED,
        notes=f"Reembolso: {notes}",
        updated_by=current_user.email
    )

    await order.save()

    return order


@router.get("/stats/summary")
async def get_orders_summary(
    current_user: User = Depends(get_current_admin_user)
):
    """
    Obtiene estadísticas de órdenes (solo admin).
    """
    total_orders = await Order.count()
    pending_orders = await Order.find(Order.status == OrderStatus.PENDING).count()
    paid_orders = await Order.find(Order.status == OrderStatus.PAID).count()
    shipped_orders = await Order.find(Order.status == OrderStatus.SHIPPED).count()
    delivered_orders = await Order.find(Order.status == OrderStatus.DELIVERED).count()

    # Calcular ingresos totales (solo órdenes pagadas/entregadas)
    paid_and_delivered = await Order.find(
        {"status": {"$in": [OrderStatus.PAID.value, OrderStatus.DELIVERED.value, OrderStatus.SHIPPED.value]}}
    ).to_list()

    total_revenue = sum(o.total_amount for o in paid_and_delivered)

    return {
        "total_orders": total_orders,
        "pending": pending_orders,
        "paid": paid_orders,
        "shipped": shipped_orders,
        "delivered": delivered_orders,
        "total_revenue": round(total_revenue, 2)
    }
