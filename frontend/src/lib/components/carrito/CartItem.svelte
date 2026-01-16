<script>
  import { removeFromCart, incrementQuantity, decrementQuantity } from '$lib/stores/cartStore';

  export let item;
  export let index = 0;

  $: itemImage = item.image || item.main_image || item.image_url || '/placeholder.png';

  const handleIncrement = () => {
    incrementQuantity(item.cartId);
  };

  const handleDecrement = () => {
    decrementQuantity(item.cartId);
  };

  const handleRemove = () => {
    removeFromCart(item.cartId);
  };
</script>

<div class="cart-item" style="transition-delay: {index * 0.05}s">
  <div class="item-image">
    <img src={itemImage} alt={item.name} />
  </div>

  <div class="item-info">
    <h3>{item.name}</h3>
    {#if item.variant_info}
      <p class="item-variant">{item.variant_info}</p>
    {/if}
    <p class="item-price">${item.price.toFixed(2)}</p>
  </div>

  <div class="item-quantity">
    <span class="qty-label">Cantidad</span>
    <div class="qty-controls">
      <button class="qty-btn" on:click={handleDecrement}>−</button>
      <span class="qty-value">{item.qty}</span>
      <button class="qty-btn" on:click={handleIncrement}>+</button>
    </div>
  </div>

  <div class="item-total">
    <span class="total-label">Total</span>
    <span class="total-value">${(item.price * item.qty).toFixed(2)}</span>
  </div>

  <button
    class="remove-btn"
    on:click={handleRemove}
    aria-label="Eliminar producto"
  >
    ✕
  </button>
</div>

<style>
.cart-item {
  display: grid;
  grid-template-columns: 120px 1fr auto auto auto;
  gap: 2rem;
  align-items: center;
  background: white;
  padding: 1.5rem;
  opacity: 0;
  transform: translateX(-20px);
  transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

:global(.cart-content.show) .cart-item {
  opacity: 1;
  transform: translateX(0);
}

.item-image {
  width: 120px;
  height: 150px;
  overflow: hidden;
  background: #f5f5f5;
}

.item-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.cart-item:hover .item-image img {
  transform: scale(1.05);
}

.item-info h3 {
  font-family: 'Playfair Display', serif;
  font-size: 1.3rem;
  margin-bottom: 0.3rem;
}

.item-variant {
  font-size: 0.85rem;
  color: #888;
  margin-bottom: 0.3rem;
}

.item-price {
  color: #666;
  font-size: 0.95rem;
}

.item-quantity,
.item-total {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.qty-label,
.total-label {
  font-size: 0.7rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  opacity: 0.6;
}

.qty-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.qty-btn {
  width: 28px;
  height: 28px;
  background: white;
  border: 1px solid #ddd;
  cursor: pointer;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.qty-btn:hover {
  background: #000;
  color: white;
  border-color: #000;
}

.qty-value {
  min-width: 24px;
  text-align: center;
  font-weight: 500;
}

.total-value {
  font-size: 1rem;
  font-weight: 500;
}

.remove-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.5rem;
  opacity: 0.4;
  transition: opacity 0.3s ease;
}

.remove-btn:hover {
  opacity: 1;
}

@media (max-width: 968px) {
  .cart-item {
    grid-template-columns: 100px 1fr;
    gap: 1.5rem;
    padding: 1.2rem;
  }

  .item-image {
    width: 100px;
    height: 130px;
    grid-row: 1 / 4;
  }

  .item-info {
    grid-column: 2;
  }

  .item-quantity {
    grid-column: 2;
    flex-direction: row;
    align-items: center;
    gap: 1rem;
  }

  .item-total {
    grid-column: 2;
    flex-direction: row;
    align-items: center;
    gap: 1rem;
  }

  .remove-btn {
    position: absolute;
    top: 1rem;
    right: 1rem;
  }

  .cart-item {
    position: relative;
  }
}
</style>
