<script>
  import { onMount } from 'svelte';
  import EditorialProduct from './EditorialProduct.svelte';
    import { goto } from '$app/navigation';

  function goToProducts() {
    goto('/productos');
  }
  
  let titleVisible = false;
  
  onMount(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            titleVisible = true;
          }
        });
      },
      { threshold: 0.5 }
    );
    
    const title = document.querySelector('.collection h2');
    if (title) observer.observe(title);
    
    return () => observer.disconnect();
  });
</script>

<section class="collection">
  <div class="header">
    <h2 class={titleVisible ? 'visible' : ''}>
      <span class="line"></span>
      Colección
      <span class="line"></span>
    </h2>
    <p class="subtitle {titleVisible ? 'visible' : ''}">
      Diseños atemporales que trascienden tendencias
    </p>
  </div>

  <div class="grid">
    <!-- Producto destacado -->
    <EditorialProduct
      image="/images/sandalia1.jpg"
      name="Sandalia Leather"
      category="MUJER"
      price="215"
    />

    <!-- Imagen editorial con overlay -->
    <div class="editorial-wrapper">
      <img
        class="editorial-image"
        src="/images/editorial.jpg"
        alt="Editorial"
      />
      <div class="editorial-overlay">
        <div class="editorial-text">
          <span class="editorial-label">Primavera 2025</span>
          <h3>Minimalismo<br/>esencial</h3>
        </div>
      </div>
    </div>

    <EditorialProduct
      image="/images/sandalia2.jpg"
      name="Sandalia Minimal"
      category="MUJER"
      price="189"
    />

    <EditorialProduct
      image="/images/tenis1.jpg"
      name="Tenis Essential"
      category="HOMBRE"
      price="165"
    />
  </div>
  
  <div class="explore-more">
  <button class="explore-btn" on:click={goToProducts}>
    Ver toda la colección
    <span class="arrow">↓</span>
  </button>
</div>
</section>

<style>
.collection {
  padding: 8rem 10vw 6rem;
  background: linear-gradient(to bottom, #fafafa 0%, #ffffff 100%);
}

.header {
  text-align: center;
  margin-bottom: 6rem;
}

h2 {
  font-family: 'Playfair Display', serif;
  font-size: 2.8rem;
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 2rem;
  opacity: 0;
  transform: translateY(30px);
  transition: all 1s cubic-bezier(0.16, 1, 0.3, 1);
}

h2.visible {
  opacity: 1;
  transform: translateY(0);
}

.line {
  width: 0;
  height: 1px;
  background: #000;
  transition: width 1s ease 0.5s;
}

h2.visible .line {
  width: 60px;
}

.subtitle {
  margin-top: 1.5rem;
  font-size: 0.95rem;
  letter-spacing: 0.5px;
  opacity: 0;
  transition: opacity 0.8s ease 0.8s;
  color: #666;
}

.subtitle.visible {
  opacity: 1;
}

.grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 5rem;
  position: relative;
}

.grid::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 1px;
  height: 80%;
  background: linear-gradient(
    to bottom,
    transparent,
    rgba(0,0,0,0.1) 50%,
    transparent
  );
  opacity: 0.5;
}

.editorial-wrapper {
  position: relative;
  overflow: hidden;
  cursor: pointer;
}

.editorial-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(1);
  transition: all 1.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.editorial-wrapper:hover .editorial-image {
  transform: scale(1.05);
  filter: grayscale(0.5);
}

.editorial-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    135deg,
    rgba(0,0,0,0.4) 0%,
    transparent 70%
  );
  opacity: 0;
  transition: opacity 0.6s ease;
  display: flex;
  align-items: flex-end;
  padding: 2rem;
}

.editorial-wrapper:hover .editorial-overlay {
  opacity: 1;
}

.editorial-text {
  color: white;
  transform: translateY(20px);
  transition: transform 0.6s ease;
}

.editorial-wrapper:hover .editorial-text {
  transform: translateY(0);
}

.editorial-label {
  display: block;
  font-size: 0.7rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
  opacity: 0.9;
}

.editorial-text h3 {
  font-family: 'Playfair Display', serif;
  font-size: 2rem;
  line-height: 1.2;
}

.explore-more {
  text-align: center;
  margin-top: 6rem;
}

.explore-btn {
  background: #000;
  color: white;
  border: 1px solid #000;
  padding: 1.2rem 3rem;
  font-size: 0.8rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  cursor: pointer;
  position: relative;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.explore-btn:hover {
  background: white;
  color: #000;
}

.explore-btn span {
  position: relative;
  z-index: 1;
}

.arrow {
  display: inline-block;
  margin-left: 1rem;
  transition: transform 0.3s ease;
}

.explore-btn:hover .arrow {
  transform: translateY(5px);
}

@media (max-width: 968px) {
  .grid {
    grid-template-columns: 1fr;
    gap: 3rem;
  }
  
  .grid::before {
    display: none;
  }
  
  h2 {
    font-size: 2.2rem;
  }
}

@media (max-width: 768px) {
  .collection {
    padding: 5rem 5vw 4rem;
  }
  
  .header {
    margin-bottom: 4rem;
  }
  
  h2 {
    font-size: 2rem;
    gap: 1rem;
  }
  
  .line {
    display: none;
  }
}
</style>