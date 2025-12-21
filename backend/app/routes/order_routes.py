from fastapi import HTTPException, APIRouter, status, Depends
from typing import List, Optional
from beanie import PydanticObjectId

from app.models.user_model import User
from app.models.product_model import Product
from app.models.orders_model import Order, OrderItem, OrderStatus
from app.schemas.order_schema import OrderCreate, OrderResponse, OrderStatusUpdate
from app.core.dependencies import get_current_user, get_current_admin_user

router = APIRouter()

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def creat_order(
    order_in: OrderCreate,
    current_user: User = Depends(get_current_user)
):
    final_items = []
    total_amount = 0.0

    for item_in in order_in.items:
        product = await Product.get(item_in.product_id)
        
        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Producto con ID: {item_in.product_id} no encotrado"
            )
        
        if product.stock < item_in.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"No hay suficiente stock para '{product.name}'. Disponibles: {product.stock}"
            )
        
        if order_in.shipping_address:
            final_address = order_in.shipping_address
        elif current_user.address:
            final_address = current_user.address
        else:
            raise HTTPException(
                status_code=400,
                detail="Se requiere una dirección de envío. Agrégala a tu perfil o envíala en la orden."
            )
        
        new_item = OrderItem(
            product_id=product.id,
            product_name=product.name,
            quantity=item_in.quantity,
            price=product.price
        )

        final_items.append(new_item)
        total_amount += item_in.quantity * product.price

        product.stock -= item_in.quantity

        
        await product.save()
    
    new_order = Order(
        user_id=current_user.id,
        items=final_items,
        total_amount=round(total_amount, 2),
        status=OrderStatus.PENDING,
        shipping_address=final_address
    )

    await new_order.create()

    return new_order

@router.get("/me", response_model=List[OrderResponse])
async def get_my_orders(current_user: User = Depends(get_current_user)):
    orders = await Order.find(
        Order.user_id == current_user.id
    ).sort(-Order.created_at).to_list()

    return orders

@router.get("/", response_model=List[OrderResponse])
async def get_all_orders(
    status: Optional[OrderStatus] = None,
    current_user: User = Depends(get_current_admin_user),
    limit: int = 20,
    skip: int = 0
):
    if status:
        orders = await Order.find(
            Order.status == status
        ).sort(-Order.created_at).skip(skip).limit(limit).to_list()
    else:
        orders = await Order.find_all().sort(-Order.created_at).skip(skip).limit(limit).to_list()

    return orders

@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(get_current_admin_user)
):
    order = await Order.get(order_id)
    if not order:
        raise HTTPException(
            status_code=404,
            detail="Orden no encontrada"
        )
    
    order.status = status_update.status
    await order.save()

    return order