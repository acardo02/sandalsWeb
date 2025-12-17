<script>
  import { removeFromCart } from '$lib/stores/cartStore';
  
  export let item;
  export let index = 0;
</script>

<div class="cart-item" style="transition-delay: {index * 0.05}s">
  <div class="item-image">
    <img src={item.image} alt={item.name} />
  </div>
  
  <div class="item-info">
    <h3>{item.name}</h3>
    <p class="item-price">€{item.price}</p>
  </div>
  
  <div class="item-quantity">
    <span class="qty-label">Cantidad:</span>
    <span class="qty-value">{item.qty}</span>
  </div>
  
  <div class="item-total">
    <span class="total-label">Total:</span>
    <span class="total-value">€{(item.price * item.qty).toFixed(2)}</span>
  </div>
  
  <button 
    class="remove-btn" 
    on:click={() => removeFromCart(item.id)}
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
  filter: grayscale(1);
  transition: filter 0.4s ease;
}

.cart-item:hover .item-image img {
  filter: grayscale(0.3);
}

.item-info h3 {
  font-family: 'Playfair Display', serif;
  font-size: 1.3rem;
  margin-bottom: 0.5rem;
}

.item-price {
  color: #666;
  font-size: 0.95rem;
}

.item-quantity,
.item-total {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.qty-label,
.total-label {
  font-size: 0.7rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  opacity: 0.6;
}

.qty-value,
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
  }
  
  .item-quantity,
  .item-total {
    grid-column: 2;
  }
  
  .remove-btn {
    grid-column: 2;
    justify-self: end;
  }
}
</style>