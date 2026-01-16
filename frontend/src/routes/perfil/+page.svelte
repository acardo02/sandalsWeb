<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth } from '$lib/api';

  let user = null;
  let loading = true;
  let saving = false;
  let error = '';
  let success = '';

  // Formulario
  let formData = {
    first_name: '',
    last_name: '',
    phone_number: '',
    document_id: '',
    address: {
      street: '',
      city: '',
      state: '',
      zip_code: '',
      country: 'El Salvador'
    }
  };

  const loadUser = async () => {
    try {
      user = await auth.getMe();
      // Llenar formulario con datos actuales
      formData = {
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        phone_number: user.phone_number || '',
        document_id: user.document_id || '',
        address: user.address || {
          street: '',
          city: '',
          state: '',
          zip_code: '',
          country: 'El Salvador'
        }
      };
    } catch (err) {
      goto('/login?redirect=/perfil');
    } finally {
      loading = false;
    }
  };

  const handleSubmit = async () => {
    saving = true;
    error = '';
    success = '';

    try {
      // Preparar datos, solo enviar address si tiene datos
      const updateData = { ...formData };
      if (!updateData.address.street) {
        delete updateData.address;
      }

      user = await auth.updateProfile(updateData);
      success = 'Perfil actualizado correctamente';
      setTimeout(() => success = '', 3000);
    } catch (err) {
      error = err.message || 'Error al actualizar perfil';
    } finally {
      saving = false;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    goto('/');
  };

  onMount(loadUser);
</script>

<svelte:head>
  <title>Mi Perfil | CALERO</title>
</svelte:head>

<section class="profile-page">
  {#if loading}
    <div class="loading">
      <div class="spinner"></div>
      <p>Cargando...</p>
    </div>
  {:else}
    <div class="profile-container">
      <div class="sidebar">
        <div class="user-info">
          <div class="avatar">
            {user.first_name?.charAt(0) || 'U'}{user.last_name?.charAt(0) || ''}
          </div>
          <h2>{user.first_name} {user.last_name}</h2>
          <p>{user.email}</p>
        </div>

        <nav class="profile-nav">
          <a href="/perfil" class="active">Mi Perfil</a>
          <a href="/mis-ordenes">Mis Órdenes</a>
          <a href="/favoritos">Mis Favoritos</a>
          <button class="logout-btn" on:click={logout}>Cerrar Sesión</button>
        </nav>
      </div>

      <div class="profile-content">
        <h1>Mi Perfil</h1>

        {#if error}
          <div class="alert error">{error}</div>
        {/if}

        {#if success}
          <div class="alert success">{success}</div>
        {/if}

        <form on:submit|preventDefault={handleSubmit}>
          <div class="form-section">
            <h3>Información Personal</h3>

            <div class="form-row">
              <div class="form-group">
                <label for="first_name">Nombre</label>
                <input
                  type="text"
                  id="first_name"
                  bind:value={formData.first_name}
                  required
                />
              </div>
              <div class="form-group">
                <label for="last_name">Apellido</label>
                <input
                  type="text"
                  id="last_name"
                  bind:value={formData.last_name}
                  required
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="phone_number">Teléfono</label>
                <input
                  type="tel"
                  id="phone_number"
                  bind:value={formData.phone_number}
                  placeholder="+503 7000-0000"
                />
              </div>
              <div class="form-group">
                <label for="document_id">DUI / NIT</label>
                <input
                  type="text"
                  id="document_id"
                  bind:value={formData.document_id}
                  placeholder="00000000-0"
                />
              </div>
            </div>

            <div class="form-group">
              <label for="email">Email</label>
              <input
                type="email"
                id="email"
                value={user.email}
                disabled
              />
              <span class="help-text">El email no se puede cambiar</span>
            </div>
          </div>

          <div class="form-section">
            <h3>Dirección de Envío</h3>

            <div class="form-group">
              <label for="street">Dirección</label>
              <input
                type="text"
                id="street"
                bind:value={formData.address.street}
                placeholder="Calle, número, colonia"
              />
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="city">Ciudad</label>
                <input
                  type="text"
                  id="city"
                  bind:value={formData.address.city}
                  placeholder="San Salvador"
                />
              </div>
              <div class="form-group">
                <label for="state">Departamento</label>
                <input
                  type="text"
                  id="state"
                  bind:value={formData.address.state}
                  placeholder="San Salvador"
                />
              </div>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label for="zip_code">Código Postal</label>
                <input
                  type="text"
                  id="zip_code"
                  bind:value={formData.address.zip_code}
                  placeholder="Opcional"
                />
              </div>
              <div class="form-group">
                <label for="country">País</label>
                <input
                  type="text"
                  id="country"
                  bind:value={formData.address.country}
                  disabled
                />
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-primary" disabled={saving}>
              {saving ? 'Guardando...' : 'Guardar Cambios'}
            </button>
          </div>
        </form>
      </div>
    </div>
  {/if}
</section>

<style>
.profile-page {
  padding: 8rem 5vw 4rem;
  min-height: 100vh;
  background: #fafafa;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
  gap: 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #000;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.profile-container {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 3rem;
  max-width: 1100px;
  margin: 0 auto;
}

/* Sidebar */
.sidebar {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  height: fit-content;
  position: sticky;
  top: 6rem;
}

.user-info {
  text-align: center;
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #eee;
}

.avatar {
  width: 80px;
  height: 80px;
  background: #000;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 auto 1rem;
}

.user-info h2 {
  font-family: 'Playfair Display', serif;
  font-size: 1.3rem;
  margin-bottom: 0.3rem;
}

.user-info p {
  color: #666;
  font-size: 0.9rem;
}

.profile-nav {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.profile-nav a {
  display: block;
  padding: 0.8rem 1rem;
  color: #333;
  text-decoration: none;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.profile-nav a:hover {
  background: #f5f5f5;
}

.profile-nav a.active {
  background: #000;
  color: white;
}

.logout-btn {
  width: 100%;
  padding: 0.8rem 1rem;
  background: none;
  border: 1px solid #c62828;
  color: #c62828;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
  transition: all 0.2s ease;
}

.logout-btn:hover {
  background: #ffebee;
}

/* Content */
.profile-content {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.profile-content h1 {
  font-family: 'Playfair Display', serif;
  font-size: 2rem;
  margin-bottom: 2rem;
}

.alert {
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1.5rem;
}

.alert.error {
  background: #ffebee;
  color: #c62828;
  border-left: 3px solid #c62828;
}

.alert.success {
  background: #e8f5e9;
  color: #2e7d32;
  border-left: 3px solid #2e7d32;
}

.form-section {
  margin-bottom: 2.5rem;
}

.form-section h3 {
  font-size: 1.1rem;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
  color: #333;
}

.form-group input {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 1px solid #ddd;
  font-size: 1rem;
  transition: border-color 0.3s ease;
}

.form-group input:focus {
  outline: none;
  border-color: #000;
}

.form-group input:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
}

.help-text {
  display: block;
  font-size: 0.8rem;
  color: #999;
  margin-top: 0.3rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.btn-primary {
  padding: 1rem 2rem;
  background: #000;
  color: white;
  border: none;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover:not(:disabled) {
  background: #333;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 968px) {
  .profile-container {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: static;
  }
}

@media (max-width: 600px) {
  .profile-page {
    padding: 6rem 1rem 2rem;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .profile-content h1 {
    font-size: 1.5rem;
  }
}
</style>
