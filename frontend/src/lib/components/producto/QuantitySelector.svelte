<script>
  export let quantity = 1;
  
  const increaseQty = () => {
    quantity = Math.min(quantity + 1, 10);
  };
  
  const decreaseQty = () => {
    quantity = Math.max(quantity - 1, 1);
  };
</script>

<div class="quantity-selector">
  <span class="qty-label">Cantidad</span>
  <div class="qty-controls">
    <button class="qty-btn" on:click={decreaseQty}>−</button>
    <span class="qty-value">{quantity}</span>
    <button class="qty-btn" on:click={increaseQty}>+</button>
  </div>
</div>

<style>
.quantity-selector {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
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

.qty-btn:hover {
  opacity: 0.6;
}

.qty-value {
  font-size: 1.1rem;
  min-width: 30px;
  text-align: center;
}
</style>