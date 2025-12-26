<script>
  import { onMount } from 'svelte';
  import { authStore } from '$lib/stores/authStore';
  import Navbar from '$lib/components/Navbar.svelte';
  import Footer from '$lib/components/Footer.svelte';

  let ready = false;

  onMount(async () => {
    await authStore.init();
    ready = true;
  });
</script>

{#if ready}
  <Navbar />

  <main class="container">
    <slot />
  </main>

  <Footer />
{:else}
  <div class="loading-screen">
    <div class="spinner"></div>
  </div>
{/if}

<style>
.container {
  max-width: 1200px;
  margin: auto;
  padding: 1rem;
}

.loading-screen {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fafafa;
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
</style>