<script>
  import { onMount } from 'svelte';
  
  let visible = false;
  
  onMount(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            visible = true;
          }
        });
      },
      { threshold: 0.3 }
    );
    
    const section = document.querySelector('.craft-section');
    if (section) observer.observe(section);
    
    return () => observer.disconnect();
  });
</script>

<section class="craft-section">
  <div class="craft-image {visible ? 'visible' : ''}">
    <img src="/images/editorial.jpg" alt="Nuestro proceso artesanal" />
    <div class="craft-overlay">
      <h2>NUESTRO PROCESO</h2>
    </div>
  </div>
  
  <div class="craft-content {visible ? 'visible' : ''}">
    <p class="craft-intro">
      Desde bocetos cuidados hasta cuero perfectamente elegido, cada 
      sandalia nace con propósito. Honramos técnicas tradicionales 
      mientras abrazamos líneas contemporáneas que trascienden el tiempo.
    </p>
    
    <div class="craft-details">
      <div class="detail">
        <h3>DISEÑO REFLEXIVO</h3>
        <p>Cada silueta es deliberada, reducida a su forma más pura mientras mantiene un confort excepcional.</p>
      </div>
      
      <div class="detail">
        <h3>ELABORACIÓN ARTESANAL</h3>
        <p>Manos expertas moldean cada pieza, asegurando que la calidad sea evidente en cada costura.</p>
      </div>
      
      <div class="detail">
        <h3>MATERIALES NATURALES</h3>
        <p>Seleccionamos cuero premium y materiales sostenibles que envejecen bellamente con el tiempo.</p>
      </div>
    </div>
  </div>
</section>

<style>
.craft-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  min-height: 90vh;
  background: #ffffff;
}

.craft-image {
  position: relative;
  overflow: hidden;
  opacity: 0;
  transform: translateX(-50px);
  transition: all 1.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.craft-image.visible {
  opacity: 1;
  transform: translateX(0);
}

.craft-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: grayscale(0.5);
  transition: filter 0.8s ease;
}

.craft-image:hover img {
  filter: grayscale(0.2);
}

.craft-overlay {
  position: absolute;
  bottom: 3rem;
  left: 3rem;
  color: white;
  z-index: 2;
}

.craft-overlay h2 {
  font-family: 'Playfair Display', serif;
  font-size: 3rem;
  letter-spacing: 2px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.craft-content {
  padding: 6rem 5rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  opacity: 0;
  transform: translateX(50px);
  transition: all 1.2s cubic-bezier(0.16, 1, 0.3, 1) 0.2s;
}

.craft-content.visible {
  opacity: 1;
  transform: translateX(0);
}

.craft-intro {
  font-size: 1.1rem;
  line-height: 1.8;
  margin-bottom: 3rem;
  color: #333;
  font-weight: 300;
}

.craft-details {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.detail h3 {
  font-size: 0.75rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 0.8rem;
  color: #000;
}

.detail p {
  font-size: 0.95rem;
  line-height: 1.7;
  color: #666;
}

@media (max-width: 968px) {
  .craft-section {
    grid-template-columns: 1fr;
    min-height: auto;
  }
  
  .craft-overlay h2 {
    font-size: 2.5rem;
  }
  
  .craft-content {
    padding: 4rem 5vw;
  }
}

@media (max-width: 640px) {
  .craft-overlay {
    bottom: 2rem;
    left: 2rem;
  }
  
  .craft-overlay h2 {
    font-size: 2rem;
  }
  
  .craft-content {
    padding: 3rem 5vw;
  }
  
  .craft-intro {
    font-size: 1rem;
  }
}
</style>