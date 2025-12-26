<script>
  import { onMount } from 'svelte';
  import { products as productsApi, upload } from '$lib/api';
  import ProductForm from '$lib/components/admin/ProductForm.svelte';
  import ProductList from '$lib/components/admin/ProductList.svelte';

  let products = [];
  let loading = true;
  let error = '';
  let showForm = false;
  let editingProduct = null;

  onMount(async () => {
    await loadProducts();
  });

  async function loadProducts() {
    try {
      loading = true;
      error = '';
      products = await productsApi.getAll({ limit: 100 });
    } catch (err) {
      error = 'Error al cargar productos: ' + err.message;
    } finally {
      loading = false;
    }
  }

  async function handleCreate(productData) {
    try {
      await productsApi.create(productData);
      await loadProducts();
      showForm = false;
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message };
    }
  }

  async function handleUpdate(id, productData) {
    try {
      await productsApi.update(id, productData);
      await loadProducts();
      editingProduct = null;
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message };
    }
  }

  async function handleDelete(id) {
    if (!confirm('¿Estás seguro de eliminar este producto?')) return;

    try {
      await productsApi.delete(id);
      await loadProducts();
    } catch (err) {
      alert('Error al eliminar producto: ' + err.message);
    }
  }

  function handleEdit(product) {
    editingProduct = product;
    showForm = true;
  }

  function handleCancelForm() {
    showForm = false;
    editingProduct = null;
  }

  function handleNewProduct() {
    editingProduct = null;
    showForm = true;
  }
</script>

<div class="dashboard">
  <header class="dashboard-header">
    <div>
      <h1>Gestión de Productos</h1>
      <p class="subtitle">Administra el catálogo de productos de CALERO</p>
    </div>
    
    {#if !showForm}
      <button class="btn-primary" on:click={handleNewProduct}>
        + Nuevo Producto
      </button>
    {/if}
  </header>

  {#if error}
    <div class="error-banner">
      {error}
    </div>
  {/if}

  {#if showForm}
    <div class="form-section">
      <ProductForm
        product={editingProduct}
        onSubmit={editingProduct ? handleUpdate : handleCreate}
        onCancel={handleCancelForm}
      />
    </div>
  {/if}

  <div class="products-section">
    <ProductList
      {products}
      {loading}
      onEdit={handleEdit}
      onDelete={handleDelete}
    />
  </div>
</div>

<style>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid #ddd;
}

h1 {
  font-family: 'Playfair Display', serif;
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #666;
  font-size: 0.95rem;
}

.btn-primary {
  background: #000;
  color: white;
  border: none;
  padding: 0.9rem 1.8rem;
  font-size: 0.85rem;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
}

.btn-primary:hover {
  background: #333;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.error-banner {
  background: #fee;
  color: #c33;
  padding: 1rem 1.5rem;
  margin-bottom: 2rem;
  border-left: 4px solid #c33;
}

.form-section {
  background: white;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.products-section {
  background: white;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    gap: 1rem;
  }

  .btn-primary {
    width: 100%;
  }

  h1 {
    font-size: 2rem;
  }
}
</style>