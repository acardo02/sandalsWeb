<script>
  import { onMount } from 'svelte';
  import { products as productsApi, coupons as couponsApi } from '$lib/api';
  import ProductForm from '$lib/components/admin/ProductForm.svelte';
  import ProductList from '$lib/components/admin/ProductList.svelte';
  import CouponForm from '$lib/components/admin/CouponForm.svelte';
  import CouponList from '$lib/components/admin/CouponList.svelte';

  // Tab activo
  let activeTab = 'products';

  // Productos
  let products = [];
  let loadingProducts = true;
  let showProductForm = false;
  let editingProduct = null;

  // Cupones
  let coupons = [];
  let loadingCoupons = true;
  let showCouponForm = false;
  let editingCoupon = null;

  let error = '';

  onMount(async () => {
    await Promise.all([loadProducts(), loadCoupons()]);
  });

  async function loadProducts() {
    try {
      loadingProducts = true;
      products = await productsApi.getAll({ limit: 100 });
    } catch (err) {
      error = 'Error al cargar productos: ' + err.message;
    } finally {
      loadingProducts = false;
    }
  }

  async function loadCoupons() {
    try {
      loadingCoupons = true;
      coupons = await couponsApi.getAll({ limit: 100 });
    } catch (err) {
      console.error('Error cargando cupones:', err);
      // No mostrar error si es problema de autenticación (el usuario verá el error al intentar crear)
      coupons = [];
    } finally {
      loadingCoupons = false;
    }
  }

  // ========== PRODUCTOS ==========
  async function handleCreateProduct(id, productData) {
    try {
      await productsApi.create(productData);
      showProductForm = false;
      editingProduct = null;
      await loadProducts();
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message };
    }
  }

  async function handleUpdateProduct(id, productData) {
    try {
      await productsApi.update(id, productData);
      showProductForm = false;
      editingProduct = null;
      await loadProducts();
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message };
    }
  }

  async function handleDeleteProduct(id) {
    if (!id) return;
    try {
      await productsApi.delete(id);
      products = products.filter(p => p.id !== id);
    } catch (err) {
      alert('Error: ' + err.message);
    }
  }

  function handleEditProduct(product) {
    editingProduct = product;
    showProductForm = true;
  }

  function handleCancelProductForm() {
    showProductForm = false;
    editingProduct = null;
  }

  // ========== CUPONES ==========
  async function handleCreateCoupon(code, couponData) {
    try {
      console.log('Creando cupon:', couponData);
      await couponsApi.create(couponData);
      showCouponForm = false;
      editingCoupon = null;
      await loadCoupons();
      return { success: true };
    } catch (err) {
      console.error('Error creando cupon:', err);
      // Mejorar mensaje de error
      let errorMsg = err.message || 'Error desconocido';
      if (errorMsg.includes('401') || errorMsg.includes('credentials')) {
        errorMsg = 'Debes iniciar sesion como administrador';
      } else if (errorMsg.includes('403')) {
        errorMsg = 'No tienes permisos de administrador';
      } else if (errorMsg.includes('fetch') || errorMsg.includes('network')) {
        errorMsg = 'Error de conexion con el servidor';
      }
      return { success: false, error: errorMsg };
    }
  }

  async function handleUpdateCoupon(code, couponData) {
    try {
      await couponsApi.update(code, couponData);
      showCouponForm = false;
      editingCoupon = null;
      await loadCoupons();
      return { success: true };
    } catch (err) {
      return { success: false, error: err.message };
    }
  }

  async function handleDeleteCoupon(code) {
    if (!code) return;
    try {
      await couponsApi.delete(code);
      coupons = [...coupons.filter(c => c.code !== code)];
    } catch (err) {
      alert('Error al eliminar: ' + err.message);
      throw err;
    }
  }

  async function handleToggleCoupon(code, isActive) {
    try {
      await couponsApi.update(code, { is_active: isActive });
      coupons = coupons.map(c => c.code === code ? { ...c, is_active: isActive } : c);
    } catch (err) {
      alert('Error al actualizar: ' + err.message);
    }
  }

  function handleEditCoupon(coupon) {
    editingCoupon = coupon;
    showCouponForm = true;
  }

  function handleCancelCouponForm() {
    showCouponForm = false;
    editingCoupon = null;
  }

  // Cambiar tab
  function switchTab(tab) {
    activeTab = tab;
    // Cerrar formularios al cambiar
    showProductForm = false;
    showCouponForm = false;
    editingProduct = null;
    editingCoupon = null;
  }
