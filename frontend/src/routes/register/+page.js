// frontend/src/routes/register/+page.js
import { authStore } from '$lib/stores/authStore';
import { goto } from '$app/navigation';
import { get } from 'svelte/store';

export async function load() {
  const auth = get(authStore);
  
  if (auth.isAuthenticated) {
    goto('/');
    return;
  }
}