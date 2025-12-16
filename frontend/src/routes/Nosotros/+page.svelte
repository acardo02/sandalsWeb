<script>
  import { onMount } from 'svelte';
  import ContactForm from '$lib/components/nosotros/ContactForm.svelte';
  import NosotrosHero from '$lib/components/nosotros/NosotrosHero.svelte';
  import NosotrosStory from '$lib/components/nosotros/NosotrosStory.svelte';
  import NosotrosValues from '$lib/components/nosotros/NosotrosValues.svelte';
</script>

<NosotrosHero />
<NosotrosStory />
<NosotrosValues />
<ContactForm />

<style>
  :global(body) {
    overflow-x: hidden;
  }
</style>