<script>
  import { goto } from '$app/navigation';

  function goToProducts() {
    goto('/productos');
  }
    
  import { onMount } from 'svelte';

  let visible = false;
  let scrollY = 0;

  onMount(() => {
    setTimeout(() => (visible = true), 200);
    
    const handleScroll = () => {
      scrollY = window.scrollY;
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  });
</script>

<section class="hero">
  <div class="background" style="transform: translateY({scrollY * 0.5}px)">
    <div class="overlay"></div>
  </div>
  
  <div class="text {visible ? 'show' : ''}">
    <div class="label">Colección 2025</div>
    <h1>
      Menos ruido.<br />
      Más diseño.
    </h1>

    <p>
      Sandalias y tenis creados con intención.<br />
      Diseño que se siente, no que grita.
    </p>
    
    <button class="cta" on:click={goToProducts}>
      Explorar colección
      <span class="arrow">→</span>
    </button>
  </div>
  
  <div class="scroll-indicator {visible ? 'show' : ''}">
    <span>Scroll</span>
    <div class="line"></div>
  </div>
</section>

<style>
.hero {
  height: 100vh;
  display: flex;
  align-items: center;
  padding-left: 10vw;
  position: relative;
  overflow: hidden;
}

.background {
  position: absolute;
  top: -10%;
  left: 0;
  width: 100%;
  height: 120%;
  background: linear-gradient(135deg, #f8f8f8 0%, #e8e8e8 100%);
  z-index: 0;
}

.background::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 60%;
  height: 100%;
  background: radial-gradient(circle at 80% 50%, rgba(0,0,0,0.03) 0%, transparent 70%);
  animation: pulse 8s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: repeating-linear-gradient(
    90deg,
    transparent,
    transparent 100px,
    rgba(0,0,0,0.01) 100px,
    rgba(0,0,0,0.01) 101px
  );
}

.text {
  opacity: 0;
  transform: translateY(50px);
  transition: all 1.4s cubic-bezier(0.16, 1, 0.3, 1);
  max-width: 800px;
  position: relative;
  z-index: 1;
}

.text.show {
  opacity: 1;
  transform: translateY(0);
}

.label {
  font-size: 0.75rem;
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-bottom: 2rem;
  opacity: 0.7;
  animation: fadeIn 1s ease 0.5s forwards;
  opacity: 0;
}

@keyframes fadeIn {
  to { opacity: 0.7; }
}

h1 {
  font-family: 'Playfair Display', serif;
  font-size: clamp(4rem, 9vw, 7rem);
  line-height: 1;
  margin-bottom: 2rem;
  position: relative;
}

h1::after {
  content: '';
  position: absolute;
  bottom: -1rem;
  left: 0;
  width: 0;
  height: 2px;
  background: #000;
  animation: lineGrow 1.2s ease 1s forwards;
}

@keyframes lineGrow {
  to { width: 120px; }
}

p {
  font-size: 1rem;
  letter-spacing: 1px;
  max-width: 420px;
  line-height: 1.8;
  margin-bottom: 3rem;
}

.cta {
  background: transparent;
  border: 1px solid #000;
  padding: 1.2rem 3rem;
  font-size: 0.85rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.4s ease;
}

.cta::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: #000;
  transition: left 0.5s ease;
  z-index: -1;
}

.cta:hover {
  color: #fff;
}

.cta:hover::before {
  left: 0;
}

.arrow {
  display: inline-block;
  margin-left: 1rem;
  transition: transform 0.3s ease;
}

.cta:hover .arrow {
  transform: translateX(5px);
}

.scroll-indicator {
  position: absolute;
  bottom: 3rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  opacity: 0;
  transition: opacity 1s ease 1.5s;
}

.scroll-indicator.show {
  opacity: 0.6;
}

.scroll-indicator span {
  font-size: 0.7rem;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.line {
  width: 1px;
  height: 40px;
  background: #000;
  animation: scrollAnim 2s ease-in-out infinite;
}

@keyframes scrollAnim {
  0%, 100% { 
    transform: translateY(0);
    opacity: 0;
  }
  50% { 
    opacity: 1;
  }
  100% { 
    transform: translateY(20px);
  }
}

@media (max-width: 768px) {
  .hero {
    padding-left: 5vw;
    padding-right: 5vw;
  }
  
  .cta {
    padding: 1rem 2rem;
    font-size: 0.75rem;
  }
}
</style>