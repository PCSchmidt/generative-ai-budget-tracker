/**
 * API Service for AI Budget Tracker Web App
 * Handles all backend communication with authentication
 */

import MockApiService from './mockApi';

// Simple event emitter for cross-component notifications
const listeners = new Map();
function on(event, cb) {
  if (!listeners.has(event)) listeners.set(event, new Set());
  listeners.get(event).add(cb);
  return () => listeners.get(event)?.delete(cb);
}
function emit(event, payload) {
  const set = listeners.get(event);
  if (set) set.forEach((cb) => {
    try { cb(payload); } catch {}
  });
}

// API Configuration (allow override via CRA env var)
// Prefer REACT_APP_API_BASE_URL; accept REACT_APP_BASE_URL as a legacy/alias
const API_BASE_URL = (
  process.env.REACT_APP_API_BASE_URL?.trim() ||
  process.env.REACT_APP_BASE_URL?.trim() ||
  (process.env.NODE_ENV === 'development'
    ? 'http://localhost:8000'  // Local development default
    : 'https://generative-ai-budget-tracker-production.up.railway.app' // Railway production default
  )
);
// Optional demo flag: allow mock fallback even in production (for frontend-only demo)
const ALLOW_PROD_MOCK = String(process.env.REACT_APP_ALLOW_MOCK_PROD || '').toLowerCase() === 'true';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.accessToken = null;
    this.refreshToken = null; // optional, backend may not provide
    this.mockService = new MockApiService();
    this.useMockService = false; // Force use of real backend for development
  this.backendChecked = false;
    
    // For development: force backend usage
    if (process.env.NODE_ENV === 'development') {
      console.log('🔧 Development mode: preferring backend if available at', this.baseURL);
      // Do not mark backendChecked here; let checkBackendAvailability decide.
      this.useMockService = false;
      this.backendChecked = false;
    }

    // Always log the resolved API base URL once at startup for easier prod debugging
    try {
      // eslint-disable-next-line no-console
      console.info('[ApiService] Base URL:', this.baseURL);
    } catch {}
  }

  // Public status getter for dev badge
  getStatus() {
    return {
      baseURL: this.baseURL,
      usingMock: this.useMockService,
  checked: this.backendChecked,
  ts: Date.now(),
  healthURL: `${this.baseURL}/health`,
    };
  }

  // Check if backend is available
  async checkBackendAvailability() {
    const isDev = process.env.NODE_ENV === 'development';
    // In development, allow falling back to mock to keep UX smooth
    if (isDev) {
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
          emit('backend_status', this.getStatus());
          return true;
        } else {
          console.warn('⚠️ Backend responded but with error status:', response.status);
          this.useMockService = true;
          this.backendChecked = true;
          emit('backend_status', this.getStatus());
          return false;
        }
      } catch (error) {
        console.error('❌ Backend connection failed:', error.message);
        this.useMockService = true;
        this.backendChecked = true;
        emit('backend_status', this.getStatus());
        return false;
      }
    }
    
  // Production: by default never fall back to mock; optional demo flag can allow fallback
  if (this.backendChecked) return !this.useMockService;
    
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 second timeout
      
  const response = await fetch(`${this.baseURL}/health`, {
        method: 'GET',
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
  // In production, do not switch to mock unless explicitly allowed for demo
  this.useMockService = !response.ok && ALLOW_PROD_MOCK;
  this.backendChecked = true;
      
      if (!response.ok) {
        console.warn('⚠️ Backend health check failed in production:', response.status, 'mockAllowed:', ALLOW_PROD_MOCK);
      } else {
        console.log('✅ Backend is available');
      }
  emit('backend_status', this.getStatus());
      return !this.useMockService;
    } catch (error) {
      console.error('❌ Backend health check error in production:', error.message, 'mockAllowed:', ALLOW_PROD_MOCK);
      this.useMockService = !!ALLOW_PROD_MOCK;
      this.backendChecked = true;
      emit('backend_status', this.getStatus());
      return !this.useMockService;
    }
  }

  // Initialize tokens from storage
  async initializeTokens() {
    try {
      const accessToken = localStorage.getItem('accessToken');
      const refreshToken = localStorage.getItem('refreshToken');
      
      if (accessToken) this.accessToken = accessToken;
      // Only use refreshToken if it's a non-empty, non-'undefined' value
      if (refreshToken && refreshToken !== 'undefined') {
        this.refreshToken = refreshToken;
      } else {
        this.refreshToken = null;
      }
      
      return { accessToken, refreshToken: this.refreshToken };
    } catch (error) {
      console.error('Failed to load tokens:', error);
      return { accessToken: null, refreshToken: null };
    }
  }

  // Store tokens securely (refresh token optional)
  async storeTokens(accessToken, refreshToken = null) {
    try {
      if (accessToken) {
        localStorage.setItem('accessToken', accessToken);
        this.accessToken = accessToken;
      }
      // Only persist refresh token if provided by backend
      if (refreshToken && refreshToken !== 'undefined') {
        localStorage.setItem('refreshToken', refreshToken);
        this.refreshToken = refreshToken;
      } else {
        localStorage.removeItem('refreshToken');
        this.refreshToken = null;
      }
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
      'Authorization': this.accessToken ? `Bearer ${this.accessToken}` : undefined,
      'Content-Type': 'application/json',
    };
  }

  // Make authenticated request (with one-time auto refresh on 401)
  async request(endpoint, options = {}, retry = true) {
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

      // Attempt a one-time silent refresh if unauthorized and we have a refresh token
      if (response.status === 401 && retry && this.refreshToken) {
        try {
          const refreshResp = await fetch(`${this.baseURL}/auth/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: this.refreshToken })
          });

          if (refreshResp.ok) {
            const data = await refreshResp.json();
            await this.storeTokens(data.access_token, data.refresh_token ?? null);
            emit('token_refreshed', { ts: Date.now() });
            // Retry original request once with new token
            const retryConfig = { ...config, headers: { ...config.headers, Authorization: `Bearer ${this.accessToken}` } };
            return await this.request(endpoint, retryConfig, false);
          } else {
            // Refresh failed; clear and propagate original response
            await this.clearTokens();
          }
        } catch (e) {
          // Network/other error on refresh; clear tokens
          await this.clearTokens();
        }
      }

      return response;
    } catch (error) {
  // Provide a clearer message when fetch fails (commonly CORS or wrong base URL)
  const method = (config && config.method) || 'GET';
  const hint = 'This is usually a CORS issue on the backend or an incorrect REACT_APP_API_BASE_URL/REACT_APP_BASE_URL.';
  const msg = `Network error for ${method} ${url} — ${hint} Original: ${error?.message || error}`;
  // eslint-disable-next-line no-console
  console.error('API Request failed:', msg);
  throw new Error(msg);
    }
  }

  // Authentication endpoints
  async signup(userData) {
    await this.checkBackendAvailability();
    
    if (this.useMockService) {
  const data = await this.mockService.signup(userData);
  // Persist tokens and user locally for session restoration
  await this.storeTokens(data.access_token, data.refresh_token ?? null);
  localStorage.setItem('user', JSON.stringify(data.user));
  return data;
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

      // Store tokens and user data (refresh token optional)
      await this.storeTokens(data.access_token, data.refresh_token ?? null);
      localStorage.setItem('user', JSON.stringify(data.user));

      return data; // Return the full response
    } catch (error) {
      throw new Error(error.message || 'Signup failed');
    }
  }

  async login(email, password) {
    await this.checkBackendAvailability();
    
    if (this.useMockService) {
  const data = await this.mockService.login(email, password);
  // Persist tokens and user locally for session restoration
  await this.storeTokens(data.access_token, data.refresh_token ?? null);
  localStorage.setItem('user', JSON.stringify(data.user));
  return data;
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

      // Store tokens and user data (refresh token optional)
      await this.storeTokens(data.access_token, data.refresh_token ?? null);
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
      // Call logout endpoint only if we truly have a refresh token and backend supports it
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

  // Keep refreshAccessToken for future, but it's unused
  async refreshAccessToken() {
    return false;
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

  // Paginated expenses with optional month (YYYY-MM)
  async getExpensesPaginated({ page = 1, page_size = 10, month = null } = {}) {
    await this.checkBackendAvailability();

    if (this.useMockService) {
      // Simple mock pagination/filtering
      const res = await this.mockService.getExpenses();
      let list = res.expenses || res || [];
      if (month) {
        list = list.filter(e => String(e.expense_date || e.created_at || '').startsWith(month));
      }
      const total = list.length;
      const start = (page - 1) * page_size;
      const items = list.slice(start, start + page_size);
      return { items, total, page, page_size };
    }

    try {
      const params = new URLSearchParams({ page: String(page), page_size: String(page_size) });
      if (month) params.append('month', month);
      const response = await this.request(`/api/expenses/paginated?${params.toString()}`);
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || 'Failed to get paginated expenses');
      return data;
    } catch (error) {
      console.error('Paginated expenses error:', error);
      throw error;
    }
  }

  // Expense summary for charts (optionally filter by month: YYYY-MM)
  async getExpenseSummary(month = null) {
    await this.checkBackendAvailability();

    if (this.useMockService) {
      // Build mock summary from mock expenses
      const mock = await this.mockService.getExpenses();
      const expenses = mock.expenses || mock || [];
      const byCat = {};
      let total = 0; let count = 0;
      for (const e of expenses) {
        if (month) {
          const d = e.expense_date || e.created_at || '';
          if (!String(d).startsWith(month)) continue;
        }
        const cat = e.category || 'Other';
        byCat[cat] = byCat[cat] || { total: 0, count: 0 };
        byCat[cat].total += Number(e.amount || 0);
        byCat[cat].count += 1;
        total += Number(e.amount || 0);
        count += 1;
      }
      return {
        total_amount: Number(total.toFixed(2)),
        total_count: count,
        categories: Object.entries(byCat).map(([k, v]) => ({ category: k, total_amount: Number(v.total.toFixed(2)), count: v.count }))
      };
    }

    try {
      const qs = month ? `?month=${encodeURIComponent(month)}` : '';
      const response = await this.request(`/api/expenses/summary${qs}`);
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to get expense summary');
      }
      return data;
    } catch (error) {
      console.error('Get expense summary error:', error);
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
  // Delegate to the canonical spending insights endpoint
  return await this.getSpendingInsights();
  }

  // ======= NEW ML-POWERED ENDPOINTS =======

  // Smart AI categorization endpoint
  async categorizeExpenseSmart(description, amount = null) {
    await this.checkBackendAvailability();
    
    if (this.useMockService) {
      // Mock smart categorization for offline development
      return {
        success: true,
        categorization: {
          category: this.mockService.categorizeExpense(description),
          confidence: 0.75,
          method: 'mock_ai',
          reasoning: 'Mock AI categorization for development'
        },
        ml_enhanced: false
      };
    }

    try {
      const params = new URLSearchParams({ description });
      if (amount !== null) params.append('amount', amount.toString());
      
      const response = await this.request(`/api/ai/categorize-smart?${params}`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Smart categorization failed');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Smart categorization error:', error);
      // Fallback to basic categorization
      return {
        success: false,
        error: error.message,
        categorization: {
          category: 'Miscellaneous',
          confidence: 0.1,
          method: 'fallback',
          reasoning: 'Error during categorization'
        }
      };
    }
  }

  // Get personalized financial advice
  async getFinancialAdvice(adviceType = 'general', includeProfile = false) {
    await this.checkBackendAvailability();
    
    if (this.useMockService) {
      // Mock financial advice for offline development
      return {
        success: true,
        advice: {
          advice_type: adviceType,
          main_advice: "Continue tracking your expenses to identify spending patterns and opportunities for improvement.",
          action_items: [
            "Review your largest expense categories",
            "Set up automatic savings transfers",
            "Track daily expenses for better awareness"
          ],
          confidence: 0.6,
          processing_method: 'mock_advisor'
        },
        expense_count: 5,
        ml_enhanced: false
      };
    }

    try {
      const params = new URLSearchParams({ advice_type: adviceType });
      if (includeProfile) params.append('include_profile', 'true');
      
      const response = await this.request(`/api/ai/financial-advice?${params}`, {
        method: 'POST',
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get financial advice');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Financial advice error:', error);
      return {
        success: false,
        error: error.message,
        advice: {
          main_advice: "Unable to generate personalized advice at this time. Continue tracking expenses for better insights.",
          action_items: ["Keep tracking expenses"],
          confidence: 0.1
        }
      };
    }
  }

  // Get spending insights and patterns
  async getSpendingInsights() {
    await this.checkBackendAvailability();
    
    if (this.useMockService) {
      // Mock spending insights for offline development
      return {
        success: true,
        insights: {
          total_spending: 1250.75,
          category_breakdown: {
            'Food & Dining': 450.25,
            'Transportation': 320.50,
            'Entertainment': 180.00,
            'Shopping': 200.00,
            'Miscellaneous': 100.00
          },
          expense_count: 12,
          average_expense: 104.23,
          recommendations: [
            "Consider meal planning to reduce dining expenses",
            "Review transportation alternatives",
            "Set a monthly entertainment budget"
          ]
        },
        expense_count: 12,
        ml_enhanced: false
      };
    }

    try {
      const response = await this.request('/api/ai/spending-insights');

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get spending insights');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Spending insights error:', error);
      return {
        success: false,
        error: error.message,
        insights: {
          error: "Unable to generate insights at this time"
        }
      };
    }
  }

  // Get AI system status
  async getAISystemStatus() {
    await this.checkBackendAvailability();
    
    if (this.useMockService) {
      return {
        ai_available: false,
        ml_enhanced: false,
        services: {
          basic_categorization: "mock_only",
          financial_advisor: "unavailable",
          spending_insights: "basic_only"
        },
        timestamp: new Date().toISOString()
      };
    }

    try {
      const response = await this.request('/api/ai/status');

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get AI status');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('AI status error:', error);
      return {
        ai_available: false,
        ml_enhanced: false,
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  // Batch categorize multiple expenses
  async batchCategorizeExpenses(descriptions) {
    await this.checkBackendAvailability();
    
    if (this.useMockService) {
      // Mock batch categorization
      return {
        success: true,
        results: descriptions.map((desc, index) => ({
          index,
          description: desc,
          categorization: {
            category: this.mockService.categorizeExpense(desc),
            confidence: 0.6,
            method: 'mock_batch'
          }
        })),
        total_processed: descriptions.length,
        ml_enhanced: false
      };
    }

    try {
      const response = await this.request('/api/ai/batch-categorize', {
        method: 'POST',
        body: JSON.stringify({ expense_descriptions: descriptions }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Batch categorization failed');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Batch categorization error:', error);
      return {
        success: false,
        error: error.message,
        results: []
      };
    }
  }

  // Enhanced expense creation with smart categorization
  async createExpenseWithAI(expenseData) {
    await this.checkBackendAvailability();
    
    // If no category provided, get AI suggestion first
    if (!expenseData.category && expenseData.description) {
      try {
        console.log('🤖 Getting AI categorization for:', expenseData.description);
        const categorizationResult = await this.categorizeExpenseSmart(
          expenseData.description, 
          expenseData.amount
        );
        
        if (categorizationResult.success) {
          expenseData.category = categorizationResult.categorization.category;
          console.log('✅ AI suggested category:', expenseData.category);
        }
      } catch (error) {
        console.warn('⚠️ AI categorization failed, proceeding without category:', error);
      }
    }
    
    // Create expense using existing method
    return await this.createExpense(expenseData);
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

  // NEW: Simple AI categorization (no auth required)
  async categorizeExpense(description, amount = null) {
    await this.checkBackendAvailability();

    if (this.useMockService) {
      return {
        success: true,
        category: this.mockService.categorizeExpense(description),
        confidence: 0.6,
        method: 'mock_public_ai'
      };
    }

    try {
      const params = new URLSearchParams({ description });
      if (amount !== null && !Number.isNaN(Number(amount))) params.append('amount', String(amount));

      const response = await this.request(`/api/ai/categorize?${params.toString()}`, { method: 'POST' });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Categorization failed');
      }
      return data; // { success, category, confidence, method }
    } catch (error) {
      console.error('Public categorization error:', error);
      return {
        success: false,
        category: 'Miscellaneous',
        confidence: 0.1,
        method: 'fallback',
        error: error.message
      };
    }
  }

  // NEW: Budgets API
  async getBudgets() {
    await this.checkBackendAvailability();
    if (this.useMockService) {
      return await this.mockService.getBudgets();
    }
    const response = await this.request('/api/budgets');
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Failed to load budgets');
    return data; // Expect { budgets: [...] } or list
  }
  async createBudget(payload) {
    await this.checkBackendAvailability();
    if (this.useMockService) {
      return await this.mockService.createBudget(payload);
    }
    const response = await this.request('/api/budgets', { method: 'POST', body: JSON.stringify(payload) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Failed to create budget');
    return data;
  }
  async updateBudget(id, payload) {
    await this.checkBackendAvailability();
    if (this.useMockService) {
      return await this.mockService.updateBudget(id, payload);
    }
    const response = await this.request(`/api/budgets/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Failed to update budget');
    return data;
  }
  async deleteBudget(id) {
    await this.checkBackendAvailability();
    if (this.useMockService) {
      return await this.mockService.deleteBudget(id);
    }
    const response = await this.request(`/api/budgets/${id}`, { method: 'DELETE' });
    if (!response.ok) { try { const d = await response.json(); throw new Error(d.detail||'Failed to delete budget'); } catch { throw new Error('Failed to delete budget'); } }
    return { success: true };
  }
  // NEW: Goals API
  async getGoals() {
    await this.checkBackendAvailability();
    if (this.useMockService) {
      return await this.mockService.getGoals();
    }
    const response = await this.request('/api/goals');
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Failed to load goals');
    return data;
  }
  async createGoal(payload) {
    await this.checkBackendAvailability();
    if (this.useMockService) {
      return await this.mockService.createGoal(payload);
    }
    const response = await this.request('/api/goals', { method: 'POST', body: JSON.stringify(payload) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Failed to create goal');
    return data;
  }
  async updateGoal(id, payload) {
    await this.checkBackendAvailability();
    if (this.useMockService) {
      return await this.mockService.updateGoal(id, payload);
    }
    const response = await this.request(`/api/goals/${id}`, { method: 'PUT', body: JSON.stringify(payload) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Failed to update goal');
    return data;
  }
  async deleteGoal(id) {
    await this.checkBackendAvailability();
    if (this.useMockService) {
      return await this.mockService.deleteGoal(id);
    }
    const response = await this.request(`/api/goals/${id}`, { method: 'DELETE' });
    if (!response.ok) { try { const d = await response.json(); throw new Error(d.detail||'Failed to delete goal'); } catch { throw new Error('Failed to delete goal'); } }
    return { success: true };
  }
  async contributeGoal(id, amount) {
    await this.checkBackendAvailability();
    if (this.useMockService) {
      return await this.mockService.contributeGoal(id, amount);
    }
    const response = await this.request(`/api/goals/${id}/contribute`, { method: 'POST', body: JSON.stringify({ amount }) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Failed to contribute');
    return data;
  }
}

// Export singleton instance
const apiService = new ApiService();

// Initialize tokens on module load
apiService.initializeTokens();

export { apiService };
export default apiService;
export const ApiEvents = { on };
export async function recheckBackend() {
  await apiService.checkBackendAvailability();
  return apiService.getStatus();
}
