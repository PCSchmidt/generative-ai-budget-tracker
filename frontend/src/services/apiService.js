/**
 * API Service for AI Budget Tracker
 * Connects to your live Railway API at: https://postgres-production-1826.up.railway.app
 */

const API_BASE_URL = 'https://postgres-production-1826.up.railway.app';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async makeRequest(endpoint, options = {}) {
    try {
      const url = `${this.baseURL}${endpoint}`;
      const config = {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      };

      console.log(`🌐 API Request: ${config.method || 'GET'} ${url}`);
      
      const response = await fetch(url, config);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || `HTTP ${response.status}`);
      }

      console.log(`✅ API Response:`, data);
      return data;
    } catch (error) {
      console.error(`❌ API Error for ${endpoint}:`, error);
      throw error;
    }
  }

  // Health check
  async getHealth() {
    return this.makeRequest('/health');
  }

  // Get all expenses
  async getExpenses() {
    return this.makeRequest('/api/expenses');
  }

  // Create new expense
  async createExpense(expenseData) {
    return this.makeRequest('/api/expenses', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        description: expenseData.description,
        amount: expenseData.amount.toString(),
        category: expenseData.category || '',
      }),
    });
  }

  // Get AI insights
  async getInsights() {
    return this.makeRequest('/api/insights');
  }

  // Test AI categorization
  async categorizeExpense(description, amount = 0) {
    return this.makeRequest(`/api/ai/categorize?description=${encodeURIComponent(description)}&amount=${amount}`);
  }

  // Get API info
  async getApiInfo() {
    return this.makeRequest('/');
  }
}

export default new ApiService();
