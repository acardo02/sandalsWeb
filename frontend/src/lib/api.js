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
      throw new Error(error.detail || `Error ${response.status}`);
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    
    return null;
  } catch (error) {
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

  async getMyOrders() {
    return request('/orders/me');
  },

  async getAll(params = {}) {
    const query = new URLSearchParams(params).toString();
    return request(`/orders/?${query}`);
  },

  async updateStatus(orderId, status) {
    return request(`/orders/${orderId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
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