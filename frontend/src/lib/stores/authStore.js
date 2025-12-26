// frontend/src/lib/stores/authStore.js

import { writable, get } from 'svelte/store';
import { auth as authApi } from '$lib/api';
import { goto } from '$app/navigation';

/**
 * @typedef {{
 *  id: string,
 *  first_name: string,
 *  last_name: string,
 *  role: string,
 *  phone_number?: string,
 *  email?: string,
 *  is_active?: boolean
 * }} User
 */

/**
 * @typedef {{
 *  user: User | null,
 *  token: string | null,
 *  loading: boolean,
 *  isAuthenticated: boolean,
 *  isAdmin: boolean
 * }} AuthState
 */

function createAuthStore() {
  const { subscribe, set, update } = writable({
    user: null,
    token: null,
    loading: true,
    isAuthenticated: false,
    isAdmin: false,
  });

  return {
    subscribe,

    /**
     * Inicializa el store desde localStorage
     */
    async init() {
      if (typeof window === 'undefined') {
        set({
          user: null,
          token: null,
          loading: false,
          isAuthenticated: false,
          isAdmin: false,
        });
        return;
      }

      const token = localStorage.getItem('token');
      
      if (!token) {
        set({
          user: null,
          token: null,
          loading: false,
          isAuthenticated: false,
          isAdmin: false,
        });
        return;
      }

      try {
        const user = await authApi.getMe();
        set({
          user,
          token,
          loading: false,
          isAuthenticated: true,
          isAdmin: user.role === 'admin',
        });
      } catch (error) {
        console.error('Error al cargar usuario:', error);
        localStorage.removeItem('token');
        set({
          user: null,
          token: null,
          loading: false,
          isAuthenticated: false,
          isAdmin: false,
        });
      }
    },

    /**
     * Login de usuario
     */
    async login(email, password) {
      try {
        const response = await authApi.login(email, password);
        const { access_token } = response;

        localStorage.setItem('token', access_token);

        const user = await authApi.getMe();

        set({
          user,
          token: access_token,
          loading: false,
          isAuthenticated: true,
          isAdmin: user.role === 'admin',
        });

        // Redirigir según el rol
        if (user.role === 'admin') {
          goto('/admin');
        } else {
          goto('/');
        }

        return { success: true };
      } catch (error) {
        return { 
          success: false, 
          error: error.message || 'Error al iniciar sesión' 
        };
      }
    },

    /**
     * Registro de usuario
     */
    async register(userData) {
      try {
        await authApi.register(userData);
        return { success: true };
      } catch (error) {
        return { 
          success: false, 
          error: error.message || 'Error al registrar usuario' 
        };
      }
    },

    /**
     * Logout
     */
    logout() {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
      }
      
      set({
        user: null,
        token: null,
        loading: false,
        isAuthenticated: false,
        isAdmin: false,
      });

      // Redirigir al login
      goto('/login');
    },

    /**
     * Obtener el estado actual
     */
    getState() {
      return get(this);
    }
  };
}

export const authStore = createAuthStore();