import { authStore } from '$lib/stores/authStore';
import { get } from 'svelte/store';

export async function load() {
  const auth = get(authStore);

  // Solo bloquea si YA está logueado
  // NO redirigir aquí
  if (auth.isAuthenticated) {
    return;
  }
}
