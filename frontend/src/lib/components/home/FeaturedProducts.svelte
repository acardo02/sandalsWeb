<script lang="ts">
  import { onMount } from 'svelte';
  import FeaturedProductCard from './FeaturedProductCard.svelte';
  
  // Definimos la interfaz del producto
  interface Product {
    id: string;
    name: string;
    price: number;
    image: string;
  }

  let featuredProducts: Product[] = [];
  let loading = true;

  onMount(async () => {
    try {
      // Pedimos 3 productos aleatorios al backend
      const res = await fetch('http://127.0.0.1:8000/products/?limit=3&random_sample=true');
      if (res.ok) {
        const data = await res.json();
        featuredProducts = data.map((p: any) => ({
          id: p._id || p.id,
          name: p.name,
          image: p.image || '/images/placeholder.jpg', 
          price: p.price
        }));
      }
    } catch (error) {
      console.error("Error cargando productos", error);
    } finally {
      loading = false;
    }
  });
</script>

<section class="featured">
  <div class="container">
    
    <div class="section-header">
      <h2>Destacados</h2>
      <div class="line"></div>
    </div>

    {#if loading}
      <div class="loading">Cargando colección...</div>
    {:else}
      <div class="products-grid">
        {#each featuredProducts as product}
          <FeaturedProductCard {product} />
        {/each}
      </div>
    {/if}
  </div>
</section>

<style>
.featured {
  padding: 4rem 10vw;
  background: #fafafa;
  min-height: 500px;
}

/* --- ESTILOS DEL TÍTULO --- */
.section-header {
  text-align: center;
  margin-bottom: 4rem; /* Espacio antes de los productos */
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

h2 {
  font-family: 'Playfair Display', serif; /* Tu tipografía estética */
  font-size: 2.5rem;
  letter-spacing: 1px;
  color: #000;
  margin: 0;
}

.line {
  width: 60px;
  height: 1px;
  background-color: #000;
  opacity: 0.3;
}
/* -------------------------- */

.products-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 4rem;
}

.loading {
  text-align: center;
  font-family: 'Playfair Display', serif;
  font-style: italic;
  color: #999;
  padding: 4rem 0;
}

@media (max-width: 968px) {
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 3rem;
  }
}

@media (max-width: 640px) {
  .featured {
    padding: 3rem 5vw;
  }
  
  h2 {
    font-size: 2rem;
  }
  
  .products-grid {
    grid-template-columns: 1fr;
    gap: 2.5rem;
  }
}
</style>