<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { cart, cartTotal, clearCart, getCartItemsForOrder } from '$lib/stores/cartStore';
  import { orders, coupons as couponsApi, auth } from '$lib/api';

  let user = null;
  let loading = true;
  let submitting = false;
  let error = '';

  // Formulario de dirección
  let shippingAddress = {
    street: '',
    city: '',
    state: '',
    zip_code: '',
    country: 'El Salvador'
  };

  // Cupón
  let couponCode = '';
  let couponLoading = false;
  let couponError = '';
  let appliedCoupon = null;
  let discountAmount = 0;

  // Método de envío
  let shippingMethodId = 'standard_ss';
  const shippingMethods = [
    { id: 'standard_ss', name: 'Envío Estándar San Salvador', price: 3.00, days: '2-4 días', freeThreshold: 50 },
    { id: 'standard_national', name: 'Envío Nacional', price: 5.00, days: '3-7 días', freeThreshold: 75 },
    { id: 'express', name: 'Envío Express', price: 10.00, days: '1-2 días', freeThreshold: null }
  ];

  // Notas del cliente
  let customerNotes = '';

  // Calcular costos
  $: subtotal = $cartTotal;
  $: selectedShipping = shippingMethods.find(m => m.id === shippingMethodId);
  $: shippingCost = selectedShipping?.freeThreshold && subtotal >= selectedShipping.freeThreshold
    ? 0
    : (selectedShipping?.price || 0);
  $: total = subtotal - discountAmount + shippingCost;

  // Validar formulario
  $: isFormValid = shippingAddress.street && shippingAddress.city &&
    shippingAddress.state && $cart.length > 0;

  const loadUser = async () => {
    try {
      user = await auth.getMe();
      // Pre-llenar dirección si el usuario tiene una guardada
      if (user.address) {
        shippingAddress = { ...user.address };
      }
    } catch (err) {
      // Usuario no autenticado
      goto('/login?redirect=/checkout');
    } finally {
      loading = false;
    }
  };

  const applyCoupon = async () => {
    if (!couponCode.trim()) return;

    couponLoading = true;
    couponError = '';

    console.log('Aplicando cupón:', couponCode.trim(), 'Subtotal:', subtotal);

    try {
      const result = await couponsApi.validate(couponCode.trim(), subtotal);
      console.log('Resultado validación:', result);

      if (result.valid) {
        appliedCoupon = result;
        discountAmount = result.discount_amount;
        couponError = '';
      }
    } catch (err) {
      console.error('Error aplicando cupón:', err);
      // Mostrar mensaje más específico
      if (err.message.includes('Failed to fetch') || err.message.includes('fetch')) {
        couponError = 'Error de conexión. Verifica que el servidor esté activo.';
      } else {
        couponError = err.message || 'Cupón no válido';
      }
      appliedCoupon = null;
      discountAmount = 0;
    } finally {
      couponLoading = false;
    }
  };

  const removeCoupon = () => {
    appliedCoupon = null;
    discountAmount = 0;
    couponCode = '';
    couponError = '';
  };

  const handleSubmit = async () => {
    if (!isFormValid || submitting) return;

    submitting = true;
    error = '';

    try {
      // Crear orden
      const orderData = {
        items: getCartItemsForOrder(),
        shipping_address: shippingAddress,
        shipping_method_id: shippingMethodId,
        coupon_code: appliedCoupon?.code || null,
        customer_notes: customerNotes || null
      };

      const order = await orders.create(orderData);

      // Crear link de pago
      const paymentResult = await orders.createPaymentLink(order.id);

      // Limpiar carrito
      clearCart();

      // Redirigir a Wompi
      if (paymentResult.payment_link) {
        window.location.href = paymentResult.payment_link;
      } else {
        // Si no hay link de pago, ir a página de confirmación
        goto(`/orden-confirmada?order_id=${order.id}`);
      }

    } catch (err) {
      error = err.message || 'Error al procesar la orden';
      submitting = false;
    }
  };

  onMount(loadUser);
</script>

<svelte:head>
  <title>Checkout | CALERO</title>
</svelte:head>

