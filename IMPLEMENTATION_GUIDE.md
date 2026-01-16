# 🛍️ GUÍA DE IMPLEMENTACIÓN COMPLETA - E-COMMERCE SANDALS WEB

## 📊 ESTADO ACTUAL DE LA IMPLEMENTACIÓN

### ✅ COMPLETADO (Backend)

#### 1. Modelos de Base de Datos
- ✅ **Product** - Con variantes (tallas/colores), múltiples imágenes, reviews
- ✅ **ProductVariant** - Sistema completo de variantes con SKU, stock individual
- ✅ **Order** - Rediseñado con tracking, shipping, cupones, pagos
- ✅ **OrderItem** - Con soporte para variantes
- ✅ **TrackingEvent** - Historial de tracking de órdenes
- ✅ **Coupon** - Sistema completo de cupones/descuentos
- ✅ **ProductReview** - Reviews con compra verificada
- ✅ **Wishlist** - Lista de deseos por usuario
- ✅ **ShippingMethod** - Métodos de envío
- ✅ **ShippingZone** - Zonas de envío

#### 2. Servicios
- ✅ **WompiService** - Integración completa con Wompi para pagos
  - Crear payment links
  - Verificar transacciones
  - Validar webhooks
- ✅ **EmailService** - Emails transaccionales con SendGrid
  - Confirmación de orden
  - Confirmación de pago
  - Notificación de envío
  - Email de bienvenida

#### 3. Configuración
- ✅ Variables de entorno para Wompi
- ✅ Variables de entorno para SendGrid
- ✅ Requirements.txt actualizado con sendgrid
- ✅ Database connection con todos los modelos

---

## 🔄 EN PROGRESO / FALTA IMPLEMENTAR

### Backend - Rutas y Schemas

#### 1. Schemas de Producto (PRIORIDAD ALTA)
Ubicación: `backend/app/schemas/product_schema.py`

```python
# CREAR/ACTUALIZAR estos schemas:

from pydantic import BaseModel, Field
from typing import Optional, List
from app.models.product_model import ProductVariant

class ProductVariantSchema(BaseModel):
    sku: str
    size: Optional[str]
    color: Optional[str]
    color_hex: Optional[str]
    price_adjustment: float = 0
    stock: int = 0
    image_url: Optional[str]
    is_available: bool = True

class ProductCreate(BaseModel):
    name: str
    description: Optional[str]
    category: str
    base_price: float
    has_variants: bool = False
    variants: List[ProductVariantSchema] = []
    sku: Optional[str]  # Para productos simples
    stock: Optional[int]  # Para productos simples
    images: List[str] = []
    tags: List[str] = []
    is_featured: bool = False

class ProductUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    category: Optional[str]
    base_price: Optional[float]
    variants: Optional[List[ProductVariantSchema]]
    images: Optional[List[str]]
    tags: Optional[List[str]]
    is_featured: Optional[bool]
    is_active: Optional[bool]

class ProductResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    category: str
    base_price: float
    has_variants: bool
    variants: List[ProductVariantSchema]
    sku: Optional[str]
    stock: Optional[int]
    images: List[str]
    main_image: Optional[str]
    tags: List[str]
    average_rating: float
    review_count: int
    is_featured: bool
    is_active: bool
    created_at: datetime

    # Helpers
    total_stock: int
    price_range: tuple[float, float]
```

#### 2. Schemas de Orden (PRIORIDAD ALTA)
Ubicación: `backend/app/schemas/order_schema.py`

```python
# ACTUALIZAR para incluir:

class OrderItemInput(BaseModel):
    product_id: str
    variant_sku: Optional[str]  # NUEVO
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemInput]
    shipping_address: AddressSchema
    shipping_method_id: str  # NUEVO
    coupon_code: Optional[str]  # NUEVO
    customer_notes: Optional[str]

class TrackingEventResponse(BaseModel):
    status: OrderStatus
    timestamp: datetime
    location: Optional[str]
    notes: Optional[str]
    updated_by: Optional[str]

class OrderResponse(BaseModel):
    id: str
    user_email: str
    items: List[OrderItemSchema]
    subtotal: float
    discount_amount: float
    shipping_cost: float
    total_amount: float
    coupon_code: Optional[str]
    shipping_address: AddressSchema
    shipping_method_name: Optional[str]
    tracking_number: Optional[str]
    estimated_delivery: Optional[datetime]
    tracking_history: List[TrackingEventResponse]
    status: OrderStatus
    payment_method: Optional[PaymentMethod]
    created_at: datetime
```

