// frontend/src/lib/api.js

const API_URL = 'http://localhost:8000';

/**
 * Obtiene el token del localStorage
 */
function getToken() {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('token');
  }
  return null;
}

/**
 * Realiza una petición HTTP con manejo de errores
 */
async function request(endpoint, options = {}) {
  const token = getToken();
  
  const config = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  if (token && !options.skipAuth) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_URL}${endpoint}`, config);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
      
      // Mejorar el mensaje de error
      let errorMessage = 'Error desconocido';
      
      if (error.detail) {
        // Si detail es un array (errores de validación de Pydantic)
        if (Array.isArray(error.detail)) {
          errorMessage = error.detail.map(e => `${e.loc.join('.')}: ${e.msg}`).join(', ');
        } else {
          errorMessage = error.detail;
        }
      }
      
      console.error('Error completo del backend:', error);
      console.error('Endpoint:', endpoint);
      console.error('Datos enviados:', options.body);
      
      throw new Error(errorMessage);
    }

    // Si es 204 No Content, no hay body que parsear
    if (response.status === 204) {
      return null;
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }

    return null;
  } catch (error) {
    // Manejar error de red o token expirado
    if (error.message.includes('No se pudieron validar las credenciales') ||
        error.message.includes('401')) {
      // Token expirado, limpiar y redirigir
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        window.location.href = '/login';
      }
    }
    console.error('API Error:', error);
    throw error;
  }
}

// ==================== AUTH ====================

export const auth = {
  async login(email, password) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Error de autenticación' }));
      throw new Error(error.detail);
    }

    return await response.json();
  },

  async register(userData) {
    return request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
      skipAuth: true,
    });
  },

  async getMe() {
    return request('/users/me');
  },

  async updateProfile(profileData) {
    return request('/users/me', {
      method: 'PATCH',
      body: JSON.stringify(profileData),
    });
  },
};

// ==================== PRODUCTS ====================

export const products = {
  async getAll(params = {}) {
    const query = new URLSearchParams(params).toString();
    return request(`/products/?${query}`, { skipAuth: true });
  },

  async getById(id) {
    return request(`/products/${id}`, { skipAuth: true });
  },

  async getVariants(id) {
    return request(`/products/${id}/variants`, { skipAuth: true });
  },

  async getVariantDetails(productId, variantSku) {
    return request(`/products/${productId}/variant/${variantSku}`, { skipAuth: true });
  },

  async getFeatured(limit = 8) {
    return request(`/products/featured?limit=${limit}`, { skipAuth: true });
  },

  async getCategories() {
    return request('/products/categories', { skipAuth: true });
  },

  async create(productData) {
    return request('/products/', {
      method: 'POST',
      body: JSON.stringify(productData),
    });
  },

  async update(id, productData) {
    return request(`/products/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(productData),
    });
  },

  async delete(id) {
    return request(`/products/${id}`, {
      method: 'DELETE',
    });
  },
};

// ==================== ORDERS ====================

export const orders = {
  async create(orderData) {
    return request('/orders/', {
      method: 'POST',
      body: JSON.stringify(orderData),
    });
  },

  async getMyOrders(params = {}) {
    const query = new URLSearchParams(params).toString();
    return request(`/orders/me?${query}`);
  },

  async getById(orderId) {
    return request(`/orders/${orderId}`);
  },

  async getAll(params = {}) {
    const query = new URLSearchParams(params).toString();
    return request(`/orders/?${query}`);
  },

  async createPaymentLink(orderId) {
    return request(`/orders/${orderId}/payment-link`, {
      method: 'POST',
    });
  },

  async cancel(orderId) {
    return request(`/orders/${orderId}/cancel`, {
      method: 'POST',
    });
  },

  async updateStatus(orderId, statusData) {
    return request(`/orders/${orderId}/status`, {
      method: 'PATCH',
      body: JSON.stringify(statusData),
    });
  },

  async updateShipping(orderId, shippingData) {
    return request(`/orders/${orderId}/shipping`, {
      method: 'PATCH',
      body: JSON.stringify(shippingData),
    });
  },

  async getStats() {
    return request('/orders/stats/summary');
  },
};

// ==================== UPLOAD ====================

export const upload = {
  async image(file) {
    const formData = new FormData();
    formData.append('file', file);

    const token = getToken();
    const response = await fetch(`${API_URL}/upload/`, {
      method: 'POST',
      headers: {
        ...(token && { 'Authorization': `Bearer ${token}` }),
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Error al subir imagen' }));
      throw new Error(error.detail);
    }

    return await response.json();
  },
};

// ==================== COUPONS ====================

export const coupons = {
  async validate(code, subtotal) {
    return request('/coupons/validate', {
      method: 'POST',
      body: JSON.stringify({ code, subtotal }),
    });
  },

  // Admin endpoints
  async create(couponData) {
    return request('/coupons/', {
      method: 'POST',
      body: JSON.stringify(couponData),
    });
  },

  async getAll(params = {}) {
    const query = new URLSearchParams(params).toString();
    return request(`/coupons/?${query}`);
  },

  async update(code, couponData) {
    return request(`/coupons/${code}`, {
      method: 'PATCH',
      body: JSON.stringify(couponData),
    });
  },

  async delete(code) {
    return request(`/coupons/${code}`, {
      method: 'DELETE',
    });
  },

  async deactivate(code) {
    return request(`/coupons/${code}/deactivate`, {
      method: 'POST',
    });
  },
};

// ==================== REVIEWS ====================

export const reviews = {
  async getByProduct(productId, params = {}) {
    const query = new URLSearchParams(params).toString();
    return request(`/reviews/product/${productId}?${query}`, { skipAuth: true });
  },

  async getProductSummary(productId) {
    return request(`/reviews/product/${productId}/summary`, { skipAuth: true });
  },

  async create(reviewData) {
    return request('/reviews/', {
      method: 'POST',
      body: JSON.stringify(reviewData),
    });
  },

  async getMyReviews(params = {}) {
    const query = new URLSearchParams(params).toString();
    return request(`/reviews/my-reviews?${query}`);
  },

  async update(reviewId, reviewData) {
    return request(`/reviews/${reviewId}`, {
      method: 'PATCH',
      body: JSON.stringify(reviewData),
    });
  },

  async delete(reviewId) {
    return request(`/reviews/${reviewId}`, {
      method: 'DELETE',
    });
  },

  async markHelpful(reviewId) {
    return request(`/reviews/${reviewId}/helpful`, {
      method: 'POST',
    });
  },
};

// ==================== WISHLIST ====================

export const wishlist = {
  async get() {
    return request('/wishlist/');
  },

  async getProducts() {
    return request('/wishlist/products');
  },

  async add(productId) {
    return request(`/wishlist/add/${productId}`, {
      method: 'POST',
    });
  },

  async remove(productId) {
    return request(`/wishlist/remove/${productId}`, {
      method: 'DELETE',
    });
  },

  async toggle(productId) {
    return request(`/wishlist/toggle/${productId}`, {
      method: 'POST',
    });
  },

  async check(productId) {
    return request(`/wishlist/check/${productId}`);
  },

  async clear() {
    return request('/wishlist/clear', {
      method: 'DELETE',
    });
  },
};