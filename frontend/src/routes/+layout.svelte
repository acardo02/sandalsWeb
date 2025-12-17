<script>
  import Navbar from '$lib/components/Navbar.svelte';
  import Footer from '$lib/components/Footer.svelte';
</script>

<Navbar />

<main class="container">
  <slot />
</main>

<Footer />

<style>
.container {
  max-width: 1200px;
  margin: auto;
  padding: 1rem;
}
</style>