#### 3. Rutas de Cupones (NUEVO)
Ubicación: `backend/app/routes/coupon_routes.py`

```python
# CREAR este archivo:

from fastapi import APIRouter, Depends, HTTPException, status
from app.models.coupon_model import Coupon
from app.core.dependencies import get_current_admin_user, get_current_user

router = APIRouter()

# ADMIN ENDPOINTS
@router.post("/", dependencies=[Depends(get_current_admin_user)])
async def create_coupon(...):
    """Crear cupón (solo admin)"""
    pass

@router.get("/", dependencies=[Depends(get_current_admin_user)])
async def list_coupons(...):
    """Listar todos los cupones (solo admin)"""
    pass

@router.patch("/{code}", dependencies=[Depends(get_current_admin_user)])
async def update_coupon(...):
    """Actualizar cupón (solo admin)"""
    pass

# PUBLIC ENDPOINT
@router.post("/validate")
async def validate_coupon(code: str, subtotal: float, current_user = Depends(get_current_user)):
    """Validar cupón y calcular descuento"""
    coupon = await Coupon.find_one(Coupon.code == code.upper())

    if not coupon:
        raise HTTPException(404, "Cupón no válido")

    is_valid, error = coupon.is_valid()
    if not is_valid:
        raise HTTPException(400, error)

    if coupon.minimum_amount and subtotal < coupon.minimum_amount:
        raise HTTPException(400, f"Compra mínima: ${coupon.minimum_amount}")

    discount = coupon.calculate_discount(subtotal)

    return {
        "valid": True,
        "code": coupon.code,
        "discount_type": coupon.discount_type,
        "discount_value": coupon.discount_value,
        "discount_amount": discount,
        "new_total": subtotal - discount
    }
```

#### 4. Rutas de Reviews (NUEVO)
Ubicación: `backend/app/routes/review_routes.py`

```python
# CREAR este archivo:

from fastapi import APIRouter, Depends, HTTPException
from app.models.review_model import ProductReview
from app.models.product_model import Product
from app.models.orders_model import Order

router = APIRouter()

@router.post("/")
async def create_review(
    product_id: str,
    order_id: str,
    rating: int,
    title: str,
    comment: str,
    current_user = Depends(get_current_user)
):
    """Crear review (solo si compró el producto)"""
    # Verificar que la orden existe y pertenece al usuario
    order = await Order.get(order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(403, "No autorizado")

    # Verificar que el producto está en la orden
    product_in_order = any(item.product_id == product_id for item in order.items)
    if not product_in_order:
        raise HTTPException(400, "Producto no está en la orden")

    # Crear review
    review = ProductReview(
        product_id=product_id,
        user_id=current_user.id,
        order_id=order_id,
        rating=rating,
        title=title,
        comment=comment,
        verified_purchase=True
    )

    await review.create()

    # Actualizar promedio del producto
    await update_product_rating(product_id)

    return review

@router.get("/product/{product_id}")
async def get_product_reviews(product_id: str, skip: int = 0, limit: int = 20):
    """Obtener reviews de un producto"""
    reviews = await ProductReview.find(
        ProductReview.product_id == product_id,
        ProductReview.is_approved == True
    ).sort(-ProductReview.created_at).skip(skip).limit(limit).to_list()

    return reviews

async def update_product_rating(product_id: str):
    """Actualiza el rating promedio de un producto"""
    reviews = await ProductReview.find(
        ProductReview.product_id == product_id,
        ProductReview.is_approved == True
    ).to_list()

    if reviews:
        avg_rating = sum(r.rating for r in reviews) / len(reviews)
        product = await Product.get(product_id)
        product.average_rating = round(avg_rating, 2)
        product.review_count = len(reviews)
        await product.save()
```

#### 5. Rutas de Wishlist (NUEVO)
Ubicación: `backend/app/routes/wishlist_routes.py`

