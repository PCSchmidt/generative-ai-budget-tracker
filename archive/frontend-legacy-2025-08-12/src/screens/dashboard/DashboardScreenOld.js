/**
 * Modern, Clean Dashboard with Professional UI/UX
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/api';

const DashboardScreen = () => {
  const { user, logout } = useAuth();
  const [showExpenseForm, setShowExpenseForm] = useState(false);
  const [expenses, setExpenses] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadExpenses();
  }, []);

  const loadExpenses = async () => {
    try {
      setIsLoading(true);
      const data = await apiService.get('/api/expenses');
      setExpenses(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to load expenses:', error);
      setExpenses([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddExpense = async (expenseData) => {
    try {
      const newExpense = await apiService.post('/api/expenses', expenseData);
      setExpenses(prev => [newExpense, ...prev]);
      setShowExpenseForm(false);
    } catch (error) {
      console.error('Failed to add expense:', error);
    }
  };

  const filteredExpenses = expenses.filter(expense =>
    expense.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    expense.category?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const stats = {
    totalExpenses: expenses.length,
    totalAmount: expenses.reduce((sum, exp) => sum + parseFloat(exp.amount || 0), 0),
    thisMonth: expenses.filter(exp => {
      const expDate = new Date(exp.expense_date || exp.created_at);
      const now = new Date();
      return expDate.getMonth() === now.getMonth() && expDate.getFullYear() === now.getFullYear();
    }).reduce((sum, exp) => sum + parseFloat(exp.amount || 0), 0)
  };

  return (
    <div style={styles.container}>
      {/* Dev Mode Indicator */}
      {process.env.NODE_ENV === 'development' && (
        <div style={styles.devIndicator}>
          🚧 DEV MODE
        </div>
      )}

      {/* Header */}
      <header style={styles.header}>
        <div>
          <h1 style={styles.title}>Budget Tracker</h1>
          <p style={styles.subtitle}>Welcome back, {user?.email?.split('@')[0] || 'User'}</p>
        </div>
        <button onClick={logout} style={styles.logoutBtn}>
          Sign Out
        </button>
      </header>

      {/* Stats Cards */}
      <div style={styles.statsGrid}>
        <div style={styles.statCard}>
          <div style={styles.statValue}>{stats.totalExpenses}</div>
          <div style={styles.statLabel}>Total Expenses</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statValue}>${stats.totalAmount.toFixed(2)}</div>
          <div style={styles.statLabel}>Total Spent</div>
        </div>
        <div style={styles.statCard}>
          <div style={styles.statValue}>${stats.thisMonth.toFixed(2)}</div>
          <div style={styles.statLabel}>This Month</div>
        </div>
      </div>

      {/* Action Bar */}
      <div style={styles.actionBar}>
        <input
          type="text"
          placeholder="Search expenses..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={styles.searchInput}
        />
        <button
          onClick={() => setShowExpenseForm(!showExpenseForm)}
          style={styles.addBtn}
        >
          {showExpenseForm ? 'Cancel' : '+ Add Expense'}
        </button>
      </div>

      {/* Main Content */}
      <div style={styles.content}>
        {/* Expense Form */}
        {showExpenseForm && (
          <div style={styles.formCard}>
            <ExpenseForm onSubmit={handleAddExpense} onCancel={() => setShowExpenseForm(false)} />
          </div>
        )}

        {/* Expense List */}
        <div style={styles.listCard}>
          <h2 style={styles.cardTitle}>Recent Expenses</h2>
          {isLoading ? (
            <div style={styles.loading}>Loading...</div>
          ) : filteredExpenses.length === 0 ? (
            <div style={styles.empty}>
              {searchTerm ? 'No expenses match your search' : 'No expenses yet. Add your first expense!'}
            </div>
          ) : (
            <div style={styles.expenseList}>
              {filteredExpenses.map(expense => (
                <div key={expense.id} style={styles.expenseItem}>
                  <div style={styles.expenseMain}>
                    <div style={styles.expenseDesc}>{expense.description}</div>
                    <div style={styles.expenseMeta}>
                      <span style={styles.expenseCategory}>{expense.category}</span>
                      <span style={styles.expenseDate}>
                        {new Date(expense.expense_date || expense.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <div style={styles.expenseAmount}>
                    ${parseFloat(expense.amount || 0).toFixed(2)}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Simple Expense Form Component
const ExpenseForm = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    description: '',
    amount: '',
    category: '',
    expense_date: new Date().toISOString().split('T')[0]
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.description || !formData.amount) return;
    onSubmit(formData);
    setFormData({ description: '', amount: '', category: '', expense_date: new Date().toISOString().split('T')[0] });
  };

  return (
    <form onSubmit={handleSubmit} style={styles.form}>
      <h3 style={styles.formTitle}>Add New Expense</h3>
      
      <input
        type="text"
        placeholder="Description (e.g., Coffee at Starbucks)"
        value={formData.description}
        onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
        style={styles.input}
        required
      />
      
      <input
        type="number"
        step="0.01"
        placeholder="Amount"
        value={formData.amount}
        onChange={(e) => setFormData(prev => ({ ...prev, amount: e.target.value }))}
        style={styles.input}
        required
      />
      
      <input
        type="text"
        placeholder="Category (optional)"
        value={formData.category}
        onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value }))}
        style={styles.input}
      />
      
      <input
        type="date"
        value={formData.expense_date}
        onChange={(e) => setFormData(prev => ({ ...prev, expense_date: e.target.value }))}
        style={styles.input}
      />
      
      <div style={styles.formActions}>
        <button type="button" onClick={onCancel} style={styles.cancelBtn}>
          Cancel
        </button>
        <button type="submit" style={styles.submitBtn}>
          Add Expense
        </button>
      </div>
    </form>
  );
};