{#if loading}
  <section class="checkout">
    <div class="loading">
      <div class="spinner"></div>
      <p>Cargando...</p>
    </div>
  </section>
{:else if $cart.length === 0}
  <section class="checkout">
    <div class="empty-cart">
      <h2>Tu carrito está vacío</h2>
      <p>Agrega productos antes de continuar al checkout</p>
      <a href="/productos" class="btn-primary">Ver Productos</a>
    </div>
  </section>
{:else}
  <section class="checkout">
    <h1>Checkout</h1>

    <div class="checkout-grid">
      <!-- Formulario -->
      <div class="checkout-form">
        <!-- Dirección de envío -->
        <div class="form-section">
          <h3>Dirección de Envío</h3>
          <div class="form-group">
            <label for="street">Dirección</label>
            <input
              type="text"
              id="street"
              bind:value={shippingAddress.street}
              placeholder="Calle, número, colonia"
              required
            />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label for="city">Ciudad</label>
              <input
                type="text"
                id="city"
                bind:value={shippingAddress.city}
                placeholder="San Salvador"
                required
              />
            </div>
            <div class="form-group">
              <label for="state">Departamento</label>
              <input
                type="text"
                id="state"
                bind:value={shippingAddress.state}
                placeholder="San Salvador"
                required
              />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label for="zip_code">Código Postal</label>
              <input
                type="text"
                id="zip_code"
                bind:value={shippingAddress.zip_code}
                placeholder="Opcional"
              />
            </div>
            <div class="form-group">
              <label for="country">País</label>
              <input
                type="text"
                id="country"
                bind:value={shippingAddress.country}
                disabled
              />
            </div>
          </div>
        </div>

        <!-- Método de envío -->
        <div class="form-section">
          <h3>Método de Envío</h3>
          <div class="shipping-options">
            {#each shippingMethods as method}
              {@const isFree = method.freeThreshold && subtotal >= method.freeThreshold}
              <label class="shipping-option {shippingMethodId === method.id ? 'selected' : ''}">
                <input
                  type="radio"
                  name="shipping"
                  value={method.id}
                  bind:group={shippingMethodId}
                />
                <div class="shipping-info">
                  <span class="shipping-name">{method.name}</span>
                  <span class="shipping-days">{method.days}</span>
                </div>
                <span class="shipping-price">
                  {#if isFree}
                    <span class="free">GRATIS</span>
                    <span class="original">${method.price.toFixed(2)}</span>
                  {:else}
                    ${method.price.toFixed(2)}
                  {/if}
                </span>
              </label>
            {/each}
          </div>
          {#if selectedShipping?.freeThreshold}
            <p class="free-shipping-note">
              {#if subtotal >= selectedShipping.freeThreshold}
                ¡Envío gratis aplicado!
              {:else}
                Agrega ${(selectedShipping.freeThreshold - subtotal).toFixed(2)} más para envío gratis
              {/if}
            </p>
          {/if}
        </div>

        <!-- Cupón -->
        <div class="form-section">
          <h3>Cupón de Descuento</h3>
          {#if appliedCoupon}
            <div class="applied-coupon">
              <div class="coupon-info">
                <span class="coupon-code">{appliedCoupon.code}</span>
                <span class="coupon-description">{appliedCoupon.description || ''}</span>
                <span class="coupon-discount">-${discountAmount.toFixed(2)}</span>
              </div>
              <button class="remove-coupon" on:click={removeCoupon}>×</button>
            </div>
          {:else}
            <div class="coupon-form">
              <input
                type="text"
                bind:value={couponCode}
                placeholder="Código de cupón"
                disabled={couponLoading}
              />
              <button
                class="apply-coupon"
                on:click={applyCoupon}
                disabled={couponLoading || !couponCode.trim()}
              >
                {couponLoading ? 'Aplicando...' : 'Aplicar'}
              </button>
            </div>
            {#if couponError}
              <p class="coupon-error">{couponError}</p>
            {/if}
          {/if}
        </div>

        <!-- Notas -->
        <div class="form-section">
          <h3>Notas (Opcional)</h3>
          <textarea
            bind:value={customerNotes}
            placeholder="Instrucciones especiales para la entrega..."
            rows="3"
          ></textarea>
        </div>
      </div>

      <!-- Resumen del pedido -->
      <div class="order-summary">
        <h3>Resumen del Pedido</h3>

        <div class="cart-items">
          {#each $cart as item}
            <div class="cart-item">
              <img
                src={item.image || item.main_image || '/placeholder.png'}
                alt={item.name}
              />
              <div class="item-info">
                <span class="item-name">{item.name}</span>
                {#if item.variant_info}
                  <span class="item-variant">{item.variant_info}</span>
                {/if}
                <span class="item-qty">Cantidad: {item.qty}</span>
              </div>
              <span class="item-price">${(item.price * item.qty).toFixed(2)}</span>
            </div>
          {/each}
        </div>

        <div class="summary-divider"></div>

        <div class="summary-row">
          <span>Subtotal</span>
          <span>${subtotal.toFixed(2)}</span>
        </div>

        {#if discountAmount > 0}
          <div class="summary-row discount">
            <span>Descuento ({appliedCoupon?.code})</span>
            <span>-${discountAmount.toFixed(2)}</span>
          </div>
        {/if}

        <div class="summary-row">
          <span>Envío ({selectedShipping?.name})</span>
          <span>{shippingCost === 0 ? 'GRATIS' : `$${shippingCost.toFixed(2)}`}</span>
        </div>

        <div class="summary-divider"></div>

        <div class="summary-row total">
          <span>Total</span>
          <span>${total.toFixed(2)}</span>
        </div>

        {#if error}
          <p class="error-message">{error}</p>
        {/if}

        <button
          class="checkout-btn"
          on:click={handleSubmit}
          disabled={!isFormValid || submitting}
        >
          {submitting ? 'Procesando...' : 'Pagar con Wompi'}
        </button>

        <p class="secure-note">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
            <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/>
          </svg>
          Pago seguro con Wompi
        </p>
      </div>
    </div>
  </section>
{/if}

<style>
.checkout {
  padding: 8rem 5vw 4rem;
  min-height: 100vh;
  background: #fafafa;
}

.loading, .empty-cart {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 1rem;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #000;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-cart h2 {
  font-family: 'Playfair Display', serif;
  font-size: 2rem;
}

.btn-primary {
  display: inline-block;
  background: #000;
  color: white;
  padding: 1rem 2rem;
  text-decoration: none;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.85rem;
  margin-top: 1rem;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background: #333;
}

h1 {
  font-family: 'Playfair Display', serif;
  font-size: 2.5rem;
  margin-bottom: 2rem;
  text-align: center;
}

.checkout-grid {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 3rem;
  max-width: 1200px;
  margin: 0 auto;
}

.checkout-form {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-section {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.form-section h3 {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
  color: #333;
}

.form-group input,
.form-section textarea {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 1px solid #ddd;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-section textarea:focus {
  outline: none;
  border-color: #000;
}

.form-group input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

/* Shipping options */
.shipping-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.shipping-option {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #ddd;
  cursor: pointer;
  transition: all 0.2s ease;
}

.shipping-option:hover {
  border-color: #000;
}

.shipping-option.selected {
  border-color: #000;
  background: #f9f9f9;
}

.shipping-option input {
  width: auto;
}

.shipping-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.shipping-name {
  font-weight: 500;
}

.shipping-days {
  font-size: 0.85rem;
  color: #666;
}

.shipping-price {
  font-weight: 500;
}

.shipping-price .free {
  color: #2e7d32;
}

.shipping-price .original {
  text-decoration: line-through;
  color: #999;
  font-size: 0.85rem;
  margin-left: 0.5rem;
}

.free-shipping-note {
  font-size: 0.85rem;
  color: #2e7d32;
  margin-top: 0.75rem;
}

/* Cupón */
.coupon-form {
  display: flex;
  gap: 0.5rem;
}

.coupon-form input {
  flex: 1;
  padding: 0.8rem 1rem;
  border: 1px solid #ddd;
  font-size: 1rem;
}

.apply-coupon {
  padding: 0.8rem 1.5rem;
  background: #000;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  transition: all 0.3s ease;
}

.apply-coupon:hover:not(:disabled) {
  background: #333;
}

.apply-coupon:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.coupon-error {
  color: #c62828;
  font-size: 0.85rem;
  margin-top: 0.5rem;
}

.applied-coupon {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #e8f5e9;
  border-radius: 4px;
}

.coupon-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.coupon-code {
  font-weight: 600;
  text-transform: uppercase;
}

.coupon-description {
  font-size: 0.85rem;
  color: #666;
}

.coupon-discount {
  color: #2e7d32;
  font-weight: 600;
}

.remove-coupon {
  width: 28px;
  height: 28px;
  border: none;
  background: #c62828;
  color: white;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1.2rem;
  line-height: 1;
}

/* Order Summary */
.order-summary {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  height: fit-content;
  position: sticky;
  top: 6rem;
}

.order-summary h3 {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
}

.cart-items {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  max-height: 300px;
  overflow-y: auto;
}

.cart-item {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.cart-item img {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.item-name {
  font-weight: 500;
  font-size: 0.95rem;
}

.item-variant {
  font-size: 0.8rem;
  color: #666;
}

.item-qty {
  font-size: 0.85rem;
  color: #999;
}

.item-price {
  font-weight: 500;
}

.summary-divider {
  height: 1px;
  background: #eee;
  margin: 1.5rem 0;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  font-size: 0.95rem;
}

.summary-row.discount {
  color: #2e7d32;
}

.summary-row.total {
  font-size: 1.2rem;
  font-weight: 600;
  margin-top: 1rem;
}

.error-message {
  color: #c62828;
  font-size: 0.9rem;
  padding: 1rem;
  background: #ffebee;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.checkout-btn {
  width: 100%;
  padding: 1.2rem;
  background: #000;
  color: white;
  border: none;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 2px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.checkout-btn:hover:not(:disabled) {
  background: #333;
}

.checkout-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.secure-note {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1rem;
  font-size: 0.85rem;
  color: #666;
}

@media (max-width: 968px) {
  .checkout-grid {
    grid-template-columns: 1fr;
  }

  .order-summary {
    position: static;
  }
}

@media (max-width: 600px) {
  .checkout {
    padding: 6rem 1rem 2rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  h1 {
    font-size: 2rem;
  }
}
</style>
