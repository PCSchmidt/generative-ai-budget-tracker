/**
 * API Service for AI Budget Tracker Web App
 * Handles all backend communication with authentication
 */

// API Configuration
const API_BASE_URL = process.env.NODE_ENV === 'development' 
  ? 'http://localhost:8000'  // Local development
  : 'https://your-railway-domain.railway.app'; // Production

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.accessToken = null;
    this.refreshToken = null;
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

  // Expense endpoints (ready for future implementation)
  async getExpenses(params = {}) {
    try {
      const queryString = new URLSearchParams(params).toString();
      const response = await this.request(`/expenses?${queryString}`);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to get expenses');
      }

      return { success: true, expenses: data };
    } catch (error) {
      return {
        success: false,
        error: error.message || 'Failed to get expenses',
      };
    }
  }

  async createExpense(expenseData) {
    try {
      const response = await this.request('/expenses', {
        method: 'POST',
        body: JSON.stringify(expenseData),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to create expense');
      }

      return { success: true, expense: data };
    } catch (error) {
      return {
        success: false,
        error: error.message || 'Failed to create expense',
      };
    }
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
export default new ApiService();