```python
# CREAR este archivo:

from fastapi import APIRouter, Depends
from app.models.wishlist_model import Wishlist

router = APIRouter()

@router.get("/")
async def get_wishlist(current_user = Depends(get_current_user)):
    """Obtener wishlist del usuario"""
    wishlist = await Wishlist.find_one(Wishlist.user_id == current_user.id)

    if not wishlist:
        wishlist = Wishlist(user_id=current_user.id, products=[])
        await wishlist.create()

    return wishlist

@router.post("/add/{product_id}")
async def add_to_wishlist(product_id: str, current_user = Depends(get_current_user)):
    """Agregar producto a wishlist"""
    wishlist = await Wishlist.find_one(Wishlist.user_id == current_user.id)

    if not wishlist:
        wishlist = Wishlist(user_id=current_user.id, products=[product_id])
        await wishlist.create()
    elif product_id not in wishlist.products:
        wishlist.products.append(product_id)
        await wishlist.save()

    return {"success": True}

@router.delete("/remove/{product_id}")
async def remove_from_wishlist(product_id: str, current_user = Depends(get_current_user)):
    """Remover producto de wishlist"""
    wishlist = await Wishlist.find_one(Wishlist.user_id == current_user.id)

    if wishlist and product_id in wishlist.products:
        wishlist.products.remove(product_id)
        await wishlist.save()

    return {"success": True}
```

#### 6. Webhook de Wompi (CRÍTICO)
Ubicación: `backend/app/routes/webhook_routes.py`

```python
# CREAR este archivo:

from fastapi import APIRouter, Request, Header, HTTPException
from app.services.wompi_service import wompi_service
from app.services.email_service import email_service
from app.models.orders_model import Order, OrderStatus

router = APIRouter()

@router.post("/wompi")
async def wompi_webhook(
    request: Request,
    x_signature: str = Header(..., alias="x-signature")
):
    """
    Webhook para recibir notificaciones de Wompi cuando un pago es completado
    """
    payload = await request.json()

    # Verificar firma de seguridad
    if not wompi_service.verify_webhook_signature(payload, x_signature):
        raise HTTPException(401, "Firma inválida")

    # Extraer datos del evento
    event = payload.get("event")
    transaction_data = payload.get("data", {}).get("transaction", {})
    transaction_id = transaction_data.get("id")
    status = transaction_data.get("status")
    reference = transaction_data.get("reference")  # order_id

    # Buscar la orden
    order = await Order.find_one(Order.id == reference)
    if not order:
        return {"received": True}  # Ignorar si no existe

    # Actualizar orden según el estado del pago
    if status == "APPROVED" and order.status == OrderStatus.PENDING:
        order.status = OrderStatus.PAID
        order.wompi_transaction_id = transaction_id
        order.paid_at = datetime.now(timezone.utc)
        order.add_tracking_event(
            status=OrderStatus.PAID,
            notes=f"Pago confirmado vía Wompi (ID: {transaction_id})",
            updated_by="wompi_webhook"
        )

        await order.save()

        # Enviar email de confirmación
        user = await User.get(order.user_id)
        await email_service.send_payment_confirmation(order, user.first_name)

    elif status == "DECLINED" or status == "ERROR":
        order.status = OrderStatus.FAILED
        order.add_tracking_event(
            status=OrderStatus.FAILED,
            notes=f"Pago rechazado/fallido (ID: {transaction_id})",
            updated_by="wompi_webhook"
        )
        await order.save()

    return {"received": True}
```

---

## 🎯 SIGUIENTE PASO - ACTUALIZAR RUTAS EXISTENTES

### products_routes.py
- Actualizar para soportar variantes
- Agregar endpoint para obtener variantes disponibles
- Validar stock de variantes al crear/actualizar

### order_routes.py
- Integrar cálculo de shipping
- Aplicar cupones
- Crear payment link de Wompi
- Enviar email de confirmación
- Manejar variantes en items

---

## 📝 FRONTEND - LO QUE FALTA

