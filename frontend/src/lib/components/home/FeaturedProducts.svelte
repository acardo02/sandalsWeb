<script>
  import FeaturedProductCard from './FeaturedProductCard.svelte';
  
  const featuredProducts = [
    {
      id: 1,
      image: '/images/sandalia1.jpg',
      name: 'Sandalia Leather',
      price: '215'
    },
    {
      id: 2,
      image: '/images/sandalia2.jpg',
      name: 'Sandalia Minimal',
      price: '189'
    },
    {
      id: 3,
      image: '/images/tenis1.jpg',
      name: 'Tenis Essential',
      price: '165'
    }
  ];
</script>

<section class="featured">
  <div class="container">
    <div class="products-grid">
      {#each featuredProducts as product}
        <FeaturedProductCard {product} />
      {/each}
    </div>
  </div>
</section>

<style>
.featured {
  padding: 4rem 10vw;
  background: #fafafa;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 4rem;
}

@media (max-width: 968px) {
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 3rem;
  }
}

@media (max-width: 640px) {
  .featured {
    padding: 3rem 5vw;
  }
  
  .products-grid {
    grid-template-columns: 1fr;
    gap: 2.5rem;
  }
}
</style>