<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { orders as ordersApi, auth } from '$lib/api';

  let order = null;
  let loading = true;
  let error = '';
  let cancelling = false;

  $: orderId = $page.params.id;

  const statusLabels = {
    pending: { label: 'Pendiente de Pago', color: '#f5a623', icon: '⏳' },
    paid: { label: 'Pago Confirmado', color: '#2e7d32', icon: '✓' },
    processing: { label: 'Preparando Pedido', color: '#1565c0', icon: '📦' },
    shipped: { label: 'Enviado', color: '#7b1fa2', icon: '🚚' },
    delivered: { label: 'Entregado', color: '#2e7d32', icon: '✅' },
    cancelled: { label: 'Cancelado', color: '#c62828', icon: '✗' },
    failed: { label: 'Pago Fallido', color: '#c62828', icon: '✗' },
    refunded: { label: 'Reembolsado', color: '#666', icon: '↩' }
  };

  const statusOrder = ['pending', 'paid', 'processing', 'shipped', 'delivered'];

  const loadOrder = async () => {
    try {
      await auth.getMe();
      order = await ordersApi.getById(orderId);
    } catch (err) {
      if (err.message.includes('credenciales') || err.message.includes('401')) {
        goto('/login?redirect=/orden/' + orderId);
        return;
      }
      error = 'No se pudo cargar la orden';
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

  const formatShortDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusInfo = (status) => {
    return statusLabels[status] || { label: status, color: '#666', icon: '?' };
  };

  const getCurrentStep = (status) => {
    const idx = statusOrder.indexOf(status);
    return idx >= 0 ? idx : 0;
  };

  const cancelOrder = async () => {
    if (!confirm('¿Estás seguro de que deseas cancelar esta orden?')) return;

    cancelling = true;
    try {
      await ordersApi.cancel(order.id);
      order = await ordersApi.getById(order.id);
    } catch (err) {
      alert('Error al cancelar: ' + err.message);
    } finally {
      cancelling = false;
    }
  };

  const retryPayment = async () => {
    try {
      const result = await ordersApi.createPaymentLink(order.id);
      if (result.payment_link) {
        window.location.href = result.payment_link;
      }
    } catch (err) {
      alert('Error al generar link de pago: ' + err.message);
    }
  };

  onMount(() => {
    if (orderId) {
      loadOrder();
    }
  });

  // Recargar si cambia el ID
  $: if (orderId && !order && !loading) {
    loading = true;
    loadOrder();
  }
</script>

<svelte:head>
  <title>Orden #{orderId ? orderId.slice(-8).toUpperCase() : ''} | CALERO</title>
</svelte:head>

<section class="order-detail">
  <a href="/mis-ordenes" class="back-link">← Volver a Mis Órdenes</a>

  {#if loading}
    <div class="loading">
      <div class="spinner"></div>
      <p>Cargando orden...</p>
    </div>
  {:else if error}
    <div class="error">
      <h2>{error}</h2>
      <a href="/mis-ordenes" class="btn-primary">Ver Mis Órdenes</a>
    </div>
  {:else if order}
    {@const statusInfo = getStatusInfo(order.status)}
    {@const currentStep = getCurrentStep(order.status)}

    <div class="order-header">
      <div>
        <h1>Orden #{order.id.slice(-8).toUpperCase()}</h1>
        <p class="order-date">Realizada el {formatDate(order.created_at)}</p>
      </div>
      <span class="status-badge" style="background: {statusInfo.color}">
        {statusInfo.icon} {statusInfo.label}
      </span>
    </div>

    <!-- Progress Tracker -->
    {#if !['cancelled', 'failed', 'refunded'].includes(order.status)}
      <div class="progress-tracker">
        {#each statusOrder as status, i}
          {@const stepInfo = getStatusInfo(status)}
          <div class="progress-step {i <= currentStep ? 'completed' : ''} {i === currentStep ? 'current' : ''}">
            <div class="step-icon">{stepInfo.icon}</div>
            <span class="step-label">{stepInfo.label}</span>
          </div>
          {#if i < statusOrder.length - 1}
            <div class="progress-line {i < currentStep ? 'completed' : ''}"></div>
          {/if}
        {/each}
      </div>
    {/if}

    <div class="order-grid">
      <!-- Productos -->
      <div class="order-section products-section">
        <h3>Productos</h3>
        <div class="items-list">
          {#each order.items as item}
            <div class="item">
              <img src={item.product_image || '/placeholder.png'} alt={item.product_name} />
              <div class="item-info">
                <span class="name">{item.product_name}</span>
                {#if item.variant_info}
                  <span class="variant">{item.variant_info}</span>
                {/if}
                <span class="details">
                  ${item.price.toFixed(2)} × {item.quantity}
                </span>
              </div>
              <span class="item-total">${(item.price * item.quantity).toFixed(2)}</span>
            </div>
          {/each}
        </div>

        <div class="totals">
          <div class="total-row">
            <span>Subtotal</span>
            <span>${order.subtotal.toFixed(2)}</span>
          </div>
          {#if order.discount_amount > 0}
            <div class="total-row discount">
              <span>Descuento ({order.coupon_code})</span>
              <span>-${order.discount_amount.toFixed(2)}</span>
            </div>
          {/if}
          <div class="total-row">
            <span>Envío</span>
            <span>{order.shipping_cost === 0 ? 'GRATIS' : `$${order.shipping_cost.toFixed(2)}`}</span>
          </div>
          <div class="total-row final">
            <span>Total</span>
            <span>${order.total_amount.toFixed(2)}</span>
          </div>
        </div>
      </div>

      <!-- Información de envío -->
      <div class="order-section">
        <h3>Envío</h3>
        <div class="info-block">
          <p class="shipping-method">{order.shipping_method_name || 'Envío Estándar'}</p>
          <p>{order.shipping_address.street}</p>
          <p>{order.shipping_address.city}, {order.shipping_address.state}</p>
          <p>{order.shipping_address.country}</p>
        </div>

        {#if order.tracking_number}
          <div class="tracking-info">
            <span class="label">Número de Rastreo:</span>
            <span class="tracking-number">{order.tracking_number}</span>
          </div>
        {/if}

        {#if order.estimated_delivery}
          <div class="delivery-estimate">
            <span class="label">Entrega Estimada:</span>
            <span>{formatDate(order.estimated_delivery)}</span>
          </div>
        {/if}
      </div>

      <!-- Historial -->
      {#if order.tracking_history && order.tracking_history.length > 0}
        <div class="order-section">
          <h3>Historial</h3>
          <div class="timeline">
            {#each order.tracking_history as event}
              {@const eventInfo = getStatusInfo(event.status)}
              <div class="timeline-item">
                <div class="timeline-dot" style="background: {eventInfo.color}"></div>
                <div class="timeline-content">
                  <span class="event-status">{eventInfo.label}</span>
                  {#if event.notes}
                    <span class="event-notes">{event.notes}</span>
                  {/if}
                  {#if event.location}
                    <span class="event-location">{event.location}</span>
                  {/if}
                  <span class="event-date">{formatShortDate(event.timestamp)}</span>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>

    <!-- Acciones -->
    <div class="order-actions">
      {#if order.status === 'pending'}
        <button class="btn-primary" on:click={retryPayment}>
          Completar Pago
        </button>
        <button class="btn-danger" on:click={cancelOrder} disabled={cancelling}>
          {cancelling ? 'Cancelando...' : 'Cancelar Orden'}
        </button>
      {/if}

      {#if order.status === 'delivered'}
        <a href="/producto/{order.items[0].product_id}" class="btn-secondary">
          Dejar una Reseña
        </a>
      {/if}
    </div>
  {/if}
</section>

<style>
.order-detail {
  padding: 8rem 5vw 4rem;
  min-height: 100vh;
  background: #fafafa;
}

.back-link {
  display: inline-block;
  color: #000;
  text-decoration: none;
  font-size: 0.9rem;
  margin-bottom: 2rem;
  transition: opacity 0.3s ease;
}

.back-link:hover {
  opacity: 0.6;
}

.loading, .error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
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

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.order-header h1 {
  font-family: 'Playfair Display', serif;
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.order-date {
  color: #666;
}

.status-badge {
  padding: 0.5rem 1.2rem;
  border-radius: 20px;
  color: white;
  font-size: 0.85rem;
}

/* Progress Tracker */
.progress-tracker {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 3rem;
  background: white;
  padding: 2rem;
  border-radius: 8px;
  overflow-x: auto;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  min-width: 100px;
}

.step-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  transition: all 0.3s ease;
}

.progress-step.completed .step-icon {
  background: #2e7d32;
}

.progress-step.current .step-icon {
  background: #1565c0;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.step-label {
  font-size: 0.75rem;
  text-align: center;
  color: #666;
}

.progress-step.completed .step-label,
.progress-step.current .step-label {
  color: #000;
  font-weight: 500;
}

.progress-line {
  flex: 1;
  height: 3px;
  background: #e0e0e0;
  min-width: 30px;
  margin: 0 0.5rem;
  margin-bottom: 1.5rem;
}

.progress-line.completed {
  background: #2e7d32;
}

/* Grid */
.order-grid {
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.order-section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.order-section h3 {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
}

.products-section {
  grid-row: 1 / 3;
}

/* Items */
.items-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
}

.item {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.item img {
  width: 70px;
  height: 70px;
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

.item-info .details {
  font-size: 0.85rem;
  color: #999;
}

.item-total {
  font-weight: 500;
}

/* Totals */
.totals {
  border-top: 1px solid #eee;
  padding-top: 1rem;
}

.total-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
}

.total-row.discount {
  color: #2e7d32;
}

.total-row.final {
  font-size: 1.2rem;
  font-weight: 600;
  border-top: 1px solid #eee;
  padding-top: 1rem;
  margin-top: 0.5rem;
}

/* Shipping */
.info-block {
  margin-bottom: 1.5rem;
}

.info-block p {
  color: #666;
  margin: 0.3rem 0;
}

.shipping-method {
  font-weight: 500;
  color: #000 !important;
  margin-bottom: 0.5rem !important;
}

.tracking-info, .delivery-estimate {
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.tracking-info .label, .delivery-estimate .label {
  display: block;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #999;
  margin-bottom: 0.3rem;
}

.tracking-number {
  font-family: monospace;
  font-size: 1.1rem;
  font-weight: 600;
}

/* Timeline */
.timeline {
  position: relative;
}

.timeline-item {
  display: flex;
  gap: 1rem;
  padding-bottom: 1.5rem;
  position: relative;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-item::before {
  content: '';
  position: absolute;
  left: 6px;
  top: 16px;
  bottom: 0;
  width: 2px;
  background: #e0e0e0;
}

.timeline-item:last-child::before {
  display: none;
}

.timeline-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  flex-shrink: 0;
  z-index: 1;
}

.timeline-content {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.event-status {
  font-weight: 500;
}

.event-notes {
  font-size: 0.9rem;
  color: #666;
}

.event-location {
  font-size: 0.85rem;
  color: #999;
}

.event-date {
  font-size: 0.8rem;
  color: #999;
}

/* Actions */
.order-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 2rem;
  flex-wrap: wrap;
}

.btn-primary, .btn-secondary, .btn-danger {
  padding: 1rem 2rem;
  text-decoration: none;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.85rem;
  cursor: pointer;
  border: none;
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

.btn-danger {
  background: white;
  color: #c62828;
  border: 1px solid #c62828;
}

.btn-danger:hover {
  background: #ffebee;
}

.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 968px) {
  .order-grid {
    grid-template-columns: 1fr;
  }

  .products-section {
    grid-row: auto;
  }

  .progress-tracker {
    justify-content: flex-start;
  }
}

@media (max-width: 600px) {
  .order-detail {
    padding: 6rem 1rem 2rem;
  }

  .order-header {
    flex-direction: column;
  }

  .order-header h1 {
    font-size: 1.5rem;
  }

  .progress-step {
    min-width: 70px;
  }

  .step-label {
    font-size: 0.65rem;
  }
}
</style>