</script>

<div class="dashboard">
  <header class="dashboard-header">
    <div>
      <h1>Panel de Administracion</h1>
      <p class="subtitle">Gestiona productos y promociones de CALERO</p>
    </div>
  </header>

  <!-- Tabs -->
  <div class="tabs">
    <button
      class="tab {activeTab === 'products' ? 'active' : ''}"
      on:click={() => switchTab('products')}
    >
      Productos ({products.length})
    </button>
    <button
      class="tab {activeTab === 'coupons' ? 'active' : ''}"
      on:click={() => switchTab('coupons')}
    >
      Promociones ({coupons.length})
    </button>
  </div>

  {#if error}
    <div class="error-banner">
      {error}
    </div>
  {/if}

  <!-- Tab de Productos -->
  {#if activeTab === 'products'}
    <div class="tab-header">
      {#if !showProductForm}
        <button class="btn-primary" on:click={() => { editingProduct = null; showProductForm = true; }}>
          + Nuevo Producto
        </button>
      {/if}
    </div>

    {#if showProductForm}
      <div class="form-section">
        <ProductForm
          product={editingProduct}
          onSubmit={editingProduct ? handleUpdateProduct : handleCreateProduct}
          onCancel={handleCancelProductForm}
        />
      </div>
    {/if}

    <div class="content-section">
      <ProductList
        {products}
        loading={loadingProducts}
        onEdit={handleEditProduct}
        onDelete={handleDeleteProduct}
      />
    </div>
  {/if}

  <!-- Tab de Cupones -->
  {#if activeTab === 'coupons'}
    <div class="tab-header">
      {#if !showCouponForm}
        <button class="btn-primary" on:click={() => { editingCoupon = null; showCouponForm = true; }}>
          + Nuevo Cupon
        </button>
      {/if}
    </div>

    {#if showCouponForm}
      <div class="form-section">
        <CouponForm
          coupon={editingCoupon}
          onSubmit={editingCoupon ? handleUpdateCoupon : handleCreateCoupon}
          onCancel={handleCancelCouponForm}
        />
      </div>
    {/if}

    <div class="content-section">
      <CouponList
        {coupons}
        loading={loadingCoupons}
        onEdit={handleEditCoupon}
        onDelete={handleDeleteCoupon}
        onToggle={handleToggleCoupon}
      />
    </div>
  {/if}
</div>

<style>
.dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 1.5rem;
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

.tabs {
  display: flex;
  gap: 0;
  margin-bottom: 2rem;
  border-bottom: 2px solid #ddd;
}

.tab {
  padding: 1rem 2rem;
  background: none;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  position: relative;
  color: #666;
  transition: all 0.3s ease;
}

.tab:hover {
  color: #000;
}

.tab.active {
  color: #000;
  font-weight: 600;
}

.tab.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: #000;
}

.tab-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1.5rem;
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

.content-section {
  background: white;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
  .tabs {
    overflow-x: auto;
  }

  .tab {
    padding: 0.8rem 1.2rem;
    font-size: 0.9rem;
    white-space: nowrap;
  }

  .tab-header {
    justify-content: center;
  }

  .btn-primary {
    width: 100%;
  }

  h1 {
    font-size: 2rem;
  }
}
</style>