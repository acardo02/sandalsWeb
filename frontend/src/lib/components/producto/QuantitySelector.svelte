<script>
  export let quantity = 1;
  export let maxStock = 10; // Stock máximo disponible
  
  const increaseQty = () => {
    if (quantity < maxStock) {
      quantity = quantity + 1;
    }
  };
  
  const decreaseQty = () => {
    quantity = Math.max(quantity - 1, 1);
  };
</script>

<div class="quantity-selector">
  <span class="qty-label">Cantidad</span>
  <div class="qty-controls">
    <button 
      class="qty-btn" 
      on:click={decreaseQty}
      disabled={quantity <= 1}
    >
      −
    </button>
    <span class="qty-value">{quantity}</span>
    <button 
      class="qty-btn" 
      on:click={increaseQty}
      disabled={quantity >= maxStock}
    >
      +
    </button>
  </div>
  {#if maxStock < 10}
    <span class="stock-warning">Solo {maxStock} disponibles</span>
  {/if}
</div>

<style>
.quantity-selector {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
  position: relative;
}

.qty-label {
  font-size: 0.85rem;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.qty-controls {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  border: 1px solid #ddd;
  padding: 0.5rem 1.5rem;
}

.qty-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.3s ease;
}

.qty-btn:hover:not(:disabled) {
  opacity: 0.6;
}

.qty-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.qty-value {
  font-size: 1.1rem;
  min-width: 30px;
  text-align: center;
}

.stock-warning {
  position: absolute;
  bottom: -1.5rem;
  right: 0;
  font-size: 0.75rem;
  color: #ff6b6b;
  font-style: italic;
}
</style>