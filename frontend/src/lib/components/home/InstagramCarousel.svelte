<script>
  import { onMount } from 'svelte';
  
  // Imágenes de ejemplo - reemplaza con tus propias imágenes
  const instagramImages = [
    '/images/insta1.jpg',
    '/images/insta2.jpg',
    '/images/insta3.jpg',
    '/images/insta4.jpg',
    '/images/insta5.jpg',
    '/images/insta6.jpg'
  ];
  
  let currentIndex = 0;
  /** @type {ReturnType<typeof setInterval> | null} */
  let autoplayInterval = null;
  
  function nextSlide() {
    currentIndex = (currentIndex + 1) % instagramImages.length;
  }
  
  /**
   * @param {number} index
   */
  function goToSlide(index) {
    currentIndex = index;
  }
  
  function prevSlide() {
    currentIndex = currentIndex === 0 ? instagramImages.length - 1 : currentIndex - 1;
  }
  
  onMount(() => {
    // Autoplay cada 4 segundos
    autoplayInterval = setInterval(nextSlide, 4000);
    
    return () => {
      if (autoplayInterval) {
        clearInterval(autoplayInterval);
      }
    };
  });
</script>

<section class="instagram-section">
  <div class="container">
    <div class="header">
      <h2>VIVE CON NOSOTROS</h2>
      <a href="https://instagram.com/tu_cuenta" target="_blank" rel="noopener noreferrer" class="instagram-link">
        @tu_cuenta
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>
          <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/>
          <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/>
        </svg>
      </a>
    </div>
    
    <div class="carousel">
      <div class="carousel-track" style="transform: translateX(-{currentIndex * 100}%)">
        {#each instagramImages as image, i}
          <div class="carousel-slide">
            <img src={image} alt="Instagram post {i + 1}" />
            <div class="slide-overlay">
              <a href="https://instagram.com/tu_cuenta" target="_blank" rel="noopener noreferrer" class="overlay-link">
                Ver en Instagram
              </a>
            </div>
          </div>
        {/each}
      </div>
      
      <button class="carousel-btn prev" on:click={prevSlide} aria-label="Anterior">
        ‹
      </button>
      
      <button class="carousel-btn next" on:click={nextSlide} aria-label="Siguiente">
        ›
      </button>
      
      <div class="carousel-dots">
        {#each instagramImages as _, i}
          <button 
            class="dot {i === currentIndex ? 'active' : ''}" 
            on:click={() => goToSlide(i)}
            aria-label="Ir a imagen {i + 1}"
          ></button>
        {/each}
      </div>
    </div>
  </div>
</section>

<style>
.instagram-section {
  padding: 6rem 10vw;
  background: linear-gradient(to bottom, #ffffff 0%, #fafafa 100%);
}

.header {
  text-align: center;
  margin-bottom: 4rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

h2 {
  font-family: 'Playfair Display', serif;
  font-size: 2.5rem;
  letter-spacing: 2px;
}

.instagram-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  letter-spacing: 1px;
  text-decoration: none;
  color: #000;
  transition: opacity 0.3s ease;
}

.instagram-link:hover {
  opacity: 0.7;
}

.carousel {
  position: relative;
  overflow: hidden;
  border-radius: 4px;
  max-width: 1200px;
  margin: 0 auto;
}

.carousel-track {
  display: flex;
  transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.carousel-slide {
  min-width: 100%;
  aspect-ratio: 16/9;
  position: relative;
  overflow: hidden;
}

.carousel-slide img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(0.3);
  transition: all 0.6s ease;
}

.carousel-slide:hover img {
  transform: scale(1.05);
  filter: grayscale(0);
}

.slide-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.4s ease;
}

.carousel-slide:hover .slide-overlay {
  opacity: 1;
}

.overlay-link {
  color: white;
  font-size: 0.85rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  text-decoration: none;
  border: 1px solid white;
  padding: 1rem 2rem;
  transition: all 0.3s ease;
}

.overlay-link:hover {
  background: white;
  color: #000;
}

.carousel-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(255, 255, 255, 0.9);
  border: none;
  width: 50px;
  height: 50px;
  font-size: 2rem;
  cursor: pointer;
  transition: all 0.3s ease;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
}

.carousel-btn:hover {
  background: white;
}

.carousel-btn.prev {
  left: 1rem;
}

.carousel-btn.next {
  right: 1rem;
}

.carousel-dots {
  position: absolute;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 0.8rem;
  z-index: 2;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 0;
}

.dot:hover {
  background: rgba(255, 255, 255, 0.8);
}

.dot.active {
  background: white;
  transform: scale(1.2);
}

@media (max-width: 968px) {
  .instagram-section {
    padding: 4rem 5vw;
  }
  
  h2 {
    font-size: 2rem;
  }
  
  .carousel-btn {
    width: 40px;
    height: 40px;
    font-size: 1.5rem;
  }
}

@media (max-width: 640px) {
  .instagram-section {
    padding: 3rem 5vw;
  }
  
  h2 {
    font-size: 1.8rem;
  }
  
  .carousel-slide {
    aspect-ratio: 1/1;
  }
  
  .carousel-btn {
    width: 35px;
    height: 35px;
    font-size: 1.3rem;
  }
  
  .carousel-btn.prev {
    left: 0.5rem;
  }
  
  .carousel-btn.next {
    right: 0.5rem;
  }
  
  .carousel-dots {
    bottom: 1rem;
  }
  
  .dot {
    width: 8px;
    height: 8px;
  }
}
</style>