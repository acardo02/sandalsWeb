"""
Servicio de integración con Wompi (Pasarela de pagos)
Documentación: https://docs.wompi.co/
"""
import httpx
import hashlib
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from app.core.config import settings

logger = logging.getLogger(__name__)


class WompiService:
    """Servicio para integración con Wompi API"""

    def __init__(self):
        self.base_url = "https://production.wompi.co/v1"  # Cambiar a sandbox para testing
        self.public_key = settings.WOMPI_PUBLIC_KEY
        self.private_key = settings.WOMPI_PRIVATE_KEY
        self.events_secret = settings.WOMPI_EVENTS_SECRET

    async def create_payment_link(
        self,
        order_id: str,
        amount_in_cents: int,
        currency: str = "USD",
        customer_email: str = "",
        reference: str = ""
    ) -> Dict[str, Any]:
        """
        Crea un enlace de pago en Wompi

        Args:
            order_id: ID de la orden
            amount_in_cents: Monto en centavos (ej: 2500 = $25.00)
            currency: Moneda (USD, CRC)
            customer_email: Email del cliente
            reference: Referencia adicional

        Returns:
            {
                "payment_link": "https://checkout.wompi.co/l/xxx",
                "transaction_id": "xxx-xxx-xxx"
            }
        """
        try:
            # Generar signature de integridad
            integrity_signature = self._generate_integrity_signature(
                order_id, amount_in_cents, currency
            )

            payload = {
                "name": f"Orden #{order_id}",
                "description": f"Pago de orden {order_id}",
                "single_use": True,  # Link de un solo uso
                "collect_shipping": False,  # Ya tenemos la dirección
                "currency": currency,
                "amount_in_cents": amount_in_cents,
                "redirect_url": f"{settings.FRONTEND_URL}/orden-confirmada?order_id={order_id}",
                "sku": order_id,
                "reference": reference or order_id,
                "customer_data": {
                    "email": customer_email,
                    "full_name": customer_email.split("@")[0]  # Provisional
                }
            }

            headers = {
                "Authorization": f"Bearer {self.public_key}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/payment_links",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )

                if response.status_code == 201:
                    data = response.json()
                    logger.info(f"Payment link created for order {order_id}: {data.get('data', {}).get('id')}")

                    return {
                        "payment_link": data["data"]["permalink"],
                        "transaction_id": data["data"]["id"],
                        "expires_at": data["data"]["expires_at"]
                    }
                else:
                    logger.error(f"Wompi API error: {response.status_code} - {response.text}")
                    raise Exception(f"Error creating payment link: {response.text}")

        except Exception as e:
            logger.error(f"Error creating Wompi payment link: {str(e)}")
            raise

    async def verify_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """
        Verifica el estado de una transacción en Wompi

        Returns:
            {
                "status": "APPROVED" | "DECLINED" | "PENDING",
                "transaction_id": "xxx",
                "amount": 2500,
                "currency": "USD",
                "payment_method": "CARD",
                "created_at": "2026-01-13T..."
            }
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.private_key}"
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/transactions/{transaction_id}",
                    headers=headers,
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()["data"]

                    return {
                        "status": data["status"],
                        "transaction_id": data["id"],
                        "amount": data["amount_in_cents"],
                        "currency": data["currency"],
                        "payment_method": data.get("payment_method_type"),
                        "created_at": data["created_at"],
                        "finalized_at": data.get("finalized_at")
                    }
                else:
                    logger.error(f"Error verifying transaction: {response.status_code}")
                    raise Exception(f"Error verifying transaction: {response.text}")

        except Exception as e:
            logger.error(f"Error verifying Wompi transaction: {str(e)}")
            raise

    def verify_webhook_signature(self, payload: Dict[str, Any], signature: str) -> bool:
        """
        Verifica la firma de un webhook de Wompi para seguridad

        Args:
            payload: Datos del webhook
            signature: Firma recibida en el header

        Returns:
            True si la firma es válida
        """
        try:
            # Construir el mensaje para verificar
            event_data = payload.get("data", {})
            transaction_id = event_data.get("transaction", {}).get("id", "")
            timestamp = payload.get("timestamp", "")

            message = f"{transaction_id}{timestamp}{self.events_secret}"

            # Calcular el hash SHA256
            calculated_signature = hashlib.sha256(message.encode()).hexdigest()

            return calculated_signature == signature

        except Exception as e:
            logger.error(f"Error verifying webhook signature: {str(e)}")
            return False

    def _generate_integrity_signature(
        self,
        reference: str,
        amount_in_cents: int,
        currency: str
    ) -> str:
        """
        Genera la firma de integridad para validar pagos

        Wompi usa esto para verificar que el monto no fue manipulado
        """
        message = f"{reference}{amount_in_cents}{currency}{self.events_secret}"
        return hashlib.sha256(message.encode()).hexdigest()


# Instancia global
wompi_service = WompiService()
