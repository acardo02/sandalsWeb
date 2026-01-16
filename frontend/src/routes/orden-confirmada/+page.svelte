<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { orders as ordersApi } from '$lib/api';

  let order = null;
  let loading = true;
  let error = '';

  const loadOrder = async () => {
    const orderId = $page.url.searchParams.get('order_id');

    if (!orderId) {
      loading = false;
      return;
    }

    try {
      order = await ordersApi.getById(orderId);
    } catch (err) {
      console.error('Error loading order:', err);
    } finally {
      loading = false;
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  onMount(loadOrder);
</script>

<svelte:head>
  <title>Orden Confirmada | CALERO</title>
</svelte:head>

<section class="confirmation-page">
  {#if loading}
    <div class="loading">
      <div class="spinner"></div>
      <p>Cargando...</p>
    </div>
  {:else}
    <div class="confirmation-content">
      <div class="success-icon">
        <svg viewBox="0 0 24 24" width="80" height="80" fill="none" stroke="#2e7d32" stroke-width="2">
          <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
          <polyline points="22 4 12 14.01 9 11.01"/>
        </svg>
      </div>

      <h1>¡Gracias por tu compra!</h1>
      <p class="subtitle">Tu orden ha sido recibida y está siendo procesada</p>

      {#if order}
        <div class="order-details">
          <div class="detail-row">
            <span class="label">Número de Orden</span>
            <span class="value">#{order.id.slice(-8).toUpperCase()}</span>
          </div>
          <div class="detail-row">
            <span class="label">Fecha</span>
            <span class="value">{formatDate(order.created_at)}</span>
          </div>
          <div class="detail-row">
            <span class="label">Total</span>
            <span class="value total">${order.total_amount.toFixed(2)}</span>
          </div>
          <div class="detail-row">
            <span class="label">Estado</span>
            <span class="value status">{order.status === 'pending' ? 'Pendiente de pago' : 'Pagado'}</span>
          </div>
        </div>

        <div class="order-items">
          <h3>Productos</h3>
          {#each order.items as item}
            <div class="item">
              <img src={item.product_image || '/placeholder.png'} alt={item.product_name} />
              <div class="item-info">
                <span class="name">{item.product_name}</span>
                {#if item.variant_info}
                  <span class="variant">{item.variant_info}</span>
                {/if}
                <span class="qty">Cantidad: {item.quantity}</span>
              </div>
              <span class="price">${(item.price * item.quantity).toFixed(2)}</span>
            </div>
          {/each}
        </div>

        <div class="shipping-info">
          <h3>Dirección de Envío</h3>
          <p>{order.shipping_address.street}</p>
          <p>{order.shipping_address.city}, {order.shipping_address.state}</p>
          <p>{order.shipping_address.country}</p>
        </div>
      {/if}

      <div class="next-steps">
        <h3>¿Qué sigue?</h3>
        <ul>
          <li>Recibirás un email de confirmación con los detalles de tu orden</li>
          <li>Te notificaremos cuando tu pedido sea enviado</li>
          <li>Podrás rastrear tu envío desde "Mis Órdenes"</li>
        </ul>
      </div>

      <div class="actions">
        <a href="/mis-ordenes" class="btn-secondary">Ver Mis Órdenes</a>
        <a href="/productos" class="btn-primary">Seguir Comprando</a>
      </div>
    </div>
  {/if}
</section>

<style>
.confirmation-page {
  padding: 8rem 5vw 4rem;
  min-height: 100vh;
  background: #fafafa;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 1rem;
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

.confirmation-content {
  max-width: 600px;
  margin: 0 auto;
  text-align: center;
}

.success-icon {
  margin-bottom: 2rem;
  animation: scaleIn 0.5s ease;
}

@keyframes scaleIn {
  from {
    transform: scale(0);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

h1 {
  font-family: 'Playfair Display', serif;
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #666;
  margin-bottom: 3rem;
}

.order-details {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 0;
  border-bottom: 1px solid #eee;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-row .label {
  color: #666;
}

.detail-row .value {
  font-weight: 500;
}

.detail-row .value.total {
  font-size: 1.2rem;
  color: #000;
}

.detail-row .value.status {
  color: #f5a623;
}

.order-items {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  text-align: left;
}

.order-items h3 {
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
}

.item {
  display: flex;
  gap: 1rem;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid #eee;
}

.item:last-child {
  border-bottom: none;
}

.item img {
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

.item-info .name {
  font-weight: 500;
}

.item-info .variant {
  font-size: 0.85rem;
  color: #666;
}

.item-info .qty {
  font-size: 0.85rem;
  color: #999;
}

.item .price {
  font-weight: 500;
}

.shipping-info {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  text-align: left;
}

.shipping-info h3 {
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.shipping-info p {
  color: #666;
  margin: 0.3rem 0;
}

.next-steps {
  background: #e8f5e9;
  padding: 2rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  text-align: left;
}

.next-steps h3 {
  margin-bottom: 1rem;
  color: #2e7d32;
}

.next-steps ul {
  list-style: none;
  padding: 0;
}

.next-steps li {
  padding: 0.5rem 0;
  padding-left: 1.5rem;
  position: relative;
  color: #333;
}

.next-steps li::before {
  content: '✓';
  position: absolute;
  left: 0;
  color: #2e7d32;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.btn-primary, .btn-secondary {
  padding: 1rem 2rem;
  text-decoration: none;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.85rem;
  transition: all 0.3s ease;
}

.btn-primary {
  background: #000;
  color: white;
}

.btn-primary:hover {
  background: #333;
}

.btn-secondary {
  background: white;
  color: #000;
  border: 1px solid #000;
}

.btn-secondary:hover {
  background: #f5f5f5;
}

@media (max-width: 768px) {
  .confirmation-page {
    padding: 6rem 1rem 2rem;
  }

  h1 {
    font-size: 2rem;
  }

  .actions {
    flex-direction: column;
  }

  .btn-primary, .btn-secondary {
    width: 100%;
    text-align: center;
  }
}
</style>
