<script>
  import { onMount } from 'svelte';
  import { products as productsApi } from '$lib/api';
  import { addToCart } from '$lib/stores/cartStore';
  import ProductImage from '$lib/components/producto/ProductImage.svelte';
  import QuantitySelector from '$lib/components/producto/QuantitySelector.svelte';
  import ProductFeatures from '$lib/components/producto/ProductFeatures.svelte';
  
  export let params;

  let product = null;
  let loading = true;
  let error = '';
  let visible = false;
  let isAdding = false;
  let quantity = 1;
  let stockError = '';
  
  const handleAddToCart = () => {
    if (!product) return;
    
    stockError = '';
    
    // Validar stock antes de agregar
    if (product.stock !== undefined && quantity > product.stock) {
      stockError = `Solo hay ${product.stock} unidades disponibles`;
      return;
    }

    if (product.stock === 0) {
      stockError = 'Producto agotado';
      return;
    }
    
    isAdding = true;
    
    // Intentar agregar al carrito
    const success = addToCart(product, quantity);
    
    if (!success) {
      stockError = `No hay suficiente stock disponible`;
      isAdding = false;
      return;
    }
    
    setTimeout(() => {
      isAdding = false;
      // Resetear cantidad después de agregar
      quantity = 1;
    }, 1500);
  };
  
  onMount(async () => {
    try {
      product = await productsApi.getById(params.id);
    } catch (err) {
      error = 'Error al cargar el producto';
      console.error(err);
    } finally {
      loading = false;
      setTimeout(() => visible = true, 200);
    }
  });
</script>

{#if loading}
  <section class="product-detail">
    <div class="loading">
      <div class="spinner"></div>
      <p>Cargando producto...</p>
    </div>
  </section>
{:else if error || !product}
  <section class="not-found">
    <h2>{error || 'Producto no encontrado'}</h2>
    <a href="/productos">Volver a productos</a>
  </section>
{:else}
  <section class="product-detail">
    <a href="/productos" class="back-link">
      ← Volver a productos
    </a>
    
    <div class="container {visible ? 'show' : ''}">
      <ProductImage 
        image={product.image_url ? product.image_url : product.image} 
        name={product.name} 
      />

      <div class="info-section">
        <span class="category">Colección 2025</span>
        <h1>{product.name}</h1>
        
        <p class="price">${product.price}</p>
        
        {#if product.stock !== undefined}
          {#if product.stock === 0}
            <p class="stock-status out-of-stock">Agotado</p>
          {:else if product.stock < 5}
            <p class="stock-status low-stock">¡Últimas {product.stock} unidades!</p>
          {:else}
            <p class="stock-status in-stock">Disponible</p>
          {/if}
        {/if}
        
        <div class="description">
          <p>{product.description || 'Diseño minimalista y atemporal. Confeccionado con materiales de alta calidad para garantizar durabilidad y comodidad excepcionales.'}</p>
        </div>
        
        <div class="divider"></div>
        
        {#if product.stock > 0}
          <QuantitySelector 
            bind:quantity 
            maxStock={product.stock || 10}
          />
          
          {#if stockError}
            <p class="stock-error">{stockError}</p>
          {/if}
          
          <button 
            class="add-to-cart-btn {isAdding ? 'adding' : ''}" 
            on:click={handleAddToCart}
            disabled={isAdding || product.stock === 0}
          >
            {isAdding ? 'Agregado al carrito ✓' : 'Agregar al carrito'}
          </button>
        {:else}
          <button class="add-to-cart-btn" disabled>
            Producto agotado
          </button>
        {/if}
        
        <ProductFeatures />
      </div>
    </div>
  </section>
{/if}

<style>
.product-detail {
  padding: 8rem 10vw 6rem;
  min-height: 100vh;
  background: white;
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
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #000;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.back-link {
  display: inline-flex;
  align-items: center;
  color: #000;
  text-decoration: none;
  font-size: 0.85rem;
  letter-spacing: 1px;
  margin-bottom: 3rem;
  transition: opacity 0.3s ease;
}

.back-link:hover {
  opacity: 0.6;
}

.container {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 8rem;
  max-width: 1400px;
  margin: 0 auto;
  opacity: 0;
  transform: translateY(30px);
  transition: all 1s cubic-bezier(0.16, 1, 0.3, 1);
}

.container.show {
  opacity: 1;
  transform: translateY(0);
}

.info-section {
  padding-top: 2rem;
}

.category {
  display: block;
  font-size: 0.75rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  opacity: 0.6;
  margin-bottom: 1rem;
}

h1 {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2.5rem, 4vw, 3.5rem);
  line-height: 1.1;
  margin-bottom: 1.5rem;
}

.price {
  font-size: 2rem;
  font-weight: 500;
  margin-bottom: 1rem;
}

.stock-status {
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 1.5rem;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  display: inline-block;
}

.stock-status.in-stock {
  background: #e8f5e9;
  color: #2e7d32;
}

.stock-status.low-stock {
  background: #fff3e0;
  color: #e65100;
}

.stock-status.out-of-stock {
  background: #ffebee;
  color: #c62828;
}

.description {
  margin-bottom: 2rem;
  line-height: 1.8;
  color: #555;
}

.divider {
  width: 100%;
  height: 1px;
  background: #e5e5e5;
  margin: 2.5rem 0;
}

.stock-error {
  color: #c62828;
  font-size: 0.9rem;
  margin-bottom: 1rem;
  padding: 0.8rem;
  background: #ffebee;
  border-left: 3px solid #c62828;
}

.add-to-cart-btn {
  width: 100%;
  background: #000;
  color: white;
  border: 1px solid #000;
  padding: 1.3rem;
  font-size: 0.8rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 2.5rem;
}

.add-to-cart-btn:hover:not(:disabled) {
  background: white;
  color: #000;
}

.add-to-cart-btn.adding {
  background: white;
  color: #000;
}

.add-to-cart-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.not-found {
  min-height: 60vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
}

.not-found h2 {
  font-family: 'Playfair Display', serif;
  font-size: 2.5rem;
  margin-bottom: 2rem;
}

.not-found a {
  color: #000;
  text-decoration: none;
  border-bottom: 1px solid #000;
  padding-bottom: 0.2rem;
  transition: opacity 0.3s ease;
}

.not-found a:hover {
  opacity: 0.6;
}

@media (max-width: 968px) {
  .product-detail {
    padding: 6rem 5vw 4rem;
  }
  
  .container {
    grid-template-columns: 1fr;
    gap: 4rem;
  }
  
  .info-section {
    padding-top: 0;
  }
}

@media (max-width: 768px) {
  h1 {
    font-size: 2rem;
  }
  
  .price {
    font-size: 1.5rem;
  }
}
</style>