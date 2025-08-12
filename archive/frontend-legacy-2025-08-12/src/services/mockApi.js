/**
 * Mock API Service for Development
 * Provides realistic mock responses for authentication and expense management
 */

class MockApiService {
  constructor() {
    this.users = [
      {
        id: 1,
        email: 'demo@budgettracker.com',
        username: 'demo',
        first_name: 'Demo',
        last_name: 'User',
        password: 'password123' // In real app, this would be hashed
      }
    ];
    
    this.expenses = [
      {
        id: 1,
        user_id: 1,
        description: 'Coffee at Starbucks',
        amount: 4.95,
        category: 'Food & Dining',
        expense_date: '2025-01-30',
        notes: 'Morning coffee',
        created_at: '2025-01-30T08:30:00Z'
      },
      {
        id: 2,
        user_id: 1,
        description: 'Uber ride home',
        amount: 12.50,
        category: 'Transportation',
        expense_date: '2025-01-29',
        notes: '',
        created_at: '2025-01-29T18:45:00Z'
      },
      {
        id: 3,
        user_id: 1,
        description: 'Netflix subscription',
        amount: 15.99,
        category: 'Entertainment',
        expense_date: '2025-01-28',
        notes: 'Monthly subscription',
        created_at: '2025-01-28T12:00:00Z'
      }
    ];
  }

  // Simulate API delay
  async delay(ms = 500) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Generate mock JWT token
  generateMockToken(userId) {
    const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
    const payload = btoa(JSON.stringify({ 
      user_id: userId, 
      exp: Math.floor(Date.now() / 1000) + 3600 // 1 hour from now
    }));
    const signature = btoa('mock-signature');
    return `${header}.${payload}.${signature}`;
  }

  // Mock Authentication
  async signup(userData) {
    await this.delay(1000); // Simulate network delay

    // Check if user already exists
    const existingUser = this.users.find(u => u.email === userData.email);
    if (existingUser) {
      throw new Error('User with this email already exists');
    }

    // Create new user
    const newUser = {
      id: this.users.length + 1,
      email: userData.email,
      username: userData.username || userData.email.split('@')[0],
      first_name: userData.first_name || '',
      last_name: userData.last_name || '',
      password: userData.password
    };

    this.users.push(newUser);

    // Generate tokens
    const accessToken = this.generateMockToken(newUser.id);
    const refreshToken = this.generateMockToken(newUser.id);

    // Return user data without password
    const { password, ...userWithoutPassword } = newUser;

    return {
      access_token: accessToken,
      refresh_token: refreshToken,
      user: userWithoutPassword
    };
  }

  async login(email, password) {
    await this.delay(800); // Simulate network delay

    // Find user
    const user = this.users.find(u => u.email === email);
    if (!user || user.password !== password) {
      throw new Error('Invalid email or password');
    }

    // Generate tokens
    const accessToken = this.generateMockToken(user.id);
    const refreshToken = this.generateMockToken(user.id);

    // Return user data without password
    const { password: _, ...userWithoutPassword } = user;

    return {
      access_token: accessToken,
      refresh_token: refreshToken,
      user: userWithoutPassword
    };
  }

  async logout() {
    await this.delay(200);
    // In mock, just return success
    return { message: 'Logged out successfully' };
  }

  async refreshToken() {
    await this.delay(300);
    
    // Generate new tokens
    const accessToken = this.generateMockToken(1); // Mock user ID
    const refreshToken = this.generateMockToken(1);

    return {
      access_token: accessToken,
      refresh_token: refreshToken
    };
  }

  // Mock Expenses
  async getExpenses(userId = 1) {
    await this.delay(600);
    const userExpenses = this.expenses.filter(expense => expense.user_id === userId);
    return { expenses: userExpenses }; // Return in expected format
  }

  async createExpense(expenseData, userId = 1) {
    await this.delay(700);

    const newExpense = {
      id: this.expenses.length + 1,
      user_id: userId,
      description: expenseData.description,
      amount: parseFloat(expenseData.amount),
      category: expenseData.category || this.categorizeExpense(expenseData.description),
      expense_date: expenseData.expense_date || new Date().toISOString().split('T')[0],
      notes: expenseData.notes || '',
      created_at: new Date().toISOString()
    };

    this.expenses.push(newExpense);
    return newExpense;
  }

