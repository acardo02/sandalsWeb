<script>
  import { onMount } from 'svelte';
  import { cart } from '$lib/stores/cartStore';
  import CartItem from '$lib/components/carrito/CartItem.svelte';
  import CartSummary from '$lib/components/carrito/CartSummary.svelte';
  import EmptyCart from '$lib/components/carrito/EmptyCart.svelte';
  
  let visible = false;
  
  $: total = $cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
  
  onMount(() => {
    setTimeout(() => visible = true, 200);
  });
</script>

<section class="carrito">
  <div class="header {visible ? 'show' : ''}">
    <h1>Tu carrito</h1>
    <a href="/productos" class="continue-shopping">← Seguir comprando</a>
  </div>

  {#if $cart.length === 0}
    <EmptyCart {visible} />
  {:else}
    <div class="cart-content {visible ? 'show' : ''}">
      <div class="cart-items">
        {#each $cart as item, i}
          <CartItem {item} index={i} />
        {/each}
      </div>

      <CartSummary {total} />
    </div>
  {/if}
</section>

<style>
.carrito {
  padding: 8rem 10vw 6rem;
  min-height: 100vh;
  background: linear-gradient(to bottom, #fafafa 0%, #ffffff 100%);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4rem;
  opacity: 0;
  transform: translateY(30px);
  transition: all 1s cubic-bezier(0.16, 1, 0.3, 1);
}

.header.show {
  opacity: 1;
  transform: translateY(0);
}

h1 {
  font-family: 'Playfair Display', serif;
  font-size: clamp(2.5rem, 5vw, 4rem);
}

.continue-shopping {
  color: #000;
  text-decoration: none;
  font-size: 0.85rem;
  letter-spacing: 1px;
  transition: opacity 0.3s ease;
}

.continue-shopping:hover {
  opacity: 0.6;
}

.cart-content {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 4rem;
  opacity: 0;
  transition: opacity 0.8s ease 0.2s;
}

.cart-content.show {
  opacity: 1;
}

.cart-items {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

@media (max-width: 1200px) {
  .cart-content {
    grid-template-columns: 1fr 350px;
    gap: 3rem;
  }
}

@media (max-width: 968px) {
  .carrito {
    padding: 6rem 5vw 4rem;
  }
  
  .cart-content {
    grid-template-columns: 1fr;
  }
  
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
}

@media (max-width: 768px) {
  h1 {
    font-size: 2.5rem;
  }
}
</style>