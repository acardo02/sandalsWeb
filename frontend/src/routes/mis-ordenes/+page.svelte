<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { orders as ordersApi, auth } from '$lib/api';

  let ordersList = [];
  let loading = true;
  let error = '';
  let statusFilter = '';

  const statusLabels = {
    pending: { label: 'Pendiente', color: '#f5a623' },
    paid: { label: 'Pagado', color: '#2e7d32' },
    processing: { label: 'Procesando', color: '#1565c0' },
    shipped: { label: 'Enviado', color: '#7b1fa2' },
    delivered: { label: 'Entregado', color: '#2e7d32' },
    cancelled: { label: 'Cancelado', color: '#c62828' },
    failed: { label: 'Fallido', color: '#c62828' },
    refunded: { label: 'Reembolsado', color: '#666' }
  };

  const loadOrders = async () => {
    loading = true;
    try {
      await auth.getMe();
      const params = {};
      if (statusFilter) params.status_filter = statusFilter;
      ordersList = await ordersApi.getMyOrders(params);
    } catch (err) {
      if (err.message.includes('credenciales') || err.message.includes('401')) {
        goto('/login?redirect=/mis-ordenes');
        return;
      }
      error = 'Error al cargar órdenes';
    } finally {
      loading = false;
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getStatusInfo = (status) => {
    return statusLabels[status] || { label: status, color: '#666' };
  };

  onMount(loadOrders);

  $: if (statusFilter !== undefined) {
    loadOrders();
  }
</script>

<svelte:head>
  <title>Mis Órdenes | CALERO</title>
</svelte:head>

<section class="orders-page">
  <h1>Mis Órdenes</h1>

  <div class="filters">
    <select bind:value={statusFilter}>
      <option value="">Todas las órdenes</option>
      <option value="pending">Pendientes</option>
      <option value="paid">Pagadas</option>
      <option value="shipped">Enviadas</option>
      <option value="delivered">Entregadas</option>
      <option value="cancelled">Canceladas</option>
    </select>
  </div>

  {#if loading}
    <div class="loading">
      <div class="spinner"></div>
      <p>Cargando órdenes...</p>
    </div>
  {:else if error}
    <div class="error">
      <p>{error}</p>
    </div>
  {:else if ordersList.length === 0}
    <div class="empty">
      <svg viewBox="0 0 24 24" width="64" height="64" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4zM3 6h18M16 10a4 4 0 01-8 0"/>
      </svg>
      <h2>No tienes órdenes aún</h2>
      <p>Cuando realices una compra, aparecerá aquí</p>
      <a href="/productos" class="btn-primary">Ver Productos</a>
    </div>
  {:else}
    <div class="orders-list">
      {#each ordersList as order}
        {@const statusInfo = getStatusInfo(order.status)}
        <a href="/orden/{order.id}" class="order-card">
          <div class="order-header">
            <div class="order-id">
              <span class="label">Orden</span>
              <span class="value">#{order.id.slice(-8).toUpperCase()}</span>
            </div>
            <span class="status-badge" style="background: {statusInfo.color}">
              {statusInfo.label}
            </span>
          </div>

          <div class="order-info">
            <div class="info-row">
              <span class="label">Fecha</span>
              <span class="value">{formatDate(order.created_at)}</span>
            </div>
            <div class="info-row">
              <span class="label">Total</span>
              <span class="value total">${order.total_amount.toFixed(2)}</span>
            </div>
            <div class="info-row">
              <span class="label">Productos</span>
              <span class="value">{order.items.length} {order.items.length === 1 ? 'artículo' : 'artículos'}</span>
            </div>
          </div>

          <div class="order-items-preview">
            {#each order.items.slice(0, 3) as item}
              <div class="item-thumb">
                <img src={item.product_image || '/placeholder.png'} alt={item.product_name} />
              </div>
            {/each}
            {#if order.items.length > 3}
              <div class="item-thumb more">+{order.items.length - 3}</div>
            {/if}
          </div>

          <div class="order-footer">
            <span class="view-details">Ver detalles →</span>
          </div>
        </a>
      {/each}
    </div>
  {/if}
</section>

<style>
.orders-page {
  padding: 8rem 5vw 4rem;
  min-height: 100vh;
  background: #fafafa;
}

h1 {
  font-family: 'Playfair Display', serif;
  font-size: 2.5rem;
  text-align: center;
  margin-bottom: 2rem;
}

.filters {
  display: flex;
  justify-content: center;
  margin-bottom: 2rem;
}

.filters select {
  padding: 0.8rem 2rem 0.8rem 1rem;
  border: 1px solid #ddd;
  font-size: 1rem;
  background: white;
  cursor: pointer;
}

.loading, .empty, .error {
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

.empty svg {
  opacity: 0.3;
  margin-bottom: 1rem;
}

.empty h2 {
  font-family: 'Playfair Display', serif;
  font-size: 1.8rem;
}

.empty p {
  color: #666;
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

.orders-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-width: 800px;
  margin: 0 auto;
}

.order-card {
  display: block;
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  text-decoration: none;
  color: inherit;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.order-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}

.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.order-id .label {
  display: block;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #999;
}

.order-id .value {
  font-family: monospace;
  font-size: 1.1rem;
  font-weight: 600;
}

.status-badge {
  padding: 0.4rem 1rem;
  border-radius: 20px;
  color: white;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.order-info {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.info-row {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.info-row .label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: #999;
}

.info-row .value {
  font-size: 0.95rem;
}

.info-row .value.total {
  font-weight: 600;
  font-size: 1.1rem;
}

.order-items-preview {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.item-thumb {
  width: 50px;
  height: 50px;
  border-radius: 4px;
  overflow: hidden;
  background: #f5f5f5;
}

.item-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-thumb.more {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  color: #666;
}

.order-footer {
  display: flex;
  justify-content: flex-end;
}

.view-details {
  font-size: 0.85rem;
  color: #000;
  text-decoration: none;
}

@media (max-width: 768px) {
  .orders-page {
    padding: 6rem 1rem 2rem;
  }

  h1 {
    font-size: 2rem;
  }

  .order-info {
    grid-template-columns: repeat(2, 1fr);
  }

  .order-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}
</style>
