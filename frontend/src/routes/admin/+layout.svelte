<script>
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { authStore } from '$lib/stores/authStore';

  let checking = true;

  onMount(async () => {
    await authStore.init();

    const unsubscribe = authStore.subscribe((state) => {
      if (!state.loading) {
        if (!state.isAuthenticated) {
          goto('/login');
        } else if (!state.isAdmin) {
          goto('/productos');
        } else {
          checking = false;
        }
      }
    });

    return unsubscribe;
  });
</script>

{#if checking}
  <div class="checking">
    <div class="spinner"></div>
    <p>Verificando acceso...</p>
  </div>
{:else}
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>Panel de Admin</h2>
        <a href="/" class="back-link">← Volver al sitio</a>
      </div>

      <nav class="sidebar-nav">
        <a href="/admin" class="nav-item">
          📦 Productos
        </a>
        <a href="/admin/orders" class="nav-item">
          📋 Órdenes
        </a>
      </nav>

      <div class="sidebar-footer">
        <div class="user-badge">
          <strong>{$authStore.user?.first_name}</strong>
          <span>Administrador</span>
        </div>
      </div>
    </aside>

    <main class="admin-content">
      <slot />
    </main>
  </div>
{/if}

<style>
.checking {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
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

.admin-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  min-height: 100vh;
}

.sidebar {
  background: #1a1a1a;
  color: white;
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 0;
  height: 100vh;
}

.sidebar-header {
  padding: 2rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.sidebar-header h2 {
  font-family: 'Playfair Display', serif;
  font-size: 1.5rem;
  margin-bottom: 0.8rem;
}

.back-link {
  color: rgba(255, 255, 255, 0.6);
  text-decoration: none;
  font-size: 0.85rem;
  transition: color 0.3s ease;
}

.back-link:hover {
  color: white;
}

.sidebar-nav {
  flex: 1;
  padding: 1.5rem 0;
}

.nav-item {
  display: block;
  padding: 1rem 1.5rem;
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.05);
  color: white;
  border-left-color: white;
}

.sidebar-footer {
  padding: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.user-badge {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.user-badge strong {
  font-size: 0.95rem;
}

.user-badge span {
  font-size: 0.75rem;
  opacity: 0.6;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.admin-content {
  background: #f5f5f5;
  padding: 2rem;
  overflow-y: auto;
}

@media (max-width: 968px) {
  .admin-layout {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: relative;
    height: auto;
  }
}
</style>