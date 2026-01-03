<script>
  import { onMount } from 'svelte';
  import { products as productsApi } from '$lib/api';
  import ProductCard from '$lib/components/ProductCard.svelte';
  import CategoryFilter from '$lib/components/CategoryFilter.svelte';
  
  let allProducts = [];
  let filteredProducts = [];
  let categories = [];
  let selectedCategory = 'Todos';
  let loading = true;
  let error = '';
  let visible = false;
  
  onMount(async () => {
    try {
      allProducts = await productsApi.getAll({ limit: 100 });
      filteredProducts = allProducts;
      
      // Extraer categorías únicas de los productos
      const uniqueCategories = [...new Set(allProducts.map(p => p.category))];
      categories = uniqueCategories.filter(c => c); // Remover undefined/null
      
    } catch (err) {
      error = 'Error al cargar productos: ' + err.message;
    } finally {
      loading = false;
      setTimeout(() => visible = true, 200);
    }
  });

  function handleFilterChange(category) {
    selectedCategory = category;
    
    if (category === 'Todos') {
      filteredProducts = allProducts;
    } else {
      filteredProducts = allProducts.filter(p => p.category === category);
    }
  }
</script>

<section class="productos">
  <div class="header {visible ? 'show' : ''}">
    <span class="label">Colección completa</span>
    <h1>Todos los productos</h1>
    <p class="subtitle">Descubre cada pieza de nuestra selección curada</p>
  </div>

  {#if loading}
    <div class="loading">
      <div class="spinner"></div>
      <p>Cargando productos...</p>
    </div>
  {:else if error}
    <div class="error">
      <p>{error}</p>
      <button on:click={() => window.location.reload()}>Reintentar</button>
    </div>
  {:else}
    {#if categories.length > 0}
      <CategoryFilter 
        {categories} 
        {selectedCategory}
        onFilterChange={handleFilterChange}
      />
    {/if}

    {#if filteredProducts.length === 0}
      <div class="empty">
        <p>No hay productos en esta categoría</p>
        <button class="reset-btn" on:click={() => handleFilterChange('Todos')}>
          Ver todos los productos
        </button>
      </div>
    {:else}
      <div class="grid {visible ? 'show' : ''}">
        {#each filteredProducts as product, i}
          <div class="product-wrapper" style="transition-delay: {i * 0.05}s">
            <ProductCard {product} />
          </div>
        {/each}
      </div>
    {/if}
  {/if}
</section>

<style>
.productos {
  padding: 8rem 10vw 6rem;
  min-height: 100vh;
  background: linear-gradient(to bottom, #fafafa 0%, #ffffff 100%);
}

.header {
  text-align: center;
  margin-bottom: 3rem;
  opacity: 0;
  transform: translateY(30px);
  transition: all 1s cubic-bezier(0.16, 1, 0.3, 1);
}

.header.show {
  opacity: 1;
  transform: translateY(0);
}

.label {
  display: inline-block;
  font-size: 0.75rem;
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-bottom: 1.5rem;
  opacity: 0.6;
}

h1 {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2.5rem, 5vw, 4rem);
  margin-bottom: 1.5rem;
}

.subtitle {
  font-size: 1rem;
  letter-spacing: 0.5px;
  opacity: 0.7;
  max-width: 600px;
  margin: 0 auto;
}

.loading,
.error,
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1rem;
  text-align: center;
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

.error {
  color: #c33;
}

.error button {
  margin-top: 1rem;
  padding: 0.8rem 2rem;
  background: #000;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  transition: background 0.3s ease;
}

.error button:hover {
  background: #333;
}

.empty {
  color: #666;
}

.reset-btn {
  margin-top: 1rem;
  padding: 0.8rem 2rem;
  background: #000;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 0.85rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  transition: all 0.3s ease;
}

.reset-btn:hover {
  background: #333;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 4rem 3rem;
  opacity: 0;
  transition: opacity 0.8s ease 0.3s;
}

.grid.show {
  opacity: 1;
}

.product-wrapper {
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.grid.show .product-wrapper {
  opacity: 1;
  transform: translateY(0);
}

@media (max-width: 968px) {
  .productos {
    padding: 6rem 5vw 4rem;
  }
  
  .header {
    margin-bottom: 2rem;
  }
  
  .grid {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 3rem 2rem;
  }
}

@media (max-width: 768px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 2.5rem 1.5rem;
  }
}

@media (max-width: 480px) {
  .grid {
    grid-template-columns: 1fr;
    gap: 2.5rem;
  }
}
</style>