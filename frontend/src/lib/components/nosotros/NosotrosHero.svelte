<script>
  import { onMount } from 'svelte';

  let visible = false;

  onMount(() => {
    setTimeout(() => (visible = true), 200);
  });
</script>

<section class="hero">
  <div class="content {visible ? 'show' : ''}">
    <span class="label">Quiénes somos</span>
    <h1>
      Creamos calzado<br />
      con propósito.
    </h1>
    <p class="intro">
      Cada pieza nace de la convicción de que el diseño auténtico<br />
      no necesita gritar para ser recordado.
    </p>
  </div>
</section>

<style>
.hero {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8rem 10vw;
  background: linear-gradient(135deg, #fafafa 0%, #f5f5f5 100%);
  position: relative;
  overflow: hidden;
}

.hero::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 60%;
  height: 150%;
  background: radial-gradient(circle, rgba(0,0,0,0.02) 0%, transparent 70%);
  animation: float 15s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(-30px, -30px) scale(1.1); }
}

.content {
  text-align: center;
  max-width: 900px;
  opacity: 0;
  transform: translateY(40px);
  transition: all 1.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.content.show {
  opacity: 1;
  transform: translateY(0);
}

.label {
  display: inline-block;
  font-size: 0.75rem;
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-bottom: 2rem;
  opacity: 0.6;
  position: relative;
}

.label::before,
.label::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 40px;
  height: 1px;
  background: #000;
  opacity: 0.3;
}

.label::before {
  right: calc(100% + 1rem);
}

.label::after {
  left: calc(100% + 1rem);
}

h1 {
  font-family: 'Playfair Display', serif;
  font-size: clamp(3rem, 7vw, 5.5rem);
  line-height: 1.1;
  margin-bottom: 2.5rem;
}

.intro {
  font-size: 1.1rem;
  line-height: 1.8;
  letter-spacing: 0.3px;
  color: #333;
}

@media (max-width: 768px) {
  .hero {
    padding: 6rem 5vw;
    min-height: 70vh;
  }
  
  .label::before,
  .label::after {
    display: none;
  }
  
  .intro br {
    display: none;
  }
}
</style>