  async updateExpense(expenseId, expenseData, userId = 1) {
    await this.delay(600);

    const expenseIndex = this.expenses.findIndex(
      expense => expense.id === expenseId && expense.user_id === userId
    );

    if (expenseIndex === -1) {
      throw new Error('Expense not found');
    }

    this.expenses[expenseIndex] = {
      ...this.expenses[expenseIndex],
      ...expenseData,
      amount: parseFloat(expenseData.amount)
    };

    return this.expenses[expenseIndex];
  }

  async deleteExpense(expenseId, userId = 1) {
    await this.delay(400);

    const expenseIndex = this.expenses.findIndex(
      expense => expense.id === expenseId && expense.user_id === userId
    );

    if (expenseIndex === -1) {
      throw new Error('Expense not found');
    }

    this.expenses.splice(expenseIndex, 1);
    return { message: 'Expense deleted successfully' };
  }

  // AI-powered expense categorization (mock)
  categorizeExpense(description) {
    const desc = description.toLowerCase();
    
    if (desc.includes('coffee') || desc.includes('restaurant') || desc.includes('food') || desc.includes('lunch') || desc.includes('dinner')) {
      return 'Food & Dining';
    } else if (desc.includes('uber') || desc.includes('taxi') || desc.includes('gas') || desc.includes('fuel') || desc.includes('transport')) {
      return 'Transportation';
    } else if (desc.includes('netflix') || desc.includes('spotify') || desc.includes('movie') || desc.includes('game')) {
      return 'Entertainment';
    } else if (desc.includes('electric') || desc.includes('water') || desc.includes('internet') || desc.includes('phone')) {
      return 'Utilities';
    } else if (desc.includes('rent') || desc.includes('mortgage') || desc.includes('insurance')) {
      return 'Housing';
    } else if (desc.includes('doctor') || desc.includes('pharmacy') || desc.includes('medical') || desc.includes('health')) {
      return 'Healthcare';
    } else if (desc.includes('clothes') || desc.includes('shopping') || desc.includes('amazon') || desc.includes('store')) {
      return 'Shopping';
    } else {
      return 'Other';
    }
  }

  // Mock Statistics
  async getExpenseStats(userId = 1) {
    await this.delay(400);
    
    const userExpenses = this.expenses.filter(expense => expense.user_id === userId);
    const totalSpent = userExpenses.reduce((sum, expense) => sum + expense.amount, 0);
    const avgExpense = userExpenses.length > 0 ? totalSpent / userExpenses.length : 0;
    
    const categories = {};
    userExpenses.forEach(expense => {
      if (!categories[expense.category]) {
        categories[expense.category] = 0;
      }
      categories[expense.category] += expense.amount;
    });

    return {
      total_expenses: userExpenses.length,
      total_amount: totalSpent,
      average_expense: avgExpense,
      categories: categories,
      this_month: totalSpent, // Simplified for mock
      last_month: totalSpent * 0.8 // Mock comparison
    };
  }

  // Mock AI Insights
  async getInsights(userId = 1) {
    await this.delay(600);
    
    const userExpenses = this.expenses.filter(expense => expense.user_id === userId);
    const totalSpent = userExpenses.reduce((sum, expense) => sum + expense.amount, 0);
    
    // Mock AI-generated insights
    const insights = [
      {
        type: 'spending_pattern',
        message: 'You spend most on Food & Dining. Consider meal prep to save money.',
        confidence: 0.85
      },
      {
        type: 'budget_recommendation',
        message: `Based on your spending of $${totalSpent.toFixed(2)}, consider setting a monthly budget of $${(totalSpent * 1.1).toFixed(2)}.`,
        confidence: 0.92
      },
      {
        type: 'saving_opportunity',
        message: 'You could save $50/month by reducing transportation costs.',
        confidence: 0.78
      }
    ];

    return {
      insights: insights,
      total_analyzed: userExpenses.length,
      confidence_score: 0.85,
      last_updated: new Date().toISOString()
    };
  }
}

export default MockApiService;
