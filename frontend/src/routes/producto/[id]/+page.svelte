<script>
  import { onMount } from 'svelte';
  import { products } from '$lib/data/products';
  import { addToCart } from '$lib/stores/cartStore';
  import ProductImage from '$lib/components/producto/ProductImage.svelte';
  import QuantitySelector from '$lib/components/producto/QuantitySelector.svelte';
  import ProductFeatures from '$lib/components/producto/ProductFeatures.svelte';
  
  export let params;

  const product = products.find(p => p.id == params.id);
  
  let visible = false;
  let isAdding = false;
  let quantity = 1;
  
  const handleAddToCart = () => {
    if (!product) return;
    
    isAdding = true;
    
    for (let i = 0; i < quantity; i++) {
      addToCart(product);
    }
    
    setTimeout(() => {
      isAdding = false;
    }, 1500);
  };
  
  onMount(() => {
    setTimeout(() => visible = true, 200);
  });
</script>

{#if product}
  <section class="product-detail">
    <a href="/productos" class="back-link">
      ← Volver a productos
    </a>
    
    <div class="container {visible ? 'show' : ''}">
      <ProductImage image={product.image} name={product.name} />

      <div class="info-section">
        <span class="category">Colección 2025</span>
        <h1>{product.name}</h1>
        
        <p class="price">€{product.price}</p>
        
        <div class="description">
          <p>{product.description || 'Diseño minimalista y atemporal. Confeccionado con materiales de alta calidad para garantizar durabilidad y comodidad excepcionales.'}</p>
        </div>
        
        <div class="divider"></div>
        
        <QuantitySelector bind:quantity />
        
        <button 
          class="add-to-cart-btn {isAdding ? 'adding' : ''}" 
          on:click={handleAddToCart}
          disabled={isAdding}
        >
          {isAdding ? 'Agregado al carrito ✓' : 'Agregar al carrito'}
        </button>
        
        <ProductFeatures />
      </div>
    </div>
  </section>
{:else}
  <section class="not-found">
    <h2>Producto no encontrado</h2>
    <a href="/productos">Volver a productos</a>
  </section>
{/if}

<style>
.product-detail {
  padding: 8rem 10vw 6rem;
  min-height: 100vh;
  background: white;
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
  margin-bottom: 2rem;
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