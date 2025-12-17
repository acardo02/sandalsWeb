<script>
  export let product;
</script>

<a href="/producto/{product.id}" class="card">
  <div class="image-wrapper">
    <img src={product.image} alt={product.name} />
    <div class="overlay">
      <span class="view-text">Ver producto</span>
    </div>
  </div>
  
  <div class="info">
    <h3>{product.name}</h3>
    <p class="price">€{product.price}</p>
  </div>
</a>

<style>
.card {
  display: flex;
  flex-direction: column;
  text-decoration: none;
  color: inherit;
  transition: transform 0.4s ease;
}

.card:hover {
  transform: translateY(-8px);
}

.image-wrapper {
  position: relative;
  overflow: hidden;
  background: #f5f5f5;
  aspect-ratio: 3/4;
}

.image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(1);
  transition: all 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

.card:hover img {
  transform: scale(1.05);
  filter: grayscale(0.3);
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.4s ease;
  pointer-events: none;
}

.card:hover .overlay {
  opacity: 1;
}

.view-text {
  color: white;
  font-size: 0.75rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  border: 1px solid white;
  padding: 0.8rem 2rem;
  background: rgba(0, 0, 0, 0);
  transition: all 0.3s ease;
  pointer-events: auto;
  cursor: pointer;
}

.view-text:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.9);
}

.info {
  margin-top: 1.5rem;
  text-align: center;
}

h3 {
  font-family: 'Playfair Display', serif;
  font-size: 1.3rem;
  margin-bottom: 0.5rem;
}

.price {
  font-size: 0.95rem;
  font-weight: 500;
  opacity: 0.7;
}

@media (max-width: 640px) {
  h3 {
    font-size: 1.1rem;
  }
}
</style>