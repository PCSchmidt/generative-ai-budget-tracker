/**
 * AI Budget Tracker - Dashboard Screen (React Web)
 * Clean, modern dashboard with expense management
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import apiService from '../../services/api';

export default function DashboardScreen() {
  const { user, logout } = useAuth();
  const [expenses, setExpenses] = useState([]);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddExpense, setShowAddExpense] = useState(false);
  const [addingExpense, setAddingExpense] = useState(false);
  
  // Edit/Delete state
  const [editingExpense, setEditingExpense] = useState(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [deletingExpense, setDeletingExpense] = useState(null);

  // Debug: Log auth state
  console.log('DashboardScreen - user:', user);
  console.log('DashboardScreen - localStorage tokens:', {
    accessToken: localStorage.getItem('accessToken'),
    refreshToken: localStorage.getItem('refreshToken'),
    user: localStorage.getItem('user')
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load dashboard data
      const [expensesData, insightsData] = await Promise.all([
        apiService.getExpenses().catch(() => ({ expenses: [] })),
        apiService.getInsights().catch(() => ({ insights: null }))
      ]);

      setExpenses(expensesData.expenses || []);
      setInsights(insightsData.insights);
      
    } catch (error) {
      console.error('Dashboard load error:', error);
      setError('Unable to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount) => {
    return `$${Number(amount || 0).toFixed(2)}`;
  };

  const handleLogout = () => {
    logout();
  };

  const handleAddExpense = async (expenseData) => {
    try {
      setAddingExpense(true);
      console.log('Adding expense:', expenseData);
      
      const response = await apiService.createExpense(expenseData);
      console.log('Expense created:', response);
      
      // Reload dashboard data
      await loadDashboardData();
      setShowAddExpense(false);
    } catch (error) {
      console.error('Error adding expense:', error);
      setError('Failed to add expense: ' + error.message);
    } finally {
      setAddingExpense(false);
    }
  };

  // Handle editing an expense
  const handleEditExpense = (expense) => {
    setEditingExpense(expense);
    setShowEditModal(true);
  };

  // Handle updating an expense
  const handleUpdateExpense = async (expenseData) => {
    try {
      setAddingExpense(true);
      console.log('Updating expense:', editingExpense.id, expenseData);
      
      const response = await apiService.updateExpense(editingExpense.id, expenseData);
      console.log('Expense updated:', response);
      
      // Reload dashboard data
      await loadDashboardData();
      setShowEditModal(false);
      setEditingExpense(null);
    } catch (error) {
      console.error('Error updating expense:', error);
      setError('Failed to update expense: ' + error.message);
    } finally {
      setAddingExpense(false);
    }
  };

  // Handle deleting an expense
  const handleDeleteExpense = async (expenseId) => {
    if (!window.confirm('Are you sure you want to delete this expense?')) {
      return;
    }

    try {
      setDeletingExpense(expenseId);
      console.log('Deleting expense:', expenseId);
      
      await apiService.deleteExpense(expenseId);
      console.log('Expense deleted');
      
      // Reload dashboard data
      await loadDashboardData();
    } catch (error) {
      console.error('Error deleting expense:', error);
      setError('Failed to delete expense: ' + error.message);
    } finally {
      setDeletingExpense(null);
    }
  };

  // Helper function to get category icons
  const getCategoryIcon = (category) => {
    const icons = {
      'Food & Dining': '🍽️',
      'Transportation': '🚗',
      'Entertainment': '🎬',
      'Utilities': '💡',
      'Housing': '🏠',
      'Healthcare': '🏥',
      'Shopping': '🛍️',
      'Other': '💳'
    };
    return icons[category] || '💳';
  };

  // Helper function to format date
  const formatDate = (dateString) => {
    if (!dateString) return '';
    try {
      const date = new Date(dateString);
      const today = new Date();
      const yesterday = new Date(today);
      yesterday.setDate(yesterday.getDate() - 1);
      
      if (date.toDateString() === today.toDateString()) {
        return 'Today';
      } else if (date.toDateString() === yesterday.toDateString()) {
        return 'Yesterday';
      } else {
        return date.toLocaleDateString('en-US', { 
          month: 'short', 
          day: 'numeric',
          year: date.getFullYear() !== today.getFullYear() ? 'numeric' : undefined
        });
      }
    } catch (error) {
      return dateString.split('T')[0]; // Fallback to raw date
    }
  };

  if (loading) {
    return (
      <div style={styles.loadingContainer}>
        <div style={styles.spinner}></div>
        <p style={styles.loadingText}>Loading your dashboard...</p>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <div>
            <h1 style={styles.title}>💰 AI Budget Tracker</h1>
            <p style={styles.subtitle}>Welcome back, {user?.username || 'User'}!</p>
          </div>
          <button style={styles.logoutButton} onClick={handleLogout}>
            Logout
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main style={styles.main}>
        {/* Summary Cards */}
        <section style={styles.summarySection}>
          <div style={styles.summaryCard}>
            <h3 style={styles.cardTitle}>Total Expenses</h3>
            <p style={styles.cardAmount}>
              {formatCurrency(expenses.reduce((sum, exp) => sum + (exp.amount || 0), 0))}
            </p>
            <p style={styles.cardSubtext}>{expenses.length} transactions</p>
          </div>

          <div style={styles.summaryCard}>
            <h3 style={styles.cardTitle}>This Month</h3>
            <p style={styles.cardAmount}>
              {formatCurrency(expenses.reduce((sum, exp) => sum + (exp.amount || 0), 0))}
            </p>
            <p style={styles.cardSubtext}>Current month</p>
          </div>

          <div style={styles.summaryCard}>
            <h3 style={styles.cardTitle}>AI Insights</h3>
            <p style={styles.cardAmount}>
              {insights?.top_category || 'Analyzing...'}
            </p>
            <p style={styles.cardSubtext}>Top category</p>
          </div>
        </section>

        {/* Quick Actions */}
        <section style={styles.actionsSection}>
          <h2 style={styles.sectionTitle}>Quick Actions</h2>
          <div style={styles.actionsGrid}>
            <button 
              style={styles.actionButton}
              onClick={() => setShowAddExpense(true)}
            >
              <span style={styles.actionIcon}>➕</span>
              Add Expense
            </button>
            <button style={styles.actionButton}>
              <span style={styles.actionIcon}>📊</span>
              View Reports
            </button>
            <button style={styles.actionButton}>
              <span style={styles.actionIcon}>🤖</span>
              AI Insights
            </button>
            <button style={styles.actionButton}>
              <span style={styles.actionIcon}>⚙️</span>
              Settings
            </button>
          </div>
        </section>

        {/* Recent Expenses */}
        <section style={styles.expensesSection}>
          <h2 style={styles.sectionTitle}>Recent Expenses</h2>
          {error && (
            <div style={styles.errorContainer}>
              <p style={styles.errorText}>{error}</p>
              <button style={styles.retryButton} onClick={loadDashboardData}>
                Retry
              </button>
            </div>
          )}
          
          {expenses.length === 0 ? (
            <div style={styles.emptyState}>
              <p style={styles.emptyStateText}>No expenses yet</p>
              <p style={styles.emptyStateSubtext}>
                Add your first expense to get started!
              </p>
              <button 
                style={styles.addExpenseButton}
                onClick={() => setShowAddExpense(true)}
              >
                Add First Expense
              </button>
            </div>
          ) : (
            <div style={styles.expensesList}>
              {expenses.slice(0, 10).map((expense, index) => (
                <div key={expense.id || index} style={styles.expenseItem}>
                  <div style={styles.expenseLeft}>
                    <div style={styles.expenseIcon}>
                      {getCategoryIcon(expense.category)}
                    </div>
                    <div style={styles.expenseInfo}>
                      <h4 style={styles.expenseDescription}>
                        {expense.description || 'Unnamed expense'}
                      </h4>
                      <div style={styles.expenseMeta}>
                        <span style={styles.expenseCategory}>
                          {expense.category || 'Uncategorized'}
                        </span>
                        <span style={styles.expenseDate}>
                          {formatDate(expense.expense_date || expense.created_at)}
                        </span>
                      </div>
                      {expense.notes && (
                        <p style={styles.expenseNotes}>{expense.notes}</p>
                      )}
                    </div>
                  </div>
                  <div style={styles.expenseRight}>
                    <p style={styles.expenseAmount}>
                      {formatCurrency(expense.amount)}
                    </p>
                    <div style={styles.expenseActions}>
                      <button
                        style={styles.editButton}
                        onClick={() => handleEditExpense(expense)}
                        title="Edit expense"
                        disabled={addingExpense}
                      >
                        ✏️
                      </button>
                      <button
                        style={{
                          ...styles.deleteButton,
                          opacity: deletingExpense === expense.id ? 0.5 : 1
                        }}
                        onClick={() => handleDeleteExpense(expense.id)}
                        title="Delete expense"
                        disabled={deletingExpense === expense.id || addingExpense}
                      >
                        {deletingExpense === expense.id ? '⏳' : '🗑️'}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* AI Insights */}
        {insights && (
          <section style={styles.insightsSection}>
            <h2 style={styles.sectionTitle}>🤖 AI Insights</h2>
            <div style={styles.insightCard}>
              <p style={styles.insightText}>{insights.advice}</p>
              {insights.tips && insights.tips.length > 0 && (
                <ul style={styles.tipsList}>
                  {insights.tips.map((tip, index) => (
                    <li key={index} style={styles.tipItem}>{tip}</li>
                  ))}
                </ul>
              )}
            </div>
          </section>
        )}
      </main>

      {/* Add Expense Modal */}
      {showAddExpense && (
        <ExpenseFormModal
          onSubmit={handleAddExpense}
          onCancel={() => setShowAddExpense(false)}
          loading={addingExpense}
        />
      )}

      {/* Edit Expense Modal */}
      {editingExpense && (
        <ExpenseFormModal
          onSubmit={handleUpdateExpense}
          onCancel={() => setEditingExpense(null)}
          loading={addingExpense}
          initialData={editingExpense}
          title="Edit Expense"
        />
      )}
    </div>
  );
}

// Simple Expense Form Modal Component
function ExpenseFormModal({ onSubmit, onCancel, loading, initialData = null, title = "Add New Expense" }) {
  const [formData, setFormData] = useState(() => {
    if (initialData) {
      return {
        description: initialData.description || '',
        amount: initialData.amount ? initialData.amount.toString() : '',
        category: initialData.category || '',
        notes: initialData.notes || '',
        expense_date: initialData.expense_date ? 
          new Date(initialData.expense_date).toISOString().split('T')[0] : 
          new Date().toISOString().split('T')[0]
      };
    }
    return {
      description: '',
      amount: '',
      category: '',
      notes: '',
      expense_date: new Date().toISOString().split('T')[0]
    };
  });

  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');

    // Validate
    if (!formData.description.trim()) {
      setError('Description is required');
      return;
    }
    if (!formData.amount || parseFloat(formData.amount) <= 0) {
      setError('Please enter a valid amount');
      return;
    }

    onSubmit({
      description: formData.description.trim(),
      amount: parseFloat(formData.amount),
      category: formData.category.trim() || 'Other',
      notes: formData.notes.trim(),
      expense_date: formData.expense_date
    });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (error) setError('');
  };

  return (
    <div style={modalStyles.overlay}>
      <div style={modalStyles.modal}>
        <h2 style={modalStyles.title}>{title}</h2>
        
        <form onSubmit={handleSubmit}>
          <div style={modalStyles.formGroup}>
            <label style={modalStyles.label}>Description *</label>
            <input
              type="text"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Coffee, Lunch, Gas, etc."
              style={modalStyles.input}
              required
            />
          </div>

          <div style={modalStyles.formGroup}>
            <label style={modalStyles.label}>Amount *</label>
            <input
              type="number"
              name="amount"
              value={formData.amount}
              onChange={handleChange}
              placeholder="0.00"
              step="0.01"
              min="0"
              style={modalStyles.input}
              required
            />
          </div>

          <div style={modalStyles.formGroup}>
            <label style={modalStyles.label}>Category</label>
            <select
              name="category"
              value={formData.category}
              onChange={handleChange}
              style={modalStyles.input}
            >
              <option value="">Select Category (or leave for AI)</option>
              <option value="Food & Dining">Food & Dining</option>
              <option value="Transportation">Transportation</option>
              <option value="Entertainment">Entertainment</option>
              <option value="Shopping">Shopping</option>
              <option value="Utilities">Utilities</option>
              <option value="Healthcare">Healthcare</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div style={modalStyles.formGroup}>
            <label style={modalStyles.label}>Date</label>
            <input
              type="date"
              name="expense_date"
              value={formData.expense_date}
              onChange={handleChange}
              style={modalStyles.input}
            />
          </div>

          <div style={modalStyles.formGroup}>
            <label style={modalStyles.label}>Notes</label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              placeholder="Optional notes..."
              style={modalStyles.textarea}
              rows="3"
            />
          </div>

          {error && (
            <div style={modalStyles.error}>{error}</div>
          )}

          <div style={modalStyles.buttons}>
            <button
              type="button"
              onClick={onCancel}
              style={modalStyles.cancelButton}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              style={modalStyles.submitButton}
              disabled={loading}
            >
              {loading ? 'Adding...' : 'Add Expense'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

const modalStyles = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
  },
  modal: {
    backgroundColor: 'white',
    borderRadius: '12px',
    padding: '24px',
    width: '90%',
    maxWidth: '500px',
    maxHeight: '90vh',
    overflow: 'auto',
    boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
  },
  title: {
    margin: '0 0 20px 0',
    fontSize: '24px',
    fontWeight: '600',
    color: '#0f172a',
  },
  formGroup: {
    marginBottom: '16px',
  },
  label: {
    display: 'block',
    marginBottom: '4px',
    fontSize: '14px',
    fontWeight: '500',
    color: '#374151',
  },
  input: {
    width: '100%',
    padding: '8px 12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    boxSizing: 'border-box',
  },
  textarea: {
    width: '100%',
    padding: '8px 12px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    fontSize: '14px',
    resize: 'vertical',
    boxSizing: 'border-box',
  },
  error: {
    backgroundColor: '#fef2f2',
    border: '1px solid #fca5a5',
    color: '#dc2626',
    padding: '8px 12px',
    borderRadius: '6px',
    marginBottom: '16px',
    fontSize: '14px',
  },
  buttons: {
    display: 'flex',
    gap: '12px',
    justifyContent: 'flex-end',
  },
  cancelButton: {
    padding: '8px 16px',
    border: '1px solid #d1d5db',
    borderRadius: '6px',
    backgroundColor: 'white',
    color: '#374151',
    cursor: 'pointer',
    fontSize: '14px',
  },
  submitButton: {
    padding: '8px 16px',
    border: 'none',
    borderRadius: '6px',
    backgroundColor: '#2563eb',
    color: 'white',
    cursor: 'pointer',
    fontSize: '14px',
  },
};

const styles = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#f8fafc',
  },
  
  loadingContainer: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: '100vh',
    backgroundColor: '#f8fafc',
  },
  
  spinner: {
    width: '40px',
    height: '40px',
    border: '4px solid #e2e8f0',
    borderTop: '4px solid #3b82f6',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
  
  loadingText: {
    marginTop: '16px',
    fontSize: '16px',
    color: '#64748b',
  },

  header: {
    backgroundColor: 'white',
    borderBottom: '1px solid #e2e8f0',
    padding: '24px',
  },

  headerContent: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    maxWidth: '1200px',
    margin: '0 auto',
  },

  title: {
    fontSize: '32px',
    fontWeight: 'bold',
    color: '#1e293b',
    margin: '0 0 8px 0',
  },

  subtitle: {
    fontSize: '16px',
    color: '#64748b',
    margin: '0',
  },

  logoutButton: {
    backgroundColor: '#ef4444',
    color: 'white',
    border: 'none',
    padding: '8px 16px',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },

  main: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '24px',
  },

  summarySection: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
    gap: '24px',
    marginBottom: '32px',
  },

  summaryCard: {
    backgroundColor: 'white',
    padding: '24px',
    borderRadius: '12px',
    boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
    border: '1px solid #e2e8f0',
  },

  cardTitle: {
    fontSize: '14px',
    fontWeight: '500',
    color: '#64748b',
    margin: '0 0 8px 0',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },

  cardAmount: {
    fontSize: '28px',
    fontWeight: 'bold',
    color: '#1e293b',
    margin: '0 0 4px 0',
  },

  cardSubtext: {
    fontSize: '12px',
    color: '#94a3b8',
    margin: '0',
  },

  actionsSection: {
    marginBottom: '32px',
  },

  sectionTitle: {
    fontSize: '20px',
    fontWeight: 'bold',
    color: '#1e293b',
    margin: '0 0 16px 0',
  },

  actionsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '16px',
  },

  actionButton: {
    backgroundColor: 'white',
    border: '1px solid #e2e8f0',
    borderRadius: '12px',
    padding: '20px',
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    fontSize: '16px',
    fontWeight: '500',
    color: '#1e293b',
    cursor: 'pointer',
    transition: 'all 0.2s',
    textAlign: 'left',
  },

  actionIcon: {
    fontSize: '20px',
  },

  expensesSection: {
    marginBottom: '32px',
  },

  errorContainer: {
    backgroundColor: '#fef2f2',
    border: '1px solid #fecaca',
    borderRadius: '8px',
    padding: '16px',
    marginBottom: '16px',
  },

  errorText: {
    color: '#dc2626',
    margin: '0 0 8px 0',
  },

  retryButton: {
    backgroundColor: '#dc2626',
    color: 'white',
    border: 'none',
    padding: '8px 16px',
    borderRadius: '6px',
    fontSize: '14px',
    cursor: 'pointer',
  },

  emptyState: {
    backgroundColor: 'white',
    border: '1px solid #e2e8f0',
    borderRadius: '12px',
    padding: '48px',
    textAlign: 'center',
  },

  emptyStateText: {
    fontSize: '18px',
    color: '#64748b',
    margin: '0 0 8px 0',
  },

  emptyStateSubtext: {
    fontSize: '14px',
    color: '#94a3b8',
    margin: '0 0 24px 0',
  },

  addExpenseButton: {
    backgroundColor: '#3b82f6',
    color: 'white',
    border: 'none',
    padding: '12px 24px',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: '500',
    cursor: 'pointer',
  },

  expensesList: {
    backgroundColor: 'white',
    border: '1px solid #e2e8f0',
    borderRadius: '12px',
    overflow: 'hidden',
  },

  expenseItem: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    padding: '16px 20px',
    borderBottom: '1px solid #f1f5f9',
    transition: 'background-color 0.2s ease',
  },

  expenseLeft: {
    display: 'flex',
    alignItems: 'flex-start',
    flex: 1,
    gap: '12px',
  },

  expenseIcon: {
    fontSize: '24px',
    marginTop: '2px',
  },

  expenseInfo: {
    flex: 1,
  },

  expenseDescription: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#1e293b',
    margin: '0 0 6px 0',
    lineHeight: '1.4',
  },

  expenseMeta: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '4px',
  },

  expenseCategory: {
    fontSize: '13px',
    fontWeight: '500',
    color: '#6366f1',
    backgroundColor: '#ede9fe',
    padding: '2px 8px',
    borderRadius: '12px',
    textTransform: 'capitalize',
  },

  expenseDate: {
    fontSize: '13px',
    color: '#64748b',
    fontWeight: '500',
  },

  expenseNotes: {
    fontSize: '14px',
    color: '#64748b',
    margin: '6px 0 0 0',
    fontStyle: 'italic',
    lineHeight: '1.4',
  },

  expenseRight: {
    textAlign: 'right',
    marginLeft: '16px',
  },

  expenseAmount: {
    fontSize: '18px',
    fontWeight: '700',
    color: '#ef4444',
    margin: '0',
  },

  insightsSection: {
    marginBottom: '32px',
  },

  insightCard: {
    backgroundColor: '#eff6ff',
    border: '1px solid #bfdbfe',
    borderLeft: '4px solid #3b82f6',
    borderRadius: '8px',
    padding: '20px',
  },

  insightText: {
    fontSize: '16px',
    color: '#1e293b',
    margin: '0 0 12px 0',
    lineHeight: '1.5',
  },

  tipsList: {
    margin: '0',
    paddingLeft: '20px',
  },

  tipItem: {
    fontSize: '14px',
    color: '#64748b',
    marginBottom: '4px',
  },

  expenseActions: {
    display: 'flex',
    gap: '8px',
    marginTop: '8px',
    alignItems: 'center',
  },

  editButton: {
    backgroundColor: 'transparent',
    border: '1px solid #e2e8f0',
    borderRadius: '6px',
    padding: '6px 8px',
    fontSize: '14px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    color: '#64748b',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: '32px',
    height: '32px',
  },

  deleteButton: {
    backgroundColor: 'transparent',
    border: '1px solid #fecaca',
    borderRadius: '6px',
    padding: '6px 8px',
    fontSize: '14px',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    color: '#dc2626',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: '32px',
    height: '32px',
  },
};

// Add CSS keyframes for spinner animation
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  
  .action-button:hover {
    background-color: #f8fafc !important;
    border-color: #cbd5e1 !important;
  }
`;
document.head.appendChild(styleSheet);
