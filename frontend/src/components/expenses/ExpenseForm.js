/**
 * ExpenseForm Component - Create and edit expenses
 * Phase 2: Core App Features - Expense Management
 */

import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/api';

const ExpenseForm = ({ onExpenseCreated, onCancel, editingExpense = null }) => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const [formData, setFormData] = useState({
    description: editingExpense?.description || '',
    amount: editingExpense?.amount || '',
    category: editingExpense?.category || '',
    notes: editingExpense?.notes || '',
    expense_date: editingExpense?.expense_date || new Date().toISOString().split('T')[0]
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Validate form
      if (!formData.description.trim()) {
        throw new Error('Description is required');
      }
      if (!formData.amount || parseFloat(formData.amount) <= 0) {
        throw new Error('Please enter a valid amount');
      }

      const expenseData = {
        description: formData.description.trim(),
        amount: parseFloat(formData.amount),
        category: formData.category.trim() || null, // Let AI categorize if empty
        notes: formData.notes.trim(),
        expense_date: formData.expense_date
      };

      const response = await apiService.post('/api/expenses', expenseData);
      
      if (response.success !== false) {
        // Reset form
        setFormData({
          description: '',
          amount: '',
          category: '',
          notes: '',
          expense_date: new Date().toISOString().split('T')[0]
        });
        
        if (onExpenseCreated) {
          onExpenseCreated(response);
        }
      } else {
        setError(response.message || 'Failed to create expense');
      }
    } catch (error) {
      console.error('Error creating expense:', error);
      setError(error.message || 'Failed to create expense');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const formStyle = {
    backgroundColor: 'var(--gray-50)',
    borderRadius: 'var(--border-radius-lg)',
    padding: 'var(--spacing-lg)',
    border: '1px solid var(--gray-200)',
    maxWidth: '500px',
    margin: '0 auto'
  };

  const titleStyle = {
    fontSize: '1.5rem',
    fontWeight: '600',
    color: 'var(--primary-900)',
    marginBottom: 'var(--spacing-lg)',
    textAlign: 'center'
  };

  const inputGroupStyle = {
    marginBottom: 'var(--spacing-md)'
  };

  const labelStyle = {
    display: 'block',
    fontSize: '0.875rem',
    fontWeight: '500',
    color: 'var(--primary-700)',
    marginBottom: 'var(--spacing-xs)'
  };

  const inputStyle = {
    width: '100%',
    padding: 'var(--spacing-sm) var(--spacing-md)',
    border: '1px solid var(--gray-200)',
    borderRadius: 'var(--border-radius-md)',
    fontSize: '1rem',
    backgroundColor: 'white',
    transition: 'border-color 0.2s ease',
    outline: 'none'
  };

  const inputFocusStyle = {
    borderColor: 'var(--accent-500)',
    boxShadow: '0 0 0 3px rgba(59, 130, 246, 0.1)'
  };

  const textareaStyle = {
    ...inputStyle,
    minHeight: '80px',
    resize: 'vertical'
  };

  const buttonGroupStyle = {
    display: 'flex',
    gap: 'var(--spacing-md)',
    marginTop: 'var(--spacing-lg)'
  };

  const primaryButtonStyle = {
    flex: 1,
    padding: 'var(--spacing-md) var(--spacing-lg)',
    backgroundColor: loading ? 'var(--gray-400)' : 'var(--accent-600)',
    color: 'white',
    border: 'none',
    borderRadius: 'var(--border-radius-md)',
    fontSize: '1rem',
    fontWeight: '500',
    cursor: loading ? 'not-allowed' : 'pointer',
    transition: 'all 0.2s ease',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  };

  const secondaryButtonStyle = {
    flex: 1,
    padding: 'var(--spacing-md) var(--spacing-lg)',
    backgroundColor: 'white',
    color: 'var(--primary-700)',
    border: '1px solid var(--gray-200)',
    borderRadius: 'var(--border-radius-md)',
    fontSize: '1rem',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s ease'
  };

  const errorStyle = {
    backgroundColor: '#fef2f2',
    color: '#dc2626',
    padding: 'var(--spacing-md)',
    borderRadius: 'var(--border-radius-md)',
    fontSize: '0.875rem',
    marginBottom: 'var(--spacing-md)',
    border: '1px solid #fecaca'
  };

  return (
    <form onSubmit={handleSubmit} style={formStyle}>
      <h2 style={titleStyle}>
        {editingExpense ? 'Edit Expense' : 'Add New Expense'}
      </h2>

      {error && (
        <div style={errorStyle}>
          {error}
        </div>
      )}

      <div style={inputGroupStyle}>
        <label style={labelStyle} htmlFor="description">
          Description *
        </label>
        <input
          id="description"
          name="description"
          type="text"
          placeholder="e.g., Coffee at Starbucks"
          value={formData.description}
          onChange={handleChange}
          style={inputStyle}
          required
        />
      </div>

      <div style={inputGroupStyle}>
        <label style={labelStyle} htmlFor="amount">
          Amount ($) *
        </label>
        <input
          id="amount"
          name="amount"
          type="number"
          step="0.01"
          min="0"
          placeholder="0.00"
          value={formData.amount}
          onChange={handleChange}
          style={inputStyle}
          required
        />
      </div>

      <div style={inputGroupStyle}>
        <label style={labelStyle} htmlFor="category">
          Category
        </label>
        <input
          id="category"
          name="category"
          type="text"
          placeholder="Leave blank for AI categorization"
          value={formData.category}
          onChange={handleChange}
          style={inputStyle}
        />
      </div>

      <div style={inputGroupStyle}>
        <label style={labelStyle} htmlFor="expense_date">
          Date
        </label>
        <input
          id="expense_date"
          name="expense_date"
          type="date"
          value={formData.expense_date}
          onChange={handleChange}
          style={inputStyle}
        />
      </div>

      <div style={inputGroupStyle}>
        <label style={labelStyle} htmlFor="notes">
          Notes
        </label>
        <textarea
          id="notes"
          name="notes"
          placeholder="Optional notes about this expense"
          value={formData.notes}
          onChange={handleChange}
          style={textareaStyle}
        />
      </div>

      <div style={buttonGroupStyle}>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            style={secondaryButtonStyle}
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={loading}
          style={primaryButtonStyle}
        >
          {loading ? 'Saving...' : (editingExpense ? 'Update Expense' : 'Add Expense')}
        </button>
      </div>
    </form>
  );
};

export default ExpenseForm;
