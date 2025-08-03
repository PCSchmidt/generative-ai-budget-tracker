/**
 * API Service for AI Budget Tracker Web App
 * Handles all backend communication with authentication
 */

import MockApiService from './mockApi';

// API Configuration
const API_BASE_URL = process.env.NODE_ENV === 'development' 
  ? 'http://localhost:8000'  // Local development
  : 'https://generative-ai-budget-tracker-production.up.railway.app'; // Railway production

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.accessToken = null;
    this.refreshToken = null;
    this.mockService = new MockApiService();
    this.useMockService = false; // Force use of real backend for development
    this.backendChecked = false;
    
    // For development: force backend usage
    if (process.env.NODE_ENV === 'development') {
      console.log('🔧 Development mode: Forcing backend connection to', this.baseURL);
      this.useMockService = false;
      this.backendChecked = true;
    }
  }

  // Check if backend is available
  async checkBackendAvailability() {
    // In development, always try the backend first
    if (process.env.NODE_ENV === 'development') {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout for dev
        
        console.log('🔍 Checking backend availability at:', `${this.baseURL}/health`);
        
        const response = await fetch(`${this.baseURL}/health`, {
          method: 'GET',
          signal: controller.signal,
          headers: {
            'Content-Type': 'application/json',
          }
        });
        
        clearTimeout(timeoutId);
        
        if (response.ok) {
          this.useMockService = false;
          this.backendChecked = true;
          console.log('✅ Backend is available and responding');
          return true;
        } else {
          console.warn('⚠️ Backend responded but with error status:', response.status);
          this.useMockService = true;
          this.backendChecked = true;
          return false;
        }
      } catch (error) {
        console.error('❌ Backend connection failed:', error.message);
        this.useMockService = true;
        this.backendChecked = true;
        return false;
      }
    }
    
    // Original logic for production
    if (this.backendChecked) return !this.useMockService;
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout
      
      const response = await fetch(`${this.baseURL}/health`, {
        method: 'GET',
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      this.useMockService = !response.ok;
      this.backendChecked = true;
      
      if (this.useMockService) {
        console.log('🚧 Backend not available, using mock service for development');
      } else {
        console.log('✅ Backend is available');
      }
      
      return !this.useMockService;
    } catch (error) {
      console.log('🚧 Backend not available, using mock service for development');
      this.useMockService = true;
      this.backendChecked = true;
      return false;
    }
  }

  // Initialize tokens from storage
  async initializeTokens() {
    try {
      const accessToken = localStorage.getItem('accessToken');
      const refreshToken = localStorage.getItem('refreshToken');
      
      if (accessToken) this.accessToken = accessToken;
      if (refreshToken) this.refreshToken = refreshToken;
      
      return { accessToken, refreshToken };
    } catch (error) {
      console.error('Failed to load tokens:', error);
      return { accessToken: null, refreshToken: null };
    }
  }

  // Store tokens securely
  async storeTokens(accessToken, refreshToken) {
    try {
      localStorage.setItem('accessToken', accessToken);
      localStorage.setItem('refreshToken', refreshToken);
      
      this.accessToken = accessToken;
      this.refreshToken = refreshToken;
    } catch (error) {
      console.error('Failed to store tokens:', error);
      throw new Error('Failed to store authentication tokens');
    }
  }

  // Clear all tokens
  async clearTokens() {
    try {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      localStorage.removeItem('user');
      this.accessToken = null;
      this.refreshToken = null;
    } catch (error) {
      console.error('Failed to clear tokens:', error);
    }
  }

  // Get auth headers
  getAuthHeaders() {
    return {
      'Authorization': `Bearer ${this.accessToken}`,
      'Content-Type': 'application/json',
    };
  }

  // Make authenticated request
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    // Add auth header if token exists
    if (this.accessToken) {
      config.headers.Authorization = `Bearer ${this.accessToken}`;
    }

    try {
      const response = await fetch(url, config);
      
      // Handle 401 - try to refresh token
      if (response.status === 401 && this.refreshToken) {
        const refreshed = await this.refreshAccessToken();
        if (refreshed) {
          // Retry original request with new token
          config.headers.Authorization = `Bearer ${this.accessToken}`;
          return await fetch(url, config);
        }
      }

      return response;
    } catch (error) {
      console.error('API Request failed:', error);
      throw error;
    }
  }

  // Authentication endpoints
  async signup(userData) {
    await this.checkBackendAvailability();
    
    if (this.useMockService) {
      return await this.mockService.signup(userData);
    }

    try {
      const response = await this.request('/auth/signup', {
        method: 'POST',
        body: JSON.stringify(userData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Signup failed');
      }

      // Store tokens and user data
      await this.storeTokens(data.access_token, data.refresh_token);
      localStorage.setItem('user', JSON.stringify(data.user));

      return data; // Return the full response
    } catch (error) {
      throw new Error(error.message || 'Signup failed');
    }
  }

  async login(email, password) {
    await this.checkBackendAvailability();
    
    if (this.useMockService) {
      return await this.mockService.login(email, password);
    }
    try {
      const response = await this.request('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Login failed');
      }

      // Store tokens and user data
      await this.storeTokens(data.access_token, data.refresh_token);
      localStorage.setItem('user', JSON.stringify(data.user));

      return data; // Return the full response
    } catch (error) {
      throw new Error(error.message || 'Login failed');
    }
  }

  async logout() {
    if (this.useMockService) {
      await this.mockService.logout();
      await this.clearTokens();
      return { message: 'Logged out successfully' };
    }

    try {
      // Call logout endpoint if we have a refresh token
      if (this.refreshToken) {
        await this.request('/auth/logout', {
          method: 'POST',
          body: JSON.stringify({ refresh_token: this.refreshToken }),
        });
      }

      // Clear all local data
      await this.clearTokens();

      return { success: true };
    } catch (error) {
      // Still clear local data even if API call fails
      await this.clearTokens();
      return { success: true };
    }
  }

  async refreshAccessToken() {
    if (!this.refreshToken) return false;

    try {
      const response = await this.request('/auth/refresh', {
        method: 'POST',
        body: JSON.stringify({ refresh_token: this.refreshToken }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      // Update stored tokens
      await this.storeTokens(data.access_token, data.refresh_token);

      return true;
    } catch (error) {
      console.error('Token refresh failed:', error);
      // Clear invalid tokens
      await this.clearTokens();
      return false;
    }
  }

  // User profile endpoints
  async getCurrentUser() {
    try {
      const response = await this.request('/auth/me');
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to get user profile');
      }

      return { success: true, user: data };
    } catch (error) {
      return {
        success: false,
        error: error.message || 'Failed to get user profile',
      };
    }
  }

  // Expense endpoints
  async getExpenses(params = {}) {
    await this.checkBackendAvailability();
    
    if (this.useMockService) {
      return await this.mockService.getExpenses();
    }

    try {
      const queryString = new URLSearchParams(params).toString();
      const endpoint = queryString ? `/api/expenses?${queryString}` : '/api/expenses';
      const response = await this.request(endpoint);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get expenses');
      }
      
      const data = await response.json();
      return data; // Return data directly for compatibility
    } catch (error) {
      console.error('Get expenses error:', error);
      throw error;
    }
  }

  async createExpense(expenseData) {
    await this.checkBackendAvailability();
    
    if (this.useMockService) {
      return await this.mockService.createExpense(expenseData);
    }

    try {
      const response = await this.request('/api/expenses', {
        method: 'POST',
        body: JSON.stringify(expenseData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create expense');
      }

      const data = await response.json();
      return data; // Return data directly for compatibility
    } catch (error) {
      console.error('Create expense error:', error);
      throw error;
    }
  }

  async updateExpense(expenseId, expenseData) {
    await this.checkBackendAvailability();
    
    if (this.useMockService) {
      return await this.mockService.updateExpense(expenseId, expenseData);
    }

    try {
      const response = await this.request(`/api/expenses/${expenseId}`, {
        method: 'PUT',
        body: JSON.stringify(expenseData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update expense');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Update expense error:', error);
      throw error;
    }
  }

  async deleteExpense(expenseId) {
    await this.checkBackendAvailability();
    
    if (this.useMockService) {
      return await this.mockService.deleteExpense(expenseId);
    }

    try {
      const response = await this.request(`/api/expenses/${expenseId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete expense');
      }

      return { success: true };
    } catch (error) {
      console.error('Delete expense error:', error);
      throw error;
    }
  }

  // Generic method for all API calls
  async get(endpoint) {
    const response = await this.request(endpoint);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Failed to fetch ${endpoint}`);
    }
    return await response.json();
  }

  async post(endpoint, data) {
    const response = await this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Failed to post to ${endpoint}`);
    }
    return await response.json();
  }

  // AI Insights endpoints (ready for future implementation)
  async getInsights() {
    try {
      const response = await this.request('/insights');
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to get insights');
      }

      return { success: true, insights: data };
    } catch (error) {
      return {
        success: false,
        error: error.message || 'Failed to get insights',
      };
    }
  }

  // Analytics endpoints (ready for future implementation)
  async getAnalytics(period = 'month') {
    try {
      const response = await this.request(`/analytics?period=${period}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to get analytics');
      }

      return { success: true, analytics: data };
    } catch (error) {
      return {
        success: false,
        error: error.message || 'Failed to get analytics',
      };
    }
  }
}

// Export singleton instance
const apiService = new ApiService();

// Initialize tokens on module load
apiService.initializeTokens();

export { apiService };
export default apiService;
