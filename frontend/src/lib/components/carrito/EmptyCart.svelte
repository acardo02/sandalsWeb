<script>
  export let visible = false;
</script>

<div class="empty-cart {visible ? 'show' : ''}">
  <div class="empty-icon">🛒</div>
  <h2>Tu carrito está vacío</h2>
  <p>Descubre nuestra colección y encuentra tu próxima pieza favorita</p>
  <a href="/productos" class="shop-btn">Explorar productos</a>
</div>

<style>
.empty-cart {
  text-align: center;
  padding: 6rem 2rem;
  max-width: 600px;
  margin: 0 auto;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.8s cubic-bezier(0.16, 1, 0.3, 1) 0.2s;
}

.empty-cart.show {
  opacity: 1;
  transform: translateY(0);
}

.empty-icon {
  font-size: 5rem;
  margin-bottom: 2rem;
  opacity: 0.3;
}

h2 {
  font-family: 'Playfair Display', serif;
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

p {
  color: #666;
  margin-bottom: 3rem;
  font-size: 1.05rem;
  line-height: 1.6;
}

.shop-btn {
  display: inline-block;
  background: #000;
  color: white;
  padding: 1.2rem 3rem;
  text-decoration: none;
  font-size: 0.8rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  transition: all 0.3s ease;
  border: 1px solid #000;
}

.shop-btn:hover {
  background: white;
  color: #000;
}
</style>
