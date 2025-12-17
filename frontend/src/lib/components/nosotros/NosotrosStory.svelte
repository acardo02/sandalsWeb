<script>
  import { onMount } from 'svelte';
  
  let visible = false;
  let imageVisible = false;
  
  onMount(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            visible = true;
            setTimeout(() => imageVisible = true, 400);
          }
        });
      },
      { threshold: 0.3 }
    );
    
    const section = document.querySelector('.story');
    if (section) observer.observe(section);
    
    return () => observer.disconnect();
  });
</script>

<section class="story">
  <div class="container">
    <div class="text-content {visible ? 'show' : ''}">
      <h2>Nuestra historia</h2>
      
      <div class="story-text">
        <p>
          Nuestro viaje comenzó con una pregunta simple: ¿puede el calzado ser 
          tanto una expresión de estilo como un compromiso con la autenticidad?
        </p>
        
        <p>
          Desde entonces, hemos dedicado cada diseño a encontrar ese equilibrio 
          perfecto entre forma y función, entre tendencia y atemporalidad. No 
          perseguimos la moda efímera; creamos piezas que trascienden temporadas.
        </p>
        
        <p>
          Cada sandalia, cada tenis, es el resultado de una obsesión por los 
          detalles imperceptibles que marcan la diferencia. Trabajamos con 
          artesanos que comparten nuestra visión: menos es más, siempre que ese 
          "menos" esté perfectamente ejecutado.
        </p>
      </div>
    </div>
    
    <div class="image-content {imageVisible ? 'show' : ''}">
      <div class="image-wrapper">
        <img src="/images/about-1.jpg" alt="Nuestro atelier" />
      </div>
      <div class="image-caption">
        <span>Nuestro atelier</span>
        <span class="year">Est. 2024</span>
      </div>
    </div>
  </div>
</section>

<style>
.story {
  padding: 10rem 10vw;
  background: white;
}

.container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8rem;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
}

.text-content {
  opacity: 0;
  transform: translateX(-40px);
  transition: all 1s cubic-bezier(0.16, 1, 0.3, 1);
}

.text-content.show {
  opacity: 1;
  transform: translateX(0);
}

h2 {
  font-family: 'Playfair Display', serif;
  font-size: 3rem;
  margin-bottom: 3rem;
  position: relative;
  padding-bottom: 1.5rem;
}

h2::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 80px;
  height: 2px;
  background: #000;
}

.story-text p {
  font-size: 1.05rem;
  line-height: 1.9;
  margin-bottom: 2rem;
  color: #333;
  letter-spacing: 0.2px;
}

.story-text p:last-child {
  margin-bottom: 0;
}

.image-content {
  opacity: 0;
  transform: translateX(40px);
  transition: all 1s cubic-bezier(0.16, 1, 0.3, 1) 0.2s;
}

.image-content.show {
  opacity: 1;
  transform: translateX(0);
}

.image-wrapper {
  position: relative;
  overflow: hidden;
  background: #f5f5f5;
}

.image-wrapper::before {
  content: '';
  display: block;
  padding-bottom: 120%;
}

.image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(1);
  transition: transform 0.8s ease, filter 0.8s ease;
}

.image-content:hover .image-wrapper img {
  transform: scale(1.05);
  filter: grayscale(0.7);
}

.image-caption {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.5rem;
  padding: 0 0.5rem;
  font-size: 0.85rem;
  letter-spacing: 1px;
}

.year {
  opacity: 0.5;
}

@media (max-width: 968px) {
  .story {
    padding: 6rem 5vw;
  }
  
  .container {
    grid-template-columns: 1fr;
    gap: 4rem;
  }
  
  h2 {
    font-size: 2.5rem;
  }
}
</style>