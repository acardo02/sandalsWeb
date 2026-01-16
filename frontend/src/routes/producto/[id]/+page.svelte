<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { products as productsApi, reviews as reviewsApi, wishlist as wishlistApi } from '$lib/api';
  import { addToCart } from '$lib/stores/cartStore';
  import ProductImage from '$lib/components/producto/ProductImage.svelte';
  import QuantitySelector from '$lib/components/producto/QuantitySelector.svelte';
  import ProductFeatures from '$lib/components/producto/ProductFeatures.svelte';

  $: productId = $page.params.id;

  let product = null;
  let variants = null;
  let reviewSummary = null;
  let loading = true;
  let error = '';
  let visible = false;
  let isAdding = false;
  let quantity = 1;
  let stockError = '';

  // Variables para variantes
  let selectedSize = null;
  let selectedColor = null;
  let selectedVariant = null;
  let availableSizes = [];
  let availableColors = [];

  // Wishlist
  let isInWishlist = false;
  let wishlistLoading = false;

  // Calcular precio final
  $: finalPrice = selectedVariant
    ? product.base_price + (selectedVariant.price_adjustment || 0)
    : product?.base_price || 0;

  // Calcular stock disponible
  $: currentStock = selectedVariant
    ? selectedVariant.stock
    : (product?.stock || 0);

  // Encontrar variante seleccionada
  $: if (variants && selectedSize && selectedColor) {
    selectedVariant = variants.variants?.find(v =>
      v.size === selectedSize && v.color === selectedColor
    ) || null;
  } else if (variants && selectedSize && !availableColors.length) {
    selectedVariant = variants.variants?.find(v => v.size === selectedSize) || null;
  } else if (variants && selectedColor && !availableSizes.length) {
    selectedVariant = variants.variants?.find(v => v.color === selectedColor) || null;
  }

  // Verificar si puede agregar al carrito
  $: canAddToCart = product && !product.has_variants
    ? currentStock > 0
    : (selectedVariant && selectedVariant.stock > 0 && selectedVariant.is_available);

  const handleAddToCart = () => {
    if (!product) return;

    stockError = '';

    // Si tiene variantes, verificar que se haya seleccionado
    if (product.has_variants) {
      if (!selectedVariant) {
        stockError = 'Por favor selecciona talla y/o color';
        return;
      }
      if (selectedVariant.stock < quantity) {
        stockError = `Solo hay ${selectedVariant.stock} unidades disponibles`;
        return;
      }
    } else {
      if (quantity > currentStock) {
        stockError = `Solo hay ${currentStock} unidades disponibles`;
        return;
      }
    }

    isAdding = true;

    // Preparar item para el carrito
    const cartItem = {
      ...product,
      price: finalPrice,
      variant_sku: selectedVariant?.sku || null,
      variant_info: selectedVariant
        ? `${selectedVariant.size || ''} ${selectedVariant.color || ''}`.trim()
        : null,
      selected_variant: selectedVariant
    };

    const success = addToCart(cartItem, quantity);

    if (!success) {
      stockError = `No hay suficiente stock disponible`;
      isAdding = false;
      return;
    }

    setTimeout(() => {
      isAdding = false;
      quantity = 1;
    }, 1500);
  };

  const toggleWishlist = async () => {
    if (wishlistLoading) return;

    wishlistLoading = true;
    try {
      const result = await wishlistApi.toggle(product.id);
      isInWishlist = result.added;
    } catch (err) {
      console.error('Error toggling wishlist:', err);
    } finally {
      wishlistLoading = false;
    }
  };

  const checkWishlist = async () => {
    try {
      const result = await wishlistApi.check(product.id);
      isInWishlist = result.in_wishlist;
    } catch (err) {
      // Usuario no autenticado, ignorar
    }
  };

  const loadProduct = async () => {
    if (!productId) return;

    loading = true;
    try {
      product = await productsApi.getById(productId);

      // Cargar variantes si el producto las tiene
      if (product.has_variants) {
        variants = await productsApi.getVariants(productId);
        availableSizes = variants.available_sizes || [];
        availableColors = variants.available_colors || [];

        // Pre-seleccionar si solo hay una opcion
        if (availableSizes.length === 1) selectedSize = availableSizes[0];
        if (availableColors.length === 1) selectedColor = availableColors[0].name;
      }

      // Cargar resumen de reviews
      try {
        reviewSummary = await reviewsApi.getProductSummary(productId);
      } catch (err) {
        // Ignorar si no hay reviews
      }

      // Verificar wishlist
      checkWishlist();

    } catch (err) {
      error = 'Error al cargar el producto';
      console.error(err);
    } finally {
      loading = false;
      setTimeout(() => visible = true, 200);
    }
  };

  onMount(() => {
    if (productId) {
      loadProduct();
    }
  });

  // Recargar si cambia el ID del producto
  $: if (productId && !product && !loading) {
    loadProduct();
  }
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
        image={selectedVariant?.image_url || product.main_image || (product.images && product.images[0])}
        name={product.name}
      />

      <div class="info-section">
        <div class="header-row">
          <span class="category">{product.category || 'Colección 2025'}</span>
          <button
            class="wishlist-btn {isInWishlist ? 'active' : ''}"
            on:click={toggleWishlist}
            disabled={wishlistLoading}
            title={isInWishlist ? 'Quitar de favoritos' : 'Agregar a favoritos'}
          >
            {#if isInWishlist}
              <svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
            {:else}
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
            {/if}
          </button>
        </div>

        <h1>{product.name}</h1>

        <!-- Rating -->
        {#if reviewSummary && reviewSummary.total_reviews > 0}
          <div class="rating-summary">
            <div class="stars">
              {#each Array(5) as _, i}
                <span class="star {i < Math.round(reviewSummary.average_rating) ? 'filled' : ''}">★</span>
              {/each}
            </div>
            <span class="rating-text">
              {reviewSummary.average_rating.toFixed(1)} ({reviewSummary.total_reviews} {reviewSummary.total_reviews === 1 ? 'review' : 'reviews'})
            </span>
          </div>
        {/if}

        <p class="price">${finalPrice.toFixed(2)}</p>

        <!-- Stock status -->
        {#if product.has_variants}
          {#if selectedVariant}
            {#if selectedVariant.stock === 0 || !selectedVariant.is_available}
              <p class="stock-status out-of-stock">Agotado</p>
            {:else if selectedVariant.stock < 5}
              <p class="stock-status low-stock">¡Últimas {selectedVariant.stock} unidades!</p>
            {:else}
              <p class="stock-status in-stock">Disponible</p>
            {/if}
          {:else}
            <p class="stock-status select-variant">Selecciona una variante</p>
          {/if}
        {:else if currentStock === 0}
          <p class="stock-status out-of-stock">Agotado</p>
        {:else if currentStock < 5}
          <p class="stock-status low-stock">¡Últimas {currentStock} unidades!</p>
        {:else}
          <p class="stock-status in-stock">Disponible</p>
        {/if}

        <div class="description">
          <p>{product.description || 'Diseño minimalista y atemporal. Confeccionado con materiales de alta calidad para garantizar durabilidad y comodidad excepcionales.'}</p>
        </div>

        <!-- Selector de variantes -->
        {#if product.has_variants}
          <div class="variants-section">
            <!-- Selector de tallas US -->
            {#if availableSizes.length > 0}
              <div class="variant-group">
                <label class="variant-label">
                  Talla US: <strong>{selectedSize ? `US ${selectedSize}` : 'Seleccionar'}</strong>
                </label>
                <div class="size-options">
                  {#each availableSizes as size}
                    {@const sizeVariant = variants.variants?.find(v => v.size === size && (!selectedColor || v.color === selectedColor))}
                    {@const isAvailable = sizeVariant && sizeVariant.stock > 0 && sizeVariant.is_available}
                    <button
                      class="size-btn {selectedSize === size ? 'selected' : ''} {!isAvailable ? 'disabled' : ''}"
                      on:click={() => selectedSize = size}
                      disabled={!isAvailable}
                    >
                      US {size}
                    </button>
                  {/each}
                </div>
              </div>
            {/if}

            <!-- Selector de colores -->
            {#if availableColors.length > 0}
              <div class="variant-group">
                <label class="variant-label">
                  Color: <strong>{selectedColor || 'Seleccionar'}</strong>
                </label>
                <div class="color-options">
                  {#each availableColors as color}
                    {@const colorVariant = variants.variants?.find(v => v.color === color.name && (!selectedSize || v.size === selectedSize))}
                    {@const isAvailable = colorVariant && colorVariant.stock > 0 && colorVariant.is_available}
                    <button
                      class="color-btn {selectedColor === color.name ? 'selected' : ''} {!isAvailable ? 'disabled' : ''}"
                      style="background-color: {color.hex}"
                      on:click={() => selectedColor = color.name}
                      disabled={!isAvailable}
                      title={color.name}
                    >
                      {#if selectedColor === color.name}
                        <span class="check">✓</span>
                      {/if}
                    </button>
                  {/each}
                </div>
              </div>
            {/if}
          </div>
        {/if}

        <div class="divider"></div>

        {#if canAddToCart}
          <QuantitySelector
            bind:quantity
            maxStock={currentStock}
          />

          {#if stockError}
            <p class="stock-error">{stockError}</p>
          {/if}

          <button
            class="add-to-cart-btn {isAdding ? 'adding' : ''}"
            on:click={handleAddToCart}
            disabled={isAdding}
          >
            {isAdding ? 'Agregado al carrito ✓' : 'Agregar al carrito'}
          </button>
        {:else}
          <button class="add-to-cart-btn" disabled>
            {product.has_variants && !selectedVariant ? 'Selecciona una variante' : 'Producto agotado'}
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

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.category {
  font-size: 0.75rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  opacity: 0.6;
}

.wishlist-btn {
  background: none;
  border: 1px solid #ddd;
  border-radius: 50%;
  width: 44px;
  height: 44px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.wishlist-btn svg {
  width: 22px;
  height: 22px;
}

.wishlist-btn:hover {
  border-color: #000;
}

.wishlist-btn.active {
  background: #000;
  border-color: #000;
  color: white;
}

.wishlist-btn.active svg {
  fill: white;
}

h1 {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2.5rem, 4vw, 3.5rem);
  line-height: 1.1;
  margin-bottom: 1rem;
}

.rating-summary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.stars {
  display: flex;
  gap: 2px;
}

.star {
  color: #ddd;
  font-size: 1.1rem;
}

.star.filled {
  color: #f5a623;
}

.rating-text {
  font-size: 0.9rem;
  color: #666;
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

.stock-status.select-variant {
  background: #e3f2fd;
  color: #1565c0;
}

.description {
  margin-bottom: 2rem;
  line-height: 1.8;
  color: #555;
}

/* Variantes */
.variants-section {
  margin-bottom: 2rem;
}

.variant-group {
  margin-bottom: 1.5rem;
}

.variant-label {
  display: block;
  font-size: 0.9rem;
  margin-bottom: 0.8rem;
  color: #333;
}

.size-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.size-btn {
  min-width: 48px;
  height: 48px;
  padding: 0 1rem;
  border: 1px solid #ddd;
  background: white;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.size-btn:hover:not(:disabled) {
  border-color: #000;
}

.size-btn.selected {
  background: #000;
  color: white;
  border-color: #000;
}

.size-btn.disabled {
  opacity: 0.4;
  cursor: not-allowed;
  text-decoration: line-through;
}

.color-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.color-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.color-btn:hover:not(:disabled) {
  transform: scale(1.1);
}

.color-btn.selected {
  border-color: #000;
  box-shadow: 0 0 0 2px white, 0 0 0 4px #000;
}

.color-btn.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.color-btn .check {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 1rem;
  text-shadow: 0 1px 2px rgba(0,0,0,0.5);
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

  .size-btn {
    min-width: 44px;
    height: 44px;
  }

  .color-btn {
    width: 36px;
    height: 36px;
  }
}
</style>
