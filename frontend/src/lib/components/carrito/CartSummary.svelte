<script>
  import { clearCart } from '$lib/stores/cartStore';
  
  export let total = 0;
</script>

<div class="cart-summary">
  <h2>Resumen del pedido</h2>
  
  <div class="summary-row">
    <span>Subtotal</span>
    <span>€{total.toFixed(2)}</span>
  </div>
  
  <div class="summary-row">
    <span>Envío</span>
    <span>Gratis</span>
  </div>
  
  <div class="divider"></div>
  
  <div class="summary-row total">
    <span>Total</span>
    <span>€{total.toFixed(2)}</span>
  </div>
  
  <a href="/checkout" class="checkout-btn">
    Proceder al pago
  </a>
  
  <button class="clear-btn" on:click={clearCart}>
    Vaciar carrito
  </button>
</div>

<style>
.cart-summary {
  background: white;
  padding: 2.5rem;
  height: fit-content;
  position: sticky;
  top: 2rem;
}

h2 {
  font-family: 'Playfair Display', serif;
  font-size: 1.8rem;
  margin-bottom: 2rem;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1.2rem;
  font-size: 0.95rem;
}

.summary-row.total {
  font-size: 1.3rem;
  font-weight: 600;
  margin-top: 1rem;
}

.divider {
  width: 100%;
  height: 1px;
  background: #e5e5e5;
  margin: 1.5rem 0;
}

.checkout-btn {
  display: block;
  width: 100%;
  background: #000;
  color: white;
  padding: 1.3rem;
  text-align: center;
  text-decoration: none;
  font-size: 0.8rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-top: 2rem;
  margin-bottom: 1rem;
  transition: all 0.3s ease;
  border: 1px solid #000;
}

.checkout-btn:hover {
  background: white;
  color: #000;
}

.clear-btn {
  width: 100%;
  background: transparent;
  color: #999;
  border: 1px solid #ddd;
  padding: 1rem;
  font-size: 0.75rem;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.3s ease;
}

.clear-btn:hover {
  color: #000;
  border-color: #000;
}

@media (max-width: 968px) {
  .cart-summary {
    position: relative;
    top: 0;
  }
}
</style>