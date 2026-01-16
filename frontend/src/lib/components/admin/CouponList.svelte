<script>
  export let coupons = [];
  export let loading = false;
  export let onEdit;
  export let onDelete;
  export let onToggle;

  let deletingCode = null;

  async function handleDeleteClick(code) {
    if (deletingCode) return;
    if (!confirm('¿Estás seguro de eliminar este cupón?')) return;

    deletingCode = code;
    try {
      await onDelete(code);
    } finally {
      deletingCode = null;
    }
  }

  function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  }

  function isExpired(validUntil) {
    return new Date(validUntil) < new Date();
  }

  function getStatus(coupon) {
    if (!coupon.is_active) return { label: 'Inactivo', class: 'inactive' };
    if (isExpired(coupon.valid_until)) return { label: 'Expirado', class: 'expired' };
    if (coupon.max_uses && coupon.current_uses >= coupon.max_uses) return { label: 'Agotado', class: 'exhausted' };
    return { label: 'Activo', class: 'active' };
  }
</script>

<div class="coupon-list">
  <h3>Cupones ({coupons.length})</h3>

  {#if loading}
    <div class="loading">
      <div class="spinner"></div>
      <p>Cargando cupones...</p>
    </div>
  {:else if coupons.length === 0}
    <div class="empty">
      <p>No hay cupones registrados</p>
      <p class="hint">Crea tu primer cupon usando el boton de arriba</p>
    </div>
  {:else}
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Codigo</th>
            <th>Descripcion</th>
            <th>Descuento</th>
            <th>Usos</th>
            <th>Validez</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {#each coupons as coupon}
            {@const status = getStatus(coupon)}
            <tr class={status.class}>
              <td class="code">
                <strong>{coupon.code}</strong>
              </td>
              <td>
                <span class="description">{coupon.description}</span>
                {#if coupon.minimum_amount}
                  <span class="min-amount">Min: ${coupon.minimum_amount}</span>
                {/if}
              </td>
              <td class="discount">
                {#if coupon.discount_type === 'percentage'}
                  <span class="value">{coupon.discount_value}%</span>
                {:else}
                  <span class="value">${coupon.discount_value}</span>
                {/if}
                {#if coupon.maximum_discount}
                  <span class="max">Max: ${coupon.maximum_discount}</span>
                {/if}
              </td>
              <td class="uses">
                {coupon.current_uses} / {coupon.max_uses || '∞'}
              </td>
              <td class="dates">
                <span class="from">{formatDate(coupon.valid_from)}</span>
                <span class="separator">→</span>
                <span class="until">{formatDate(coupon.valid_until)}</span>
              </td>
              <td>
                <span class="status-badge {status.class}">{status.label}</span>
              </td>
              <td class="actions">
                <button
                  type="button"
                  class="btn-toggle"
                  on:click|stopPropagation={() => onToggle(coupon.code, !coupon.is_active)}
                  title={coupon.is_active ? 'Desactivar' : 'Activar'}
                >
                  {coupon.is_active ? '⏸' : '▶'}
                </button>
                <button
                  type="button"
                  class="btn-edit"
                  on:click|stopPropagation={() => onEdit(coupon)}
                >
                  Editar
                </button>
                <button
                  type="button"
                  class="btn-delete"
                  on:click|stopPropagation={() => handleDeleteClick(coupon.code)}
                  disabled={deletingCode === coupon.code}
                >
                  {deletingCode === coupon.code ? '...' : 'Eliminar'}
                </button>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>

<style>
.coupon-list {
  width: 100%;
}

h3 {
  font-family: 'Playfair Display', serif;
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
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

.empty {
  text-align: center;
  padding: 4rem 2rem;
  color: #666;
}

.empty p {
  margin: 0.5rem 0;
}

.hint {
  font-size: 0.9rem;
  opacity: 0.7;
}

.table-wrapper {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

thead {
  background: #f5f5f5;
}

th {
  padding: 1rem;
  text-align: left;
  font-size: 0.8rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  font-weight: 600;
  border-bottom: 2px solid #ddd;
}

td {
  padding: 1rem;
  border-bottom: 1px solid #eee;
  vertical-align: middle;
}

tr.inactive td,
tr.expired td {
  opacity: 0.6;
}

.code strong {
  font-family: monospace;
  font-size: 1rem;
  letter-spacing: 1px;
}

.description {
  display: block;
}

.min-amount {
  display: block;
  font-size: 0.8rem;
  color: #666;
  margin-top: 0.2rem;
}

.discount .value {
  font-weight: 600;
  font-size: 1.1rem;
  color: #2e7d32;
}

.discount .max {
  display: block;
  font-size: 0.75rem;
  color: #666;
}

.uses {
  font-family: monospace;
}

.dates {
  font-size: 0.85rem;
  white-space: nowrap;
}

.dates .separator {
  margin: 0 0.3rem;
  color: #999;
}

.status-badge {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.active {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-badge.inactive {
  background: #f5f5f5;
  color: #666;
}

.status-badge.expired {
  background: #fff3e0;
  color: #e65100;
}

.status-badge.exhausted {
  background: #ffebee;
  color: #c62828;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.btn-toggle,
.btn-edit,
.btn-delete {
  padding: 0.5rem 0.8rem;
  font-size: 0.8rem;
  cursor: pointer;
  border: none;
  transition: all 0.3s ease;
}

.btn-toggle {
  background: #e3f2fd;
  color: #1565c0;
  font-size: 1rem;
  padding: 0.5rem;
}

.btn-toggle:hover {
  background: #bbdefb;
}

.btn-edit {
  background: #f0f0f0;
  color: #333;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-edit:hover {
  background: #e0e0e0;
}

.btn-delete {
  background: #ffebee;
  color: #c62828;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-delete:hover {
  background: #ffcdd2;
}

.btn-delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 968px) {
  table {
    font-size: 0.85rem;
  }

  th, td {
    padding: 0.7rem;
  }

  .actions {
    flex-direction: column;
  }
}
</style>
