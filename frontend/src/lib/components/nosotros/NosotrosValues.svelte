<script>
  import { onMount } from 'svelte';
  
  let visible = false;
  
  const values = [
    {
      title: 'Diseño intencional',
      description: 'Cada línea, cada material, cada decisión tiene un propósito. No añadimos nada que no deba estar ahí.'
    },
    {
      title: 'Calidad atemporal',
      description: 'Creamos piezas que mejoran con el tiempo, no que se desgastan. La durabilidad es nuestro compromiso.'
    },
    {
      title: 'Minimalismo honesto',
      description: 'La simplicidad no es ausencia, es la perfección alcanzada cuando no hay nada más que quitar.'
    }
  ];
  
  onMount(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            visible = true;
          }
        });
      },
      { threshold: 0.2 }
    );
    
    const section = document.querySelector('.values');
    if (section) observer.observe(section);
    
    return () => observer.disconnect();
  });
</script>

<section class="values">
  <div class="container">
    <h2 class={visible ? 'show' : ''}>Nuestros valores</h2>
    
    <div class="values-grid">
      {#each values as value, i}
        <div class="value-card {visible ? 'show' : ''}" style="transition-delay: {i * 0.15}s">
          <div class="number">0{i + 1}</div>
          <h3>{value.title}</h3>
          <p>{value.description}</p>
        </div>
      {/each}
    </div>
  </div>
</section>

<style>
.values {
  padding: 10rem 10vw;
  background: #fafafa;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
}

h2 {
  font-family: 'Playfair Display', serif;
  font-size: 3rem;
  text-align: center;
  margin-bottom: 6rem;
  opacity: 0;
  transform: translateY(30px);
  transition: all 1s cubic-bezier(0.16, 1, 0.3, 1);
}

h2.show {
  opacity: 1;
  transform: translateY(0);
}

.values-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 4rem;
}

.value-card {
  background: white;
  padding: 3rem 2.5rem;
  position: relative;
  opacity: 0;
  transform: translateY(40px);
  transition: all 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

.value-card.show {
  opacity: 1;
  transform: translateY(0);
}

.value-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: #000;
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.value-card:hover::before {
  transform: scaleX(1);
}

.number {
  font-family: 'Playfair Display', serif;
  font-size: 3rem;
  opacity: 0.1;
  margin-bottom: 1.5rem;
  font-weight: 300;
}

h3 {
  font-family: 'Playfair Display', serif;
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
}

p {
  font-size: 0.95rem;
  line-height: 1.8;
  color: #555;
  letter-spacing: 0.2px;
}

@media (max-width: 968px) {
  .values {
    padding: 6rem 5vw;
  }
  
  h2 {
    font-size: 2.5rem;
    margin-bottom: 4rem;
  }
  
  .values-grid {
    grid-template-columns: 1fr;
    gap: 2.5rem;
  }
  
  .value-card {
    padding: 2.5rem 2rem;
  }
}

@media (max-width: 768px) {
  .number {
    font-size: 2.5rem;
  }
  
  h3 {
    font-size: 1.3rem;
  }
}
</style>