<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/authStore';

  let email = '';
  let password = '';
  let confirmPassword = '';
  let first_name = '';
  let last_name = '';
  let phone_number = '';
  let error = '';
  let loading = false;
  let visible = false;
  let success = false;
  let passwordErrors = [];

  // Validaciones de contraseña como variables
  $: hasMinLength = password.length >= 8;
  $: hasUpperCase = /[A-Z]/.test(password);
  $: hasLowerCase = /[a-z]/.test(password);
  $: hasNumber = /[0-9]/.test(password);
  $: hasSpecialChar = /[!@#$%^&*()_\-+=[\]{};:'",.<>?/\\|`~]/.test(password);

  // Validar contraseña en tiempo real
  $: {
    passwordErrors = [];
    if (password.length > 0) {
      if (!hasMinLength) passwordErrors.push('Mínimo 8 caracteres');
      if (!hasUpperCase) passwordErrors.push('Una letra mayúscula');
      if (!hasLowerCase) passwordErrors.push('Una letra minúscula');
      if (!hasNumber) passwordErrors.push('Un número');
      if (!hasSpecialChar) passwordErrors.push('Un carácter especial');
    }
  }

  onMount(() => {
    setTimeout(() => visible = true, 100);
  });

  async function handleSubmit(e) {
    e.preventDefault();
    error = '';

    // Validar formato de contraseña (incluye _ - y otros caracteres especiales)
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_\-+=\[\]{};:'",.<>?/\\|`~])[A-Za-z\d!@#$%^&*()_\-+=\[\]{};:'",.<>?/\\|`~]{8,}$/;
    
    if (!passwordRegex.test(password)) {
      error = 'La contraseña no cumple con los requisitos de seguridad';
      return;
    }

    if (password !== confirmPassword) {
      error = 'Las contraseñas no coinciden';
      return;
    }

    loading = true;

    const result = await authStore.register({
      email,
      password,
      first_name,
      last_name,
      phone_number,
    });

    if (result.success) {
      success = true;
      setTimeout(() => {
        goto('/login');
      }, 2000);
    } else {
      error = result.error;
      loading = false;
    }
  }
</script>

<section class="register-page {visible ? 'show' : ''}">
  <div class="register-container">
    <div class="header">
      <h1>Crear Cuenta</h1>
      <p class="subtitle">Únete a la familia CALERO</p>
    </div>

    {#if success}
      <div class="success-message">
        ¡Cuenta creada exitosamente! Redirigiendo al login...
      </div>
    {:else}
      <form on:submit={handleSubmit}>
        {#if error}
          <div class="error-message">
            {error}
          </div>
        {/if}

        <div class="form-row">
          <div class="form-group">
            <label for="first_name">Nombre</label>
            <input
              id="first_name"
              type="text"
              bind:value={first_name}
              required
              disabled={loading}
            />
          </div>

          <div class="form-group">
            <label for="last_name">Apellido</label>
            <input
              id="last_name"
              type="text"
              bind:value={last_name}
              required
              disabled={loading}
            />
          </div>
        </div>

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
          <label for="phone">Teléfono</label>
          <input
            id="phone"
            type="tel"
            bind:value={phone_number}
            required
            placeholder="+503 1234-5678"
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
            placeholder="Mínimo 8 caracteres"
            disabled={loading}
          />
          {#if password.length > 0 && passwordErrors.length > 0}
            <div class="password-requirements">
              <p class="requirements-title">La contraseña debe tener:</p>
              <ul>
                <li class:valid={hasMinLength}>
                  {hasMinLength ? '✓' : '○'} Mínimo 8 caracteres
                </li>
                <li class:valid={hasUpperCase}>
                  {hasUpperCase ? '✓' : '○'} Una letra mayúscula
                </li>
                <li class:valid={hasLowerCase}>
                  {hasLowerCase ? '✓' : '○'} Una letra minúscula
                </li>
                <li class:valid={hasNumber}>
                  {hasNumber ? '✓' : '○'} Un número
                </li>
                <li class:valid={hasSpecialChar}>
                  {hasSpecialChar ? '✓' : '○'} Un carácter especial
                </li>
              </ul>
            </div>
          {/if}
        </div>

        <div class="form-group">
          <label for="confirmPassword">Confirmar contraseña</label>
          <input
            id="confirmPassword"
            type="password"
            bind:value={confirmPassword}
            required
            placeholder="Repite tu contraseña"
            disabled={loading}
          />
        </div>

        <button type="submit" class="submit-btn" disabled={loading}>
          {loading ? 'Creando cuenta...' : 'Crear cuenta'}
        </button>
      </form>
    {/if}

    <div class="footer">
      <p>¿Ya tienes cuenta? <a href="/login">Inicia sesión aquí</a></p>
    </div>
  </div>
</section>

<style>
.register-page {
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

.register-page.show {
  opacity: 1;
  transform: translateY(0);
}

.register-container {
  background: white;
  padding: 3rem 2.5rem;
  max-width: 550px;
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

.success-message {
  background: #e8f5e9;
  color: #2e7d32;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border-left: 3px solid #2e7d32;
  text-align: center;
}

.error-message {
  background: #fee;
  color: #c33;
  padding: 1rem;
  margin-bottom: 1.5rem;
  border-left: 3px solid #c33;
  font-size: 0.9rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
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
  box-sizing: border-box;
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
  box-sizing: border-box;
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

.password-requirements {
  margin-top: 0.8rem;
  padding: 1rem;
  background: #f9f9f9;
  border-left: 3px solid #ddd;
  font-size: 0.85rem;
}

.requirements-title {
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #666;
}

.password-requirements ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.password-requirements li {
  padding: 0.3rem 0;
  color: #999;
  transition: color 0.3s ease;
}

.password-requirements li.valid {
  color: #2e7d32;
  font-weight: 500;
}

@media (max-width: 768px) {
  .register-container {
    padding: 2rem 1.5rem;
  }

  h1 {
    font-size: 2rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>