// Clean, Modern Styles
const styles = {
  container: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '2rem',
    backgroundColor: '#f8fafc',
    minHeight: '100vh',
    fontFamily: "'Inter', system-ui, sans-serif"
  },
  
  devIndicator: {
    position: 'fixed',
    top: '1rem',
    right: '1rem',
    backgroundColor: '#fbbf24',
    color: '#92400e',
    padding: '0.5rem 1rem',
    borderRadius: '0.5rem',
    fontSize: '0.75rem',
    fontWeight: '600',
    zIndex: 1000
  },
  
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '2rem',
    padding: '1.5rem',
    backgroundColor: 'white',
    borderRadius: '1rem',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
  },
  
  title: {
    fontSize: '2rem',
    fontWeight: '700',
    color: '#1f2937',
    margin: '0 0 0.25rem 0'
  },
  
  subtitle: {
    fontSize: '1rem',
    color: '#6b7280',
    margin: 0
  },
  
  logoutBtn: {
    padding: '0.5rem 1rem',
    backgroundColor: '#f3f4f6',
    border: '1px solid #d1d5db',
    borderRadius: '0.5rem',
    color: '#374151',
    cursor: 'pointer',
    fontSize: '0.875rem',
    fontWeight: '500'
  },
  
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '1rem',
    marginBottom: '2rem'
  },
  
  statCard: {
    backgroundColor: 'white',
    padding: '1.5rem',
    borderRadius: '1rem',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
    textAlign: 'center'
  },
  
  statValue: {
    fontSize: '2rem',
    fontWeight: '700',
    color: '#1f2937',
    marginBottom: '0.25rem'
  },
  
  statLabel: {
    fontSize: '0.875rem',
    color: '#6b7280',
    fontWeight: '500'
  },
  
  actionBar: {
    display: 'flex',
    gap: '1rem',
    marginBottom: '2rem',
    alignItems: 'center'
  },
  
  searchInput: {
    flex: 1,
    padding: '0.75rem',
    border: '1px solid #d1d5db',
    borderRadius: '0.5rem',
    fontSize: '1rem',
    backgroundColor: 'white'
  },
  
  addBtn: {
    padding: '0.75rem 1.5rem',
    backgroundColor: '#3b82f6',
    color: 'white',
    border: 'none',
    borderRadius: '0.5rem',
    fontSize: '1rem',
    fontWeight: '600',
    cursor: 'pointer'
  },
  
  content: {
    display: 'grid',
    gap: '2rem'
  },
  
  formCard: {
    backgroundColor: 'white',
    padding: '2rem',
    borderRadius: '1rem',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
  },
  
  listCard: {
    backgroundColor: 'white',
    padding: '2rem',
    borderRadius: '1rem',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
  },
  
  cardTitle: {
    fontSize: '1.25rem',
    fontWeight: '600',
    color: '#1f2937',
    margin: '0 0 1.5rem 0'
  },
  
  loading: {
    textAlign: 'center',
    color: '#6b7280',
    padding: '2rem'
  },
  
  empty: {
    textAlign: 'center',
    color: '#6b7280',
    padding: '2rem',
    fontStyle: 'italic'
  },
  
  expenseList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '0.75rem'
  },
  
  expenseItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '1rem',
    backgroundColor: '#f9fafb',
    borderRadius: '0.5rem',
    border: '1px solid #e5e7eb'
  },
  
  expenseMain: {
    flex: 1
  },
  
  expenseDesc: {
    fontSize: '1rem',
    fontWeight: '500',
    color: '#1f2937',
    marginBottom: '0.25rem'
  },
  
  expenseMeta: {
    display: 'flex',
    gap: '1rem',
    fontSize: '0.875rem',
    color: '#6b7280'
  },
  
  expenseCategory: {
    backgroundColor: '#dbeafe',
    color: '#1e40af',
    padding: '0.125rem 0.5rem',
    borderRadius: '0.25rem',
    fontSize: '0.75rem'
  },
  
  expenseDate: {},
  
  expenseAmount: {
    fontSize: '1.125rem',
    fontWeight: '600',
    color: '#1f2937'
  },
  
  form: {
    display: 'flex',
    flexDirection: 'column',
    gap: '1rem'
  },
  
  formTitle: {
    fontSize: '1.25rem',
    fontWeight: '600',
    color: '#1f2937',
    margin: '0 0 1rem 0'
  },
  
  input: {
    padding: '0.75rem',
    border: '1px solid #d1d5db',
    borderRadius: '0.5rem',
    fontSize: '1rem'
  },
  
  formActions: {
    display: 'flex',
    gap: '1rem',
    justifyContent: 'flex-end'
  },
  
  cancelBtn: {
    padding: '0.75rem 1.5rem',
    backgroundColor: '#f3f4f6',
    border: '1px solid #d1d5db',
    borderRadius: '0.5rem',
    color: '#374151',
    cursor: 'pointer',
    fontSize: '1rem'
  },
  
  submitBtn: {
    padding: '0.75rem 1.5rem',
    backgroundColor: '#3b82f6',
    color: 'white',
    border: 'none',
    borderRadius: '0.5rem',
    fontSize: '1rem',
    fontWeight: '600',
    cursor: 'pointer'
  }
};

export default DashboardScreen;
