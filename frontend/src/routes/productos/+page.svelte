<script>
  import { onMount } from 'svelte';
  import { products } from '$lib/data/products';
  import ProductCard from '$lib/components/ProductCard.svelte';
  
  let visible = false;
  
  onMount(() => {
    setTimeout(() => visible = true, 200);
  });
</script>

<section class="productos">
  <div class="header {visible ? 'show' : ''}">
    <span class="label">Colección completa</span>
    <h1>Todos los productos</h1>
    <p class="subtitle">Descubre cada pieza de nuestra selección curada</p>
  </div>

  <div class="grid {visible ? 'show' : ''}">
    {#each products as product, i}
      <div class="product-wrapper" style="transition-delay: {i * 0.05}s">
        <ProductCard {product} />
      </div>
    {/each}
  </div>
</section>

<style>
.productos {
  padding: 8rem 10vw 6rem;
  min-height: 100vh;
  background: linear-gradient(to bottom, #fafafa 0%, #ffffff 100%);
}

.header {
  text-align: center;
  margin-bottom: 6rem;
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
    margin-bottom: 4rem;
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