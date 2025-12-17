<script>
  // @ts-nocheck
  import { onMount } from 'svelte';
  
  let visible = false;
  let formData = {
    name: '',
    email: '',
    subject: '',
    message: ''
  };
  let isSubmitting = false;
  let submitted = false;
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    isSubmitting = true;
    
    // Simular envío (aquí conectarías con tu backend)
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    submitted = true;
    isSubmitting = false;
    
    // Reset después de 3 segundos
    setTimeout(() => {
      submitted = false;
      formData = { name: '', email: '', subject: '', message: '' };
    }, 3000);
  };
  
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
    
    const section = document.querySelector('.contact');
    if (section) {
      observer.observe(section);
    }
    
    return () => {
      if (section) {
        observer.unobserve(section);
      }
      observer.disconnect();
    };
  });
</script>

<section class="contact">
  <div class="container">
    <div class="contact-info {visible ? 'show' : ''}">
      <span class="label">Conversemos</span>
      <h2>Nos encantaría<br />escucharte.</h2>
      
      <div class="info-blocks">
        <div class="info-block">
          <h4>Email</h4>
          <a href="mailto:hola@tutienda.com">hola@tutienda.com</a>
        </div>
        
        <div class="info-block">
          <h4>Teléfono</h4>
          <a href="tel:+50312345678">+503 1234 5678</a>
        </div>
        
        <div class="info-block">
          <h4>Redes</h4>
          <div class="social">
            <a href="https://www.instagram.com/calerosv?utm_source=ig_web_button_share_sheet&igsh=ZDNlZDc0MzIxNw==" target="_blank">Instagram</a>
            <a href="#" target="_blank">Facebook</a>
          </div>
        </div>
      </div>
    </div>
    
    <div class="form-wrapper {visible ? 'show' : ''}">
      {#if submitted}
        <div class="success-message">
          <div class="check">✓</div>
          <h3>¡Mensaje enviado!</h3>
          <p>Te responderemos pronto.</p>
        </div>
      {:else}
        <form on:submit={handleSubmit}>
          <div class="form-group">
            <label for="name">Nombre</label>
            <input 
              type="text" 
              id="name" 
              bind:value={formData.name}
              required
              placeholder="Tu nombre"
            />
          </div>
          
          <div class="form-group">
            <label for="email">Email</label>
            <input 
              type="email" 
              id="email" 
              bind:value={formData.email}
              required
              placeholder="tu@email.com"
            />
          </div>
          
          <div class="form-group">
            <label for="subject">Asunto</label>
            <input 
              type="text" 
              id="subject" 
              bind:value={formData.subject}
              required
              placeholder="¿En qué podemos ayudarte?"
            />
          </div>
          
          <div class="form-group">
            <label for="message">Mensaje</label>
            <textarea 
              id="message" 
              bind:value={formData.message}
              required
              rows="5"
              placeholder="Cuéntanos más..."
            ></textarea>
          </div>
          
          <button type="submit" class="submit-btn" disabled={isSubmitting}>
            {isSubmitting ? 'Enviando...' : 'Enviar mensaje'}
          </button>
        </form>
      {/if}
    </div>
  </div>
</section>

<style>
.contact {
  padding: 10rem 10vw;
  background: white;
}

.container {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 8rem;
  max-width: 1400px;
  margin: 0 auto;
}

.contact-info {
  opacity: 0;
  transform: translateX(-40px);
  transition: all 1s cubic-bezier(0.16, 1, 0.3, 1);
}

.contact-info.show {
  opacity: 1;
  transform: translateX(0);
}

.label {
  display: block;
  font-size: 0.75rem;
  letter-spacing: 3px;
  text-transform: uppercase;
  margin-bottom: 2rem;
  opacity: 0.6;
}

h2 {
  font-family: 'Playfair Display', serif;
  font-size: 3.5rem;
  line-height: 1.1;
  margin-bottom: 4rem;
}

.info-blocks {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

.info-block h4 {
  font-size: 0.75rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  margin-bottom: 0.8rem;
  opacity: 0.5;
}

.info-block a {
  color: #000;
  text-decoration: none;
  font-size: 1.1rem;
  transition: opacity 0.3s ease;
  display: block;
  margin-bottom: 0.5rem;
}

.info-block a:hover {
  opacity: 0.6;
}

.social {
  display: flex;
  gap: 2rem;
}

.form-wrapper {
  opacity: 0;
  transform: translateX(40px);
  transition: all 1s cubic-bezier(0.16, 1, 0.3, 1) 0.2s;
}

.form-wrapper.show {
  opacity: 1;
  transform: translateX(0);
}

.form-group {
  margin-bottom: 2rem;
}

label {
  display: block;
  font-size: 0.85rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 0.8rem;
  opacity: 0.7;
}

input,
textarea {
  width: 100%;
  padding: 1rem 0;
  border: none;
  border-bottom: 1px solid #ddd;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.3s ease;
  background: transparent;
}

input:focus,
textarea:focus {
  outline: none;
  border-bottom-color: #000;
}

textarea {
  resize: vertical;
  min-height: 120px;
}

.submit-btn {
  background: #000;
  color: white;
  border: 1px solid #000;
  padding: 1.2rem 3rem;
  font-size: 0.8rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  cursor: pointer;
  width: 100%;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.submit-btn:hover:not(:disabled) {
  background: white;
  color: #000;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.success-message {
  text-align: center;
  padding: 4rem 2rem;
}

.check {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: #000;
  color: white;
  font-size: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 2rem;
  animation: scaleIn 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes scaleIn {
  from {
    transform: scale(0);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.success-message h3 {
  font-family: 'Playfair Display', serif;
  font-size: 2rem;
  margin-bottom: 1rem;
}

.success-message p {
  font-size: 1rem;
  opacity: 0.7;
}

@media (max-width: 968px) {
  .contact {
    padding: 6rem 5vw;
  }
  
  .container {
    grid-template-columns: 1fr;
    gap: 4rem;
  }
  
  h2 {
    font-size: 2.8rem;
  }
}

@media (max-width: 768px) {
  h2 {
    font-size: 2.2rem;
  }
  
  .social {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>