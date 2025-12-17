<script>
  import { cart } from '$lib/stores/cartStore';
</script>

<nav>
  <a href="/" class="logo">CALERO</a>

  <div class="links">
    <a href="/Nosotros">Nosotros</a>
    <a href="/productos">Productos</a>
    <a href="/carrito">Carrito ({$cart.length})</a>
  </div>
</nav>

<style>
nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #eee;
}
.logo {
  font-weight: bold;
  text-decoration: none;
  color: black;
}
.links a {
  margin-left: 1rem;
  text-decoration: none;
  color: black;
}
</style>
