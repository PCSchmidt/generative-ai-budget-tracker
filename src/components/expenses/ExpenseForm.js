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

  // NEW: AI suggestion state
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState('');
  const [aiSuggestion, setAiSuggestion] = useState(null); // { category, confidence, method, reasoning }

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

      // Use AI-assisted creation to auto-categorize when category is empty
      const response = await apiService.createExpenseWithAI(expenseData);
      
      if (response && response.id) {
        // Reset form
        setFormData({
          description: '',
          amount: '',
          category: '',
          notes: '',
          expense_date: new Date().toISOString().split('T')[0]
        });
        setAiSuggestion(null);
        
        if (onExpenseCreated) {
          onExpenseCreated(response);
        }
      } else if (response?.success === false) {
        setError(response.error || response.message || 'Failed to create expense');
      } else {
        // Backward compatibility with previous API
        if (onExpenseCreated) onExpenseCreated(response);
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

  // NEW: Trigger AI suggestion
  const handleAISuggest = async () => {
    setAiError('');
    setAiLoading(true);
    setAiSuggestion(null);
    try {
      const desc = formData.description?.trim();
      const amt = formData.amount ? parseFloat(formData.amount) : null;
      if (!desc || desc.length < 3) {
        setAiError('Enter a description first');
        return;
      }

      // Try protected smart endpoint first (uses auth when available)
      let result;
      try {
        result = await apiService.categorizeExpenseSmart(desc, isNaN(amt) ? null : amt);
      } catch (smartErr) {
        result = { success: false, error: smartErr?.message };
      }

      if (result?.success && result.categorization) {
        const { category, confidence, method, reasoning } = result.categorization;
        setAiSuggestion({ category, confidence, method, reasoning });
      } else {
        // Fallback to public categorization (no auth required)
        const fallback = await apiService.categorizeExpense(desc, isNaN(amt) ? null : amt);
        if (fallback?.success) {
          setAiSuggestion({
            category: fallback.category,
            confidence: fallback.confidence,
            method: fallback.method || 'public_ai',
            reasoning: 'Public AI categorization fallback'
          });
          if (result?.error) setAiError(result.error);
        } else {
          setAiError(result?.error || fallback?.error || 'AI could not provide a suggestion');
        }
      }
    } catch (err) {
      console.warn('AI suggestion failed:', err);
      setAiError(err.message || 'AI suggestion failed');
    } finally {
      setAiLoading(false);
    }
  };

  // NEW: Accept AI suggestion into category field
  const acceptAISuggestion = () => {
    if (aiSuggestion?.category) {
      setFormData(prev => ({ ...prev, category: aiSuggestion.category }));
    }
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

  // NEW: Styles for AI suggestion card
  const aiCardStyle = {
    padding: 'var(--spacing-md)',
    border: '1px solid var(--gray-200)',
    borderRadius: 'var(--border-radius-md)',
    backgroundColor: 'white',
    marginTop: 'var(--spacing-sm)'
  };
  const aiRowStyle = { display: 'flex', alignItems: 'center', justifyContent: 'space-between' };
  const aiBadgeStyle = {
    fontSize: '0.8rem',
    color: '#065f46',
    backgroundColor: '#ecfdf5',
    border: '1px solid #a7f3d0',
    borderRadius: '999px',
    padding: '2px 8px'
  };
  const aiAcceptBtnStyle = {
    padding: '6px 10px',
    backgroundColor: '#2563eb',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer'
  };
  const aiSuggestBtnStyle = {
    marginTop: '6px',
    padding: '8px 10px',
    backgroundColor: '#f3f4f6',
    color: '#111827',
    border: '1px solid #e5e7eb',
    borderRadius: '6px',
    cursor: aiLoading ? 'not-allowed' : 'pointer'
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
        {/* AI Suggestion UI */}
        {aiSuggestion && (
          <div style={aiCardStyle}>
            <div style={aiRowStyle}>
              <div>
                <div style={{ fontWeight: 600, color: '#111827' }}>AI Suggestion: {aiSuggestion.category}</div>
                <div style={{ fontSize: '0.85rem', color: '#4b5563' }}>
                  Confidence: {typeof aiSuggestion.confidence === 'number' ? `${Math.round(aiSuggestion.confidence * 100)}%` : '—'}
                </div>
                <div style={{ marginTop: 4 }}>
                  <span style={aiBadgeStyle}>{aiSuggestion.method || 'ai'}</span>
                </div>
              </div>
              <button type="button" onClick={acceptAISuggestion} style={aiAcceptBtnStyle}>Use</button>
            </div>
            {aiSuggestion.reasoning && (
              <div style={{ marginTop: 6, fontSize: '0.85rem', color: '#374151' }}>
                Why: {aiSuggestion.reasoning}
              </div>
            )}
          </div>
        )}
        {aiError && (
          <div style={{ ...errorStyle, marginTop: '8px' }}>{aiError}</div>
        )}
        <button type="button" onClick={handleAISuggest} style={aiSuggestBtnStyle} disabled={aiLoading}>
          {aiLoading ? 'Getting AI suggestion...' : 'Suggest with AI'}
        </button>
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
