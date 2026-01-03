<script>
  import { addToCart } from '$lib/stores/cartStore';
  export let product;
  
  const API_URL = 'http://localhost:8000';
  let isAdding = false;
  
  const handleAddToCart = () => {
    isAdding = true;
    addToCart(product);
    
    setTimeout(() => {
      isAdding = false;
    }, 1000);
  };
  
  $: imageUrl = product.image_url ? `${API_URL}${product.image_url}` : product.image || '/placeholder.png';
  $: productLink = product.id ? `/producto/${product.id}` : `/producto/${product.id}`;
</script>

<a href={productLink} class="card">
  <div class="image-wrapper">
    <img src={imageUrl} alt={product.name} />
    <div class="overlay">
      <span class="view-details">Ver detalles</span>
    </div>
  </div>

  <div class="info">
    <h3>{product.name}</h3>
    <p class="price">${product.price}</p>
  </div>

  <button 
    class="add-btn {isAdding ? 'adding' : ''}" 
    on:click|preventDefault={handleAddToCart}
    disabled={isAdding || product.stock === 0}
  >
    <span>{isAdding ? 'Agregado ✓' : product.stock === 0 ? 'Agotado' : 'Agregar al carrito'}</span>
  </button>
</a>

<style>
.card {
  display: flex;
  flex-direction: column;
  text-decoration: none;
  color: inherit;
  transition: transform 0.3s ease;
}

.card:hover {
  transform: translateY(-5px);
}

.image-wrapper {
  position: relative;
  overflow: hidden;
  background: #f5f5f5;
  margin-bottom: 1.2rem;
}

.image-wrapper::before {
  content: '';
  display: block;
  padding-bottom: 130%;
}

img {
  position: absolute;
  top: 0;
  left: 0;
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

.view-details {
  color: white;
  font-size: 0.75rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  border: 1px solid white;
  padding: 0.7rem 1.5rem;
  transform: translateY(10px);
  transition: all 0.4s ease;
  background: rgba(0, 0, 0, 0);
  pointer-events: auto;
  cursor: pointer;
}

.card:hover .view-details {
  transform: translateY(0);
}

.view-details:hover {
  background: rgba(255, 255, 255, 0.2);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.9);
}

.info {
  margin-bottom: 1rem;
}

h3 {
  font-family: 'Playfair Display', serif;
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
  transition: letter-spacing 0.3s ease;
}

.card:hover h3 {
  letter-spacing: 0.5px;
}

.price {
  font-size: 0.95rem;
  font-weight: 500;
  opacity: 0.8;
  margin-bottom: 0.3rem;
}

.add-btn {
  width: 100%;
  background: #000;
  color: white;
  border: 1px solid #000;
  padding: 0.9rem;
  font-size: 0.75rem;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.add-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: white;
  transition: left 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}

.add-btn:hover:not(:disabled) {
  color: #000;
}

.add-btn:hover:not(:disabled)::before {
  left: 0;
}

.add-btn span {
  position: relative;
  z-index: 1;
}

.add-btn.adding {
  background: white;
  color: #000;
  pointer-events: none;
}

.add-btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

@media (max-width: 768px) {
  h3 {
    font-size: 1.1rem;
  }
  
  .add-btn {
    padding: 0.8rem;
    font-size: 0.7rem;
  }
}
</style>