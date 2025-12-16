<script>
  export let image;
  export let name;
  export let category;
  export let price;
</script>

<div class="product">
  <div class="image">
    <img src={image} alt={name} />
  </div>

  <div class="info">
    <h3>{name}</h3>
    <span class="category">{category}</span>
    <span class="price">€{price}</span>
  </div>
</div>

<style>
.product {
  display: flex;
  flex-direction: column;
}

.image {
  overflow: hidden;
}

.image img {
  width: 100%;
  filter: grayscale(1);
  transition: transform 1.2s ease;
}

.product:hover img {
  transform: scale(1.05);
}

.info {
  margin-top: 1.5rem;
}

h3 {
  font-family: 'Playfair Display', serif;
  font-size: 1.4rem;
}

.category {
  display: block;
  margin-top: 0.3rem;
  font-size: 0.7rem;
  letter-spacing: 1.5px;
}

.price {
  display: block;
  margin-top: 0.5rem;
  font-size: 0.8rem;
}
</style>
