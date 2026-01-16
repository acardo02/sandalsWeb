<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { wishlist as wishlistApi, auth } from '$lib/api';
  import { addToCart } from '$lib/stores/cartStore';

  let products = [];
  let loading = true;
  let error = '';

  const loadWishlist = async () => {
    try {
      await auth.getMe();
      products = await wishlistApi.getProducts();
    } catch (err) {
      if (err.message.includes('credenciales') || err.message.includes('401')) {
        goto('/login?redirect=/favoritos');
        return;
      }
      error = 'Error al cargar favoritos';
    } finally {
      loading = false;
    }
  };

  const removeFromWishlist = async (productId) => {
    try {
      await wishlistApi.remove(productId);
      products = products.filter(p => p.id !== productId);
    } catch (err) {
      console.error('Error removing from wishlist:', err);
    }
  };

  const handleAddToCart = (product) => {
    addToCart({
      id: product.id,
      name: product.name,
      price: product.base_price,
      image: product.main_image
    }, 1);
  };

  onMount(loadWishlist);
</script>

<svelte:head>
  <title>Mis Favoritos | CALERO</title>
</svelte:head>

<section class="wishlist-page">
  <h1>Mis Favoritos</h1>

  {#if loading}
    <div class="loading">
      <div class="spinner"></div>
      <p>Cargando...</p>
    </div>
  {:else if error}
    <div class="error">
      <p>{error}</p>
      <a href="/productos" class="btn">Ver Productos</a>
    </div>
  {:else if products.length === 0}
    <div class="empty">
      <svg viewBox="0 0 24 24" width="64" height="64" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
      </svg>
      <h2>Tu lista de favoritos está vacía</h2>
      <p>Explora nuestra colección y guarda tus productos favoritos</p>
      <a href="/productos" class="btn-primary">Ver Productos</a>
    </div>
  {:else}
    <div class="wishlist-grid">
      {#each products as product}
        <div class="wishlist-item">
          <a href="/producto/{product.id}" class="product-image">
            <img src={product.main_image || '/placeholder.png'} alt={product.name} />
            {#if !product.in_stock}
              <span class="out-of-stock-badge">Agotado</span>
            {/if}
          </a>

          <div class="product-info">
            <a href="/producto/{product.id}" class="product-name">{product.name}</a>
            <p class="product-price">${product.base_price.toFixed(2)}</p>
          </div>

          <div class="actions">
            {#if product.in_stock}
              <button class="add-cart-btn" on:click={() => handleAddToCart(product)}>
                Agregar al Carrito
              </button>
            {:else}
              <button class="add-cart-btn" disabled>Sin Stock</button>
            {/if}

            <button
              class="remove-btn"
              on:click={() => removeFromWishlist(product.id)}
              title="Quitar de favoritos"
            >
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
              </svg>
            </button>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</section>

<style>
.wishlist-page {
  padding: 8rem 5vw 4rem;
  min-height: 100vh;
  background: #fafafa;
}

h1 {
  font-family: 'Playfair Display', serif;
  font-size: 2.5rem;
  text-align: center;
  margin-bottom: 3rem;
}

.loading, .empty, .error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
  gap: 1rem;
  text-align: center;
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

.empty svg {
  opacity: 0.3;
  margin-bottom: 1rem;
}

.empty h2 {
  font-family: 'Playfair Display', serif;
  font-size: 1.8rem;
}

.empty p {
  color: #666;
  margin-bottom: 1rem;
}

.btn-primary {
  display: inline-block;
  background: #000;
  color: white;
  padding: 1rem 2rem;
  text-decoration: none;
  text-transform: uppercase;
  letter-spacing: 1px;
  font-size: 0.85rem;
  transition: all 0.3s ease;
}

.btn-primary:hover {
  background: #333;
}

.wishlist-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.wishlist-item {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.wishlist-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.1);
}

.product-image {
  display: block;
  position: relative;
  aspect-ratio: 4/5;
  overflow: hidden;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.wishlist-item:hover .product-image img {
  transform: scale(1.05);
}

.out-of-stock-badge {
  position: absolute;
  top: 1rem;
  left: 1rem;
  background: #c62828;
  color: white;
  padding: 0.3rem 0.8rem;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.product-info {
  padding: 1.5rem;
  text-align: center;
}

.product-name {
  display: block;
  font-family: 'Playfair Display', serif;
  font-size: 1.2rem;
  color: #000;
  text-decoration: none;
  margin-bottom: 0.5rem;
}

.product-name:hover {
  text-decoration: underline;
}

.product-price {
  font-size: 1.1rem;
  font-weight: 500;
}

.actions {
  display: flex;
  gap: 0.5rem;
  padding: 0 1.5rem 1.5rem;
}

.add-cart-btn {
  flex: 1;
  padding: 0.9rem;
  background: #000;
  color: white;
  border: none;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.add-cart-btn:hover:not(:disabled) {
  background: #333;
}

.add-cart-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.remove-btn {
  padding: 0.9rem;
  background: white;
  border: 1px solid #ddd;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.remove-btn:hover {
  border-color: #c62828;
  color: #c62828;
}

@media (max-width: 768px) {
  .wishlist-page {
    padding: 6rem 1rem 2rem;
  }

  h1 {
    font-size: 2rem;
  }

  .wishlist-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1rem;
  }

  .product-info {
    padding: 1rem;
  }

  .actions {
    flex-direction: column;
    padding: 0 1rem 1rem;
  }
}
</style>
