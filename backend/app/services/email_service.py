"""
Servicio de envío de emails usando SendGrid
"""
import logging
from typing import Optional, List, Dict
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from app.core.config import settings
from app.models.orders_model import Order, OrderItem

logger = logging.getLogger(__name__)


class EmailService:
    """Servicio para envío de emails transaccionales"""

    def __init__(self):
        self.api_key = settings.SENDGRID_API_KEY
        self.from_email = settings.EMAIL_FROM
        self.from_name = settings.EMAIL_FROM_NAME
        self.sg = SendGridAPIClient(self.api_key) if self.api_key else None

    async def send_order_confirmation(self, order: Order, user_name: str) -> bool:
        """
        Envía email de confirmación de orden creada
        """
        try:
            subject = f"Confirmación de Orden #{order.id}"

            html_content = self._render_order_confirmation(order, user_name)

            return await self._send_email(
                to_email=order.user_email,
                subject=subject,
                html_content=html_content
            )

        except Exception as e:
            logger.error(f"Error sending order confirmation: {str(e)}")
            return False

    async def send_payment_confirmation(self, order: Order, user_name: str) -> bool:
        """
        Envía email de confirmación de pago recibido
        """
        try:
            subject = f"¡Pago Confirmado! - Orden #{order.id}"

            html_content = self._render_payment_confirmation(order, user_name)

            return await self._send_email(
                to_email=order.user_email,
                subject=subject,
                html_content=html_content
            )

        except Exception as e:
            logger.error(f"Error sending payment confirmation: {str(e)}")
            return False

    async def send_shipping_notification(
        self,
        order: Order,
        user_name: str,
        tracking_url: Optional[str] = None
    ) -> bool:
        """
        Envía email cuando la orden es enviada
        """
        try:
            subject = f"Tu Orden ha sido Enviada - #{order.id}"

            html_content = self._render_shipping_notification(order, user_name, tracking_url)

            return await self._send_email(
                to_email=order.user_email,
                subject=subject,
                html_content=html_content
            )

        except Exception as e:
            logger.error(f"Error sending shipping notification: {str(e)}")
            return False

    async def send_welcome_email(self, email: str, name: str) -> bool:
        """
        Envía email de bienvenida a nuevo usuario
        """
        try:
            subject = f"¡Bienvenido a {settings.PROJECT_NAME}!"

            html_content = self._render_welcome_email(name)

            return await self._send_email(
                to_email=email,
                subject=subject,
                html_content=html_content
            )

        except Exception as e:
            logger.error(f"Error sending welcome email: {str(e)}")
            return False

    async def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        cc: Optional[List[str]] = None
    ) -> bool:
        """Envía un email usando SendGrid"""
        if not self.sg:
            logger.warning("SendGrid not configured, email not sent")
            return False

        try:
            message = Mail(
                from_email=Email(self.from_email, self.from_name),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content)
            )

            if cc:
                message.add_cc(cc)

            response = self.sg.send(message)

            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"SendGrid error: {response.status_code} - {response.body}")
                return False

        except Exception as e:
            logger.error(f"Error sending email via SendGrid: {str(e)}")
            return False

    def _render_order_confirmation(self, order: Order, user_name: str) -> str:
        """Renderiza el HTML del email de confirmación de orden"""
        items_html = ""
        for item in order.items:
            variant_info = f" ({item.variant_info})" if item.variant_info else ""
            items_html += f"""
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #eee;">
                    {item.product_name}{variant_info}
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: center;">
                    {item.quantity}
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">
                    ${item.price:.2f}
                </td>
                <td style="padding: 10px; border-bottom: 1px solid #eee; text-align: right;">
                    ${item.subtotal:.2f}
                </td>
            </tr>
            """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #000; color: #fff; padding: 20px; text-align: center;">
                <h1 style="margin: 0;">CALERO</h1>
            </div>

            <div style="padding: 30px; background: #f9f9f9;">
                <h2>¡Gracias por tu orden, {user_name}!</h2>
                <p>Hemos recibido tu orden <strong>#{order.id}</strong> y está siendo procesada.</p>

                <div style="background: #fff; padding: 20px; margin: 20px 0; border-radius: 5px;">
                    <h3>Resumen de Orden</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <thead>
                            <tr style="background: #f0f0f0;">
                                <th style="padding: 10px; text-align: left;">Producto</th>
                                <th style="padding: 10px; text-align: center;">Cantidad</th>
                                <th style="padding: 10px; text-align: right;">Precio</th>
                                <th style="padding: 10px; text-align: right;">Subtotal</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                    </table>

                    <div style="margin-top: 20px; padding-top: 10px; border-top: 2px solid #000;">
                        <table style="width: 100%;">
                            <tr>
                                <td style="text-align: right; padding: 5px;"><strong>Subtotal:</strong></td>
                                <td style="text-align: right; padding: 5px;">${order.subtotal:.2f}</td>
                            </tr>
                            {f'''<tr>
                                <td style="text-align: right; padding: 5px;"><strong>Descuento:</strong></td>
                                <td style="text-align: right; padding: 5px; color: green;">-${order.discount_amount:.2f}</td>
                            </tr>''' if order.discount_amount > 0 else ''}
                            <tr>
                                <td style="text-align: right; padding: 5px;"><strong>Envío:</strong></td>
                                <td style="text-align: right; padding: 5px;">${order.shipping_cost:.2f}</td>
                            </tr>
                            <tr style="font-size: 1.2em;">
                                <td style="text-align: right; padding: 10px;"><strong>TOTAL:</strong></td>
                                <td style="text-align: right; padding: 10px;"><strong>${order.total_amount:.2f}</strong></td>
                            </tr>
                        </table>
                    </div>
                </div>

                <div style="background: #fff; padding: 20px; margin: 20px 0; border-radius: 5px;">
                    <h3>Dirección de Envío</h3>
                    <p>
                        {order.shipping_address.street}<br>
                        {order.shipping_address.city}, {order.shipping_address.state}<br>
                        {order.shipping_address.country} {order.shipping_address.zip_code or ''}
                    </p>
                </div>

                <p style="text-align: center; margin-top: 30px;">
                    <a href="{settings.FRONTEND_URL}/mi-cuenta/ordenes/{order.id}"
                       style="background: #000; color: #fff; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Ver Estado de Orden
                    </a>
                </p>
            </div>

            <div style="text-align: center; padding: 20px; color: #666; font-size: 0.9em;">
                <p>Si tienes alguna pregunta, contáctanos respondiendo a este email.</p>
                <p>&copy; 2026 CALERO. Todos los derechos reservados.</p>
            </div>
        </body>
        </html>
        """

    def _render_payment_confirmation(self, order: Order, user_name: str) -> str:
        """Renderiza el HTML del email de confirmación de pago"""
        return f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #4CAF50; color: #fff; padding: 20px; text-align: center;">
                <h1 style="margin: 0;">✓ ¡Pago Confirmado!</h1>
            </div>

            <div style="padding: 30px; background: #f9f9f9;">
                <h2>Hola {user_name},</h2>
                <p>¡Excelentes noticias! Tu pago ha sido confirmado exitosamente.</p>

                <div style="background: #fff; padding: 20px; margin: 20px 0; border-radius: 5px; text-align: center;">
                    <h3>Orden #{order.id}</h3>
                    <p style="font-size: 1.5em; color: #4CAF50; margin: 20px 0;">
                        <strong>${order.total_amount:.2f}</strong>
                    </p>
                    <p>Estado: <strong style="color: #4CAF50;">PAGADO</strong></p>
                </div>

                <p>Tu orden está siendo preparada para envío. Te notificaremos cuando sea despachada.</p>

                <p style="text-align: center; margin-top: 30px;">
                    <a href="{settings.FRONTEND_URL}/mi-cuenta/ordenes/{order.id}"
                       style="background: #000; color: #fff; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Ver Detalles de Orden
                    </a>
                </p>
            </div>
        </body>
        </html>
        """

    def _render_shipping_notification(
        self,
        order: Order,
        user_name: str,
        tracking_url: Optional[str]
    ) -> str:
        """Renderiza el HTML del email de notificación de envío"""
        tracking_section = ""
        if order.tracking_number:
            tracking_section = f"""
            <div style="background: #fff; padding: 20px; margin: 20px 0; border-radius: 5px; text-align: center;">
                <h3>Número de Rastreo</h3>
                <p style="font-size: 1.3em; font-family: monospace; background: #f0f0f0; padding: 10px;">
                    {order.tracking_number}
                </p>
                {f'<a href="{tracking_url}" style="color: #007bff;">Rastrear Envío</a>' if tracking_url else ''}
            </div>
            """

        return f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #2196F3; color: #fff; padding: 20px; text-align: center;">
                <h1 style="margin: 0;">📦 ¡Tu Orden está en Camino!</h1>
            </div>

            <div style="padding: 30px; background: #f9f9f9;">
                <h2>Hola {user_name},</h2>
                <p>¡Buenas noticias! Tu orden <strong>#{order.id}</strong> ha sido enviada.</p>

                {tracking_section}

                <div style="background: #fff; padding: 20px; margin: 20px 0; border-radius: 5px;">
                    <h3>Información de Envío</h3>
                    <p><strong>Transportista:</strong> {order.carrier or 'Por confirmar'}</p>
                    <p><strong>Método:</strong> {order.shipping_method_name or 'Estándar'}</p>
                    {f'<p><strong>Entrega Estimada:</strong> {order.estimated_delivery.strftime("%d %b %Y")}</p>' if order.estimated_delivery else ''}
                </div>

                <p style="text-align: center; margin-top: 30px;">
                    <a href="{settings.FRONTEND_URL}/mi-cuenta/ordenes/{order.id}"
                       style="background: #000; color: #fff; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Ver Estado de Envío
                    </a>
                </p>
            </div>
        </body>
        </html>
        """

    def _render_welcome_email(self, name: str) -> str:
        """Renderiza el HTML del email de bienvenida"""
        return f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #000; color: #fff; padding: 30px; text-align: center;">
                <h1 style="margin: 0; font-size: 2.5em;">CALERO</h1>
                <p style="margin: 10px 0 0 0;">Productos Artesanales</p>
            </div>

            <div style="padding: 30px; background: #f9f9f9;">
                <h2>¡Bienvenido, {name}!</h2>
                <p>Gracias por unirte a la familia CALERO. Estamos emocionados de tenerte con nosotros.</p>

                <p>En CALERO encontrarás productos artesanales de la más alta calidad, hechos con amor y dedicación.</p>

                <div style="background: #fff; padding: 20px; margin: 20px 0; border-radius: 5px;">
                    <h3>¿Qué sigue?</h3>
                    <ul style="line-height: 2;">
                        <li>Explora nuestro catálogo de productos</li>
                        <li>Agrega tus favoritos a la wishlist</li>
                        <li>Disfruta de envíos gratis en compras sobre $50</li>
                    </ul>
                </div>

                <p style="text-align: center; margin-top: 30px;">
                    <a href="{settings.FRONTEND_URL}/productos"
                       style="background: #000; color: #fff; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Comenzar a Comprar
                    </a>
                </p>
            </div>

            <div style="text-align: center; padding: 20px; color: #666; font-size: 0.9em;">
                <p>&copy; 2026 CALERO. Todos los derechos reservados.</p>
            </div>
        </body>
        </html>
        """


# Instancia global
email_service = EmailService()
