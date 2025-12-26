<script>
  import { onMount } from 'svelte';
  import { authStore } from '$lib/stores/authStore';

  let email = '';
  let password = '';
  let error = '';
  let loading = false;
  let visible = false;

  onMount(() => {
    setTimeout(() => visible = true, 100);
  });

  async function handleSubmit(e) {
    e.preventDefault();
    error = '';
    loading = true;

    const result = await authStore.login(email, password);

    if (!result.success) {
      error = result.error;
      loading = false;
    }
    // Si es exitoso, el authStore maneja la redirección automáticamente
  }
</script>

<section class="login-page {visible ? 'show' : ''}">
  <div class="login-container">
    <div class="header">
      <h1>Iniciar Sesión</h1>
      <p class="subtitle">Accede a tu cuenta de CALERO</p>
    </div>

    <form on:submit={handleSubmit}>
      {#if error}
        <div class="error-message">
          {error}
        </div>
      {/if}

      <div class="form-group">
        <label for="email">Correo electrónico</label>
        <input
          id="email"
          type="email"
          bind:value={email}
          required
          placeholder="tu@email.com"
          disabled={loading}
        />
      </div>

      <div class="form-group">
        <label for="password">Contraseña</label>
        <input
          id="password"
          type="password"
          bind:value={password}
          required
          placeholder="••••••••"
          disabled={loading}
        />
      </div>

      <button type="submit" class="submit-btn" disabled={loading}>
        {loading ? 'Iniciando sesión...' : 'Iniciar sesión'}
      </button>
    </form>

    <div class="footer">
      <p>¿No tienes cuenta? <a href="/register">Regístrate aquí</a></p>
    </div>
  </div>
</section>

<style>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  background: linear-gradient(135deg, #fafafa 0%, #f0f0f0 100%);
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}

.login-page.show {
  opacity: 1;
  transform: translateY(0);
}

.login-container {
  background: white;
  padding: 3rem 2.5rem;
  max-width: 450px;
  width: 100%;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
}

.header {
  text-align: center;
  margin-bottom: 2.5rem;
}

h1 {
  font-family: 'Playfair Display', serif;
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.subtitle {
  color: #666;
  font-size: 0.9rem;
  letter-spacing: 0.5px;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 1rem;
  margin-bottom: 1.5rem;
  border-left: 3px solid #c33;
  font-size: 0.9rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: #333;
}

input {
  width: 100%;
  padding: 0.9rem;
  border: 1px solid #ddd;
  font-size: 1rem;
  transition: all 0.3s ease;
  font-family: inherit;
}

input:focus {
  outline: none;
  border-color: #000;
}

input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.submit-btn {
  width: 100%;
  background: #000;
  color: white;
  border: 1px solid #000;
  padding: 1.1rem;
  font-size: 0.8rem;
  letter-spacing: 2px;
  text-transform: uppercase;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1rem;
}

.submit-btn:hover:not(:disabled) {
  background: white;
  color: #000;
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.footer {
  margin-top: 2rem;
  text-align: center;
  font-size: 0.9rem;
  color: #666;
}

.footer a {
  color: #000;
  text-decoration: none;
  border-bottom: 1px solid #000;
  transition: opacity 0.3s ease;
}

.footer a:hover {
  opacity: 0.6;
}

@media (max-width: 768px) {
  .login-container {
    padding: 2rem 1.5rem;
  }

  h1 {
    font-size: 2rem;
  }
}
</style>