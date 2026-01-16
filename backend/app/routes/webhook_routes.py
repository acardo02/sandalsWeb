"""
Rutas para webhooks externos (Wompi, etc.)
"""
from fastapi import APIRouter, Request, Header, HTTPException, status, BackgroundTasks
from datetime import datetime, timezone
import logging

from app.models.orders_model import Order, OrderStatus
from app.models.user_model import User
from app.services.wompi_service import wompi_service
from app.services.email_service import email_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/wompi")
async def wompi_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_signature: str = Header(None, alias="x-signature")
):
    """
    Webhook para recibir notificaciones de Wompi cuando un pago es completado.

    Wompi envía eventos como:
    - transaction.updated: Cuando el estado de una transacción cambia
    - payment_link.closed: Cuando un link de pago es usado/cerrado
    """
    try:
        payload = await request.json()

        logger.info(f"Wompi webhook received: {payload.get('event')}")

        # Verificar firma de seguridad (si está disponible)
        if x_signature:
            if not wompi_service.verify_webhook_signature(payload, x_signature):
                logger.warning("Invalid webhook signature")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Firma inválida"
                )

        # Extraer datos del evento
        event_type = payload.get("event")
        event_data = payload.get("data", {})
        transaction_data = event_data.get("transaction", {})

        transaction_id = transaction_data.get("id")
        transaction_status = transaction_data.get("status")
        reference = transaction_data.get("reference")  # Este es el order_id

        if not reference:
            logger.warning("No reference found in webhook payload")
            return {"received": True, "processed": False}

        # Buscar la orden por referencia (el reference es el order_id como string)
        order = await Order.get(reference)

        if not order:
            # Intentar buscar por wompi_transaction_id si ya se guardó
            order = await Order.find_one(Order.wompi_transaction_id == transaction_id)

        if not order:
            logger.warning(f"Order not found for reference: {reference}")
            return {"received": True, "processed": False, "reason": "Order not found"}

        # Procesar según el estado de la transacción
        if transaction_status == "APPROVED":
            await process_approved_payment(order, transaction_id, transaction_data, background_tasks)

        elif transaction_status == "DECLINED":
            await process_declined_payment(order, transaction_id, transaction_data)

        elif transaction_status == "VOIDED":
            await process_voided_payment(order, transaction_id, transaction_data)

        elif transaction_status == "ERROR":
            await process_failed_payment(order, transaction_id, transaction_data)

        return {"received": True, "processed": True}

    except Exception as e:
        logger.error(f"Error processing Wompi webhook: {str(e)}")
        # Siempre retornar 200 para que Wompi no reintente
        return {"received": True, "error": str(e)}


async def process_approved_payment(
    order: Order,
    transaction_id: str,
    transaction_data: dict,
    background_tasks: BackgroundTasks
):
    """Procesa un pago aprobado"""
    if order.status in [OrderStatus.PAID, OrderStatus.PROCESSING, OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
        logger.info(f"Order {order.id} already processed, skipping")
        return

    order.status = OrderStatus.PAID
    order.wompi_transaction_id = transaction_id
    order.paid_at = datetime.now(timezone.utc)

    # Agregar evento de tracking
    order.add_tracking_event(
        status=OrderStatus.PAID,
        notes=f"Pago confirmado vía Wompi (ID: {transaction_id})",
        updated_by="wompi_webhook"
    )

    await order.save()
    logger.info(f"Order {order.id} marked as PAID")

    # Enviar email de confirmación de pago en background
    user = await User.get(order.user_id)
    if user:
        background_tasks.add_task(
            email_service.send_payment_confirmation,
            order,
            user.first_name
        )


async def process_declined_payment(
    order: Order,
    transaction_id: str,
    transaction_data: dict
):
    """Procesa un pago rechazado"""
    if order.status != OrderStatus.PENDING:
        return

    decline_reason = transaction_data.get("status_message", "Pago rechazado")

    order.add_tracking_event(
        status=OrderStatus.FAILED,
        notes=f"Pago rechazado: {decline_reason} (ID: {transaction_id})",
        updated_by="wompi_webhook"
    )

    order.status = OrderStatus.FAILED
    await order.save()
    logger.info(f"Order {order.id} marked as FAILED (declined)")


async def process_voided_payment(
    order: Order,
    transaction_id: str,
    transaction_data: dict
):
    """Procesa un pago anulado"""
    order.add_tracking_event(
        status=OrderStatus.CANCELLED,
        notes=f"Pago anulado (ID: {transaction_id})",
        updated_by="wompi_webhook"
    )

    order.status = OrderStatus.CANCELLED
    await order.save()
    logger.info(f"Order {order.id} marked as CANCELLED (voided)")


async def process_failed_payment(
    order: Order,
    transaction_id: str,
    transaction_data: dict
):
    """Procesa un pago fallido"""
    if order.status != OrderStatus.PENDING:
        return

    error_message = transaction_data.get("status_message", "Error en el pago")

    order.add_tracking_event(
        status=OrderStatus.FAILED,
        notes=f"Error en el pago: {error_message} (ID: {transaction_id})",
        updated_by="wompi_webhook"
    )

    order.status = OrderStatus.FAILED
    await order.save()
    logger.info(f"Order {order.id} marked as FAILED (error)")


@router.get("/wompi/test")
async def test_webhook():
    """
    Endpoint de prueba para verificar que el webhook está funcionando.
    """
    return {
        "status": "ok",
        "message": "Wompi webhook endpoint is active",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