### 1. Selector de Variantes en Producto
```svelte
<!-- producto/[id]/+page.svelte -->
<script>
  let selectedVariant = null;
  let selectedSize = null;
  let selectedColor = null;

  function selectVariant(size, color) {
    selectedVariant = product.variants.find(v =>
      v.size === size && v.color === color
    );
  }
</script>

<div class="variant-selector">
  <!-- Selector de talla -->
  <div class="sizes">
    {#each availableSizes as size}
      <button
        class:selected={selectedSize === size}
        on:click={() => selectedSize = size}
      >
        {size}
      </button>
    {/each}
  </div>

  <!-- Selector de color -->
  <div class="colors">
    {#each availableColors as color}
      <button
        class="color-swatch"
        style="background: {color.hex}"
        on:click={() => selectedColor = color}
      />
    {/each}
  </div>

  <p class="stock-info">
    {#if selectedVariant}
      {selectedVariant.stock} unidades disponibles
    {/if}
  </p>
</div>
```

### 2. Aplicar Cupón en Checkout
```svelte
<!-- checkout/+page.svelte -->
<script>
  let couponCode = '';
  let discount = 0;

  async function applyCoupon() {
    try {
      const response = await api.coupons.validate(couponCode, subtotal);
      discount = response.discount_amount;
      alert(`¡Cupón aplicado! Descuento: $${discount}`);
    } catch (error) {
      alert(error.message);
    }
  }
</script>

<div class="coupon-section">
  <input bind:value={couponCode} placeholder="Código de cupón" />
  <button on:click={applyCoupon}>Aplicar</button>
</div>
```

### 3. Tracking de Orden
```svelte
<!-- mi-cuenta/ordenes/[id]/+page.svelte -->
<script>
  export let data;
  const order = data.order;
</script>

<div class="tracking">
  <h2>Orden #{order.id}</h2>

  <div class="timeline">
    {#each order.tracking_history as event}
      <div class="event">
        <div class="status">{event.status}</div>
        <div class="date">{formatDate(event.timestamp)}</div>
        {#if event.location}
          <div class="location">{event.location}</div>
        {/if}
        {#if event.notes}
          <div class="notes">{event.notes}</div>
        {/if}
      </div>
    {/each}
  </div>

  {#if order.tracking_number}
    <div class="tracking-number">
      <strong>Tracking:</strong> {order.tracking_number}
    </div>
  {/if}
</div>
```

---

## 🚀 PLAN DE IMPLEMENTACIÓN RECOMENDADO

### Semana 1 (CRÍTICO)
1. ✅ Schemas de productos y órdenes
2. ✅ Actualizar products_routes.py
3. ✅ Actualizar order_routes.py con Wompi
4. ✅ Webhook de Wompi
5. ✅ Rutas de cupones

### Semana 2 (IMPORTANTE)
6. ✅ Rutas de reviews y wishlist
7. ✅ Frontend: Selector de variantes
8. ✅ Frontend: Sistema de cupones
9. ✅ Frontend: Página de tracking
10. ✅ Testing completo

### Semana 3 (POLISH)
11. ✅ Panel admin mejorado
12. ✅ Dashboard con métricas
13. ✅ Emails mejorados con templates
14. ✅ Optimizaciones de performance
15. ✅ Documentación completa

---

## 📌 NOTAS IMPORTANTES

### Configuración Requerida

1. **Wompi**: Obtener claves en https://dashboard.wompi.co/
2. **SendGrid**: Crear cuenta en https://sendgrid.com/
3. **MongoDB**: Actualizar índices al iniciar

### Variables de Entorno Críticas
```env
# Wompi
WOMPI_PUBLIC_KEY=pub_test_xxx
WOMPI_PRIVATE_KEY=prv_test_xxx
WOMPI_EVENTS_SECRET=test_xxx
WOMPI_ENV=sandbox

# SendGrid
SENDGRID_API_KEY=SG.xxx
EMAIL_FROM=noreply@tudominio.com

# URLs
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000
```

### Testing
```bash
# Backend
pytest backend/tests/

# Frontend
npm run test

# E2E
npm run test:e2e
```

---

## 🎓 RECURSOS

- [Documentación Wompi](https://docs.wompi.co/)
- [Documentación SendGrid](https://docs.sendgrid.com/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SvelteKit Docs](https://kit.svelte.dev/)

---

✅ **Con esta guía tienes el roadmap completo para terminar la implementación del e-commerce.**
