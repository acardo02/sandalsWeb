<script>
  import { onMount } from 'svelte';
  import ProductCard from '$lib/components/ProductCard.svelte';
  import CategoryFilter from '$lib/components/CategoryFilter.svelte';
  
  let products = [];
  let categories = [];
  let selectedCategory = 'Todos';
  let searchTerm = '';
  
  // Control de estado
  let isFirstLoad = true; // Nueva variable para controlar solo la primera vez
  let error = '';
  let visible = false;
  let searchTimeout;

  async function fetchProducts() {
    // ELIMINADO: loading = true; 
    // Ya no bloqueamos la pantalla al buscar.
    
    try {
      let url = `http://127.0.0.1:8000/products/?limit=100`;
      
      if (selectedCategory !== 'Todos') {
        url += `&category=${encodeURIComponent(selectedCategory)}`;
      }
      
      if (searchTerm) {
        url += `&search=${encodeURIComponent(searchTerm)}`;
      }

      const res = await fetch(url);
      if (res.ok) {
        products = await res.json();
        
        if (categories.length === 0) {
           const unique = [...new Set(products.map(p => p.category))];
           categories = unique.filter(c => c);
        }
      } else {
        error = 'Error al obtener datos';
      }
    } catch (err) {
      error = 'Error de conexión: ' + err.message;
    } finally {
      // Solo desactivamos el loader si era la primera carga
      if (isFirstLoad) {
        isFirstLoad = false;
        setTimeout(() => visible = true, 100);
      }
    }
  }

  onMount(() => {
    fetchProducts();
  });

  function handleFilterChange(category) {
    selectedCategory = category;
    fetchProducts();
  }

  function handleSearchInput() {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      fetchProducts();
    }, 300); // Bajamos un poco el tiempo para que se sienta más ágil
  }
</script>

<section class="productos">
  <div class="header {visible ? 'show' : ''}">
    <span class="label">Colección completa</span>
    <h1>Nuestros Productos</h1>
    
    <div class="search-container">
      <input 
        type="text" 
        placeholder="Buscar..." 
        bind:value={searchTerm}
        on:input={handleSearchInput}
        class="search-input"
      />
      <span class="search-icon">🔍</span>
    </div>
  </div>

  {#if isFirstLoad}
    <div class="loading">
      <div class="spinner"></div>
      <p>Cargando colección...</p>
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

    {#if products.length === 0}
      <div class="empty">
        <p>No encontramos "{searchTerm}"</p>
        <button class="reset-btn" on:click={() => { searchTerm = ''; selectedCategory = 'Todos'; fetchProducts(); }}>
          Ver todo
        </button>
      </div>
    {:else}
      <div class="grid {visible ? 'show' : ''}">
        {#each products as product (product.id || product._id)}
          <div class="product-wrapper">
            <ProductCard {product} />
          </div>
        {/each}
      </div>
    {/if}
  {/if}
</section>

<style>
/* TUS ESTILOS SE MANTIENEN IGUAL, SOLO AGREGAMOS UNA PEQUEÑA MEJORA AL INPUT */

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
  display: flex;
  flex-direction: column;
  align-items: center;
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
  margin-bottom: 1rem;
  opacity: 0.6;
}

h1 {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2.5rem, 5vw, 4rem);
  margin-bottom: 2rem;
}

.search-container {
  position: relative;
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}

.search-input {
  width: 100%;
  padding: 1rem 2rem 1rem 0; /* Espacio para el icono */
  font-size: 1.1rem; /* Un poco más grande para mejor lectura */
  font-family: 'Playfair Display', serif; /* Tipografía más estética al escribir */
  background: transparent;
  border: none;
  border-bottom: 1px solid #ddd;
  transition: all 0.3s ease;
  text-align: center;
  color: #333;
}

.search-input:focus {
  outline: none;
  border-bottom-color: #000;
}

.search-input::placeholder {
  color: #ccc;
  font-style: italic;
  font-family: 'Playfair Display', serif;
}

.search-icon {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0.3;
  pointer-events: none;
  font-size: 1rem;
}

.loading, .error, .empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1rem;
  text-align: center;
  color: #666;
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
  opacity: 1; /* Quitamos la opacidad inicial para que no parpadee */
}

.product-wrapper {
  animation: fadeIn 0.5s ease forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 968px) {
  .productos { padding: 6rem 5vw 4rem; }
  .grid { grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 3rem 2rem; }
}

@media (max-width: 768px) {
  .grid { grid-template-columns: repeat(2, 1fr); gap: 2.5rem 1.5rem; }
}

@media (max-width: 480px) {
  .grid { grid-template-columns: 1fr; gap: 2.5rem; }
}
</style>