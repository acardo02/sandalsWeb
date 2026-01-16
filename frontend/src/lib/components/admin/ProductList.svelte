<script>
  export let products = [];
  export let loading = false;
  export let onEdit;
  export let onDelete;
</script>

<div class="product-list">
  <h3>Productos ({products.length})</h3>

  {#if loading}
    <div class="loading">
      <div class="spinner"></div>
      <p>Cargando productos...</p>
    </div>
  {:else if products.length === 0}
    <div class="empty">
      <p>No hay productos registrados</p>
      <p class="hint">Crea tu primer producto usando el boton de arriba</p>
    </div>
  {:else}
    <div class="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Imagen</th>
            <th>Nombre</th>
            <th>Categoria</th>
            <th>Precio</th>
            <th>Stock</th>
            <th>Tallas</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {#each products as product}
            <tr>
              <td class="image-cell">
                {#if product.main_image || (product.images && product.images.length > 0)}
                  <img src={product.main_image || product.images[0]} alt={product.name} />
                {:else}
                  <div class="no-image">Sin imagen</div>
                {/if}
              </td>
              <td>
                <strong>{product.name}</strong>
                {#if product.description}
                  <p class="description">{product.description.slice(0, 50)}...</p>
                {/if}
              </td>
              <td>{product.category}</td>
              <td class="price">${product.base_price?.toFixed(2) || '0.00'}</td>
              <td>
                <span class="stock {product.total_stock === 0 ? 'out-of-stock' : ''}">
                  {product.total_stock || 0}
                </span>
              </td>
              <td class="sizes">
                {#if product.variants && product.variants.length > 0}
                  {product.variants.map(v => v.size).join(', ')}
                {:else}
                  -
                {/if}
              </td>
              <td class="actions">
                <button type="button" class="btn-edit" on:click={() => onEdit(product)}>
                  Editar
                </button>
                <button type="button" class="btn-delete" on:click={() => onDelete(product.id)}>
                  Eliminar
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
.product-list {
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

.image-cell {
  width: 80px;
}

.image-cell img {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border: 1px solid #ddd;
}

.no-image {
  width: 60px;
  height: 60px;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  color: #999;
  text-align: center;
}

td strong {
  display: block;
  margin-bottom: 0.3rem;
}

.description {
  font-size: 0.8rem;
  color: #666;
  margin: 0;
}

.price {
  font-weight: 600;
  font-size: 1rem;
}

.stock {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  background: #e8f5e9;
  color: #2e7d32;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
}

.stock.out-of-stock {
  background: #ffebee;
  color: #c62828;
}

.sizes {
  font-size: 0.85rem;
  color: #666;
  max-width: 150px;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.btn-edit,
.btn-delete {
  padding: 0.5rem 1rem;
  font-size: 0.8rem;
  cursor: pointer;
  border: none;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn-edit {
  background: #f0f0f0;
  color: #333;
}

.btn-edit:hover {
  background: #e0e0e0;
}

.btn-delete {
  background: #ffebee;
  color: #c62828;
}

.btn-delete:hover {
  background: #ffcdd2;
}

@media (max-width: 968px) {
  table {
    font-size: 0.85rem;
  }

  th,
  td {
    padding: 0.7rem;
  }

  .image-cell img,
  .no-image {
    width: 50px;
    height: 50px;
  }

  .actions {
    flex-direction: column;
  }
}
</style>
