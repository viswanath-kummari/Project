/* ==========================================================================
   API CLIENT & TOKEN MANAGEMENT
   Fresh Cut Meat Shop Management System
   ========================================================================== */

const API_BASE = '/api';

const Api = {
  getToken() {
    return localStorage.getItem('fc_auth_token') || sessionStorage.getItem('fc_auth_token');
  },

  getUser() {
    const raw = localStorage.getItem('fc_auth_user') || sessionStorage.getItem('fc_auth_user');
    try {
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  },

  setAuth(token, user, remember = true) {
    const storage = remember ? localStorage : sessionStorage;
    storage.setItem('fc_auth_token', token);
    storage.setItem('fc_auth_user', JSON.stringify(user));
  },

  clearAuth() {
    localStorage.removeItem('fc_auth_token');
    localStorage.removeItem('fc_auth_user');
    sessionStorage.removeItem('fc_auth_token');
    sessionStorage.removeItem('fc_auth_user');
  },

  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    };

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      // Handle 401 Unauthorized
      if (response.status === 401 && !endpoint.includes('/auth/login')) {
        this.clearAuth();
        window.dispatchEvent(new CustomEvent('auth:expired'));
        throw new Error('Your session has expired. Please sign in again.');
      }

      // Handle 403 Forbidden
      if (response.status === 403) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Access denied: Admin privileges required.');
      }

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.error || `Request failed with status ${response.status}`);
      }

      return data;
    } catch (err) {
      console.error(`API Error on ${endpoint}:`, err);
      throw err;
    }
  },

  get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  },

  post(endpoint, body) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(body)
    });
  },

  put(endpoint, body) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(body)
    });
  },

  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }
};
