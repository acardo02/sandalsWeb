<script>
  import { onMount } from 'svelte';
  import { cart } from '$lib/stores/cartStore';
  import { authStore } from '$lib/stores/authStore';

  let showUserMenu = false;

  onMount(() => {
    authStore.init();
    
    // Cerrar menú al hacer click fuera
    const handleClickOutside = (e) => {
      if (showUserMenu && !e.target.closest('.user-menu')) {
        showUserMenu = false;
      }
    };
    
    document.addEventListener('click', handleClickOutside);
    
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  });

  function toggleUserMenu(e) {
    e.stopPropagation();
    showUserMenu = !showUserMenu;
  }

  function handleLogout() {
    showUserMenu = false;
    authStore.logout();
  }
</script>

<nav>
  <a href="/" class="logo">CALERO</a>

  <div class="links">
    {#if !$authStore.isAdmin}
      <a href="/Nosotros">Nosotros</a>
      <a href="/productos">Productos</a>
    {/if}
    
    {#if $authStore.isAuthenticated}
      {#if $authStore.isAdmin}
        <a href="/admin" class="admin-link">Dashboard Admin</a>
      {:else}
        <a href="/carrito">Carrito ({$cart.length})</a>
      {/if}
      
      <div class="user-menu">
        <button class="user-btn" on:click={toggleUserMenu}>
          {$authStore.user?.first_name || 'Usuario'}
        </button>
        
        {#if showUserMenu}
          <div class="dropdown">
            <div class="user-info">
              <strong>{$authStore.user?.first_name} {$authStore.user?.last_name}</strong>
              <span>{$authStore.user?.email}</span>
              <span class="role">{$authStore.user?.role === 'admin' ? 'Administrador' : 'Cliente'}</span>
            </div>
            <button class="logout-btn" on:click={handleLogout}>Cerrar sesión</button>
          </div>
        {/if}
      </div>
    {:else}
      <a href="/carrito">Carrito ({$cart.length})</a>
      <a href="/login" class="login-link">Iniciar sesión</a>
    {/if}
  </div>
</nav>

<style>
nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  border-bottom: 1px solid #eee;
  background: white;
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo {
  font-weight: bold;
  font-size: 1.3rem;
  letter-spacing: 2px;
  text-decoration: none;
  color: black;
  transition: opacity 0.3s ease;
}

.logo:hover {
  opacity: 0.6;
}

.links {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.links a {
  text-decoration: none;
  color: black;
  font-size: 0.9rem;
  letter-spacing: 0.5px;
  transition: opacity 0.3s ease;
}

.links a:hover {
  opacity: 0.6;
}

.admin-link {
  background: #000;
  color: white !important;
  padding: 0.5rem 1rem;
  border-radius: 2px;
  font-size: 0.8rem;
  letter-spacing: 1px;
}

.admin-link:hover {
  opacity: 1;
  background: #333;
}

.login-link {
  border: 1px solid #000;
  padding: 0.5rem 1.2rem;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.login-link:hover {
  background: #000;
  color: white !important;
  opacity: 1;
}

.user-menu {
  position: relative;
}

.user-btn {
  background: none;
  border: 1px solid #000;
  padding: 0.5rem 1.2rem;
  border-radius: 2px;
  cursor: pointer;
  font-size: 0.9rem;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
}

.user-btn:hover {
  background: #000;
  color: white;
}

.dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  background: white;
  border: 1px solid #ddd;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  min-width: 220px;
  z-index: 1000;
}

.user-info {
  padding: 1rem;
  border-bottom: 1px solid #eee;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.user-info strong {
  font-size: 0.95rem;
}

.user-info span {
  font-size: 0.8rem;
  color: #666;
}

.user-info .role {
  display: inline-block;
  margin-top: 0.3rem;
  padding: 0.2rem 0.5rem;
  background: #f0f0f0;
  font-size: 0.7rem;
  letter-spacing: 1px;
  text-transform: uppercase;
  width: fit-content;
}

.logout-btn {
  width: 100%;
  background: none;
  border: none;
  padding: 0.8rem 1rem;
  text-align: left;
  cursor: pointer;
  font-size: 0.85rem;
  transition: background 0.2s ease;
}

.logout-btn:hover {
  background: #f5f5f5;
}

@media (max-width: 768px) {
  nav {
    padding: 1rem;
  }

  .links {
    gap: 1rem;
    font-size: 0.85rem;
  }

  .logo {
    font-size: 1.1rem;
  }
}
</style>