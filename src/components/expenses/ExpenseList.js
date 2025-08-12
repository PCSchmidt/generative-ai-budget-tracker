/**
 * ExpenseList Component - Display and manage expenses
 * Phase 2: Core App Features - Expense Management
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { apiService } from '../../services/api';
import LoadingSpinner from '../ui/LoadingSpinner';

const ExpenseList = ({ refreshTrigger, onEditExpense, searchFilter = '' }) => {
  const { user } = useAuth();
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [sortBy, setSortBy] = useState('date');
  const [sortOrder, setSortOrder] = useState('desc');
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [total, setTotal] = useState(0);

  // Load expenses from API
  const loadExpenses = async () => {
    try {
      setLoading(true);
      setError('');
      
      // Prefer paginated API, fallback to legacy
      const paged = await apiService.get(`/api/expenses/paginated?page=${page}&page_size=${pageSize}`);
      if (paged && Array.isArray(paged.items)) {
        setExpenses(paged.items);
        setTotal(paged.total || paged.items.length);
      } else {
        const legacy = await apiService.get('/api/expenses');
        if (Array.isArray(legacy)) {
          setExpenses(legacy);
          setTotal(legacy.length);
        } else if (legacy && legacy.expenses && Array.isArray(legacy.expenses)) {
          setExpenses(legacy.expenses);
          setTotal(legacy.expenses.length);
        } else {
          console.warn('Unexpected response format:', paged || legacy);
          setExpenses([]);
          setTotal(0);
        }
      }
    } catch (error) {
      console.error('Error loading expenses:', error);
      setError('Failed to load expenses');
      setExpenses([]);
    } finally {
      setLoading(false);
    }
  };

  // Load expenses on mount and when refreshTrigger changes
  useEffect(() => {
    loadExpenses();
  }, [refreshTrigger, page, pageSize]);

  // Filter and sort expenses
  const filteredAndSortedExpenses = expenses
    .filter(expense => {
      if (!searchFilter) return true;
      const searchLower = searchFilter.toLowerCase();
      return (
        expense.description?.toLowerCase().includes(searchLower) ||
        expense.category?.toLowerCase().includes(searchLower) ||
        expense.notes?.toLowerCase().includes(searchLower)
      );
    })
    .sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case 'amount':
          aValue = parseFloat(a.amount) || 0;
          bValue = parseFloat(b.amount) || 0;
          break;
        case 'category':
          aValue = (a.category || '').toLowerCase();
          bValue = (b.category || '').toLowerCase();
          break;
        case 'description':
          aValue = (a.description || '').toLowerCase();
          bValue = (b.description || '').toLowerCase();
          break;
        case 'date':
        default:
          aValue = new Date(a.expense_date || a.created_at);
          bValue = new Date(b.expense_date || b.created_at);
          break;
      }
      
      if (aValue < bValue) return sortOrder === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('desc');
    }
  };

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      });
    } catch {
      return 'Invalid Date';
    }
  };

  const formatAmount = (amount) => {
    const num = parseFloat(amount);
    if (isNaN(num)) return '$0.00';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(num);
  };

  // Styles
  const containerStyle = {
    backgroundColor: 'white',
    borderRadius: 'var(--border-radius-lg)',
    border: '1px solid var(--gray-200)',
    overflow: 'hidden'
  };

  const headerStyle = {
    padding: 'var(--spacing-lg)',
    borderBottom: '1px solid var(--gray-200)',
    backgroundColor: 'var(--gray-50)'
  };

  const titleStyle = {
    fontSize: '1.25rem',
    fontWeight: '600',
    color: 'var(--primary-900)',
    margin: 0
  };

  const sortControlsStyle = {
    display: 'flex',
    gap: 'var(--spacing-md)',
    marginTop: 'var(--spacing-md)',
    alignItems: 'center'
  };

  const sortButtonStyle = {
    padding: 'var(--spacing-xs) var(--spacing-sm)',
    backgroundColor: 'white',
    border: '1px solid var(--gray-200)',
    borderRadius: 'var(--border-radius-sm)',
    fontSize: '0.875rem',
    cursor: 'pointer',
    transition: 'all 0.2s ease'
  };

  const activeSortButtonStyle = {
    ...sortButtonStyle,
    backgroundColor: 'var(--accent-600)',
    color: 'white',
    borderColor: 'var(--accent-600)'
  };

  const listStyle = {
    maxHeight: '400px',
    overflowY: 'auto'
  };
  const paginationStyle = { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 16px', borderTop: '1px solid var(--gray-200)', background: 'white' };
  const pagerBtn = { padding: '6px 10px', borderRadius: 6, border: '1px solid var(--gray-200)', background: 'white', cursor: 'pointer' };
  const pageInfo = { fontSize: 12, color: 'var(--primary-700)' };

  const expenseItemStyle = {
    padding: 'var(--spacing-md) var(--spacing-lg)',
    borderBottom: '1px solid var(--gray-100)',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    transition: 'background-color 0.2s ease',
    cursor: 'pointer'
  };

  const expenseItemHoverStyle = {
    backgroundColor: 'var(--gray-50)'
  };

  const expenseDetailsStyle = {
    flex: 1
  };

  const descriptionStyle = {
    fontSize: '1rem',
    fontWeight: '500',
    color: 'var(--primary-900)',
    marginBottom: 'var(--spacing-xs)'
  };

  const metaStyle = {
    fontSize: '0.875rem',
    color: 'var(--primary-600)',
    display: 'flex',
    gap: 'var(--spacing-md)'
  };

  const categoryStyle = {
    backgroundColor: 'var(--accent-100)',
    color: 'var(--accent-700)',
    padding: '2px 8px',
    borderRadius: 'var(--border-radius-sm)',
    fontSize: '0.75rem',
    fontWeight: '500'
  };

  const amountStyle = {
    fontSize: '1.125rem',
    fontWeight: '600',
    color: 'var(--primary-900)'
  };

  const emptyStateStyle = {
    padding: 'var(--spacing-xl)',
    textAlign: 'center',
    color: 'var(--primary-600)'
  };

  const errorStyle = {
    padding: 'var(--spacing-lg)',
    backgroundColor: '#fef2f2',
    color: '#dc2626',
    textAlign: 'center'
  };

  if (loading) {
    return (
      <div style={containerStyle}>
        <div style={headerStyle}>
          <h3 style={titleStyle}>Recent Expenses</h3>
        </div>
        <div style={{ padding: 'var(--spacing-xl)', textAlign: 'center' }}>
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={containerStyle}>
        <div style={headerStyle}>
          <h3 style={titleStyle}>Recent Expenses</h3>
        </div>
        <div style={errorStyle}>
          {error}
        </div>
      </div>
    );
  }

  return (
    <div style={containerStyle}>
      <div style={headerStyle}>
        <h3 style={titleStyle}>
          Recent Expenses ({filteredAndSortedExpenses.length})
        </h3>
        
        <div style={sortControlsStyle}>
          <span style={{ fontSize: '0.875rem', color: 'var(--primary-600)' }}>
            Sort by:
          </span>
          {[
            { key: 'date', label: 'Date' },
            { key: 'amount', label: 'Amount' },
            { key: 'category', label: 'Category' },
            { key: 'description', label: 'Description' }
          ].map(({ key, label }) => (
            <button
              key={key}
              onClick={() => handleSort(key)}
              style={sortBy === key ? activeSortButtonStyle : sortButtonStyle}
            >
              {label} {sortBy === key && (sortOrder === 'asc' ? '↑' : '↓')}
            </button>
          ))}
        </div>
      </div>

      {filteredAndSortedExpenses.length === 0 ? (
        <div style={emptyStateStyle}>
          {searchFilter ? 
            `No expenses found matching "${searchFilter}"` : 
            'No expenses yet. Add your first expense to get started!'
          }
        </div>
      ) : (
        <div style={listStyle}>
          {filteredAndSortedExpenses.map((expense) => (
            <div
              key={expense.id}
              style={expenseItemStyle}
              onClick={() => onEditExpense && onEditExpense(expense)}
              onMouseEnter={(e) => {
                e.target.style.backgroundColor = expenseItemHoverStyle.backgroundColor;
              }}
              onMouseLeave={(e) => {
                e.target.style.backgroundColor = 'transparent';
              }}
            >
              <div style={expenseDetailsStyle}>
                <div style={descriptionStyle}>
                  {expense.description}
                </div>
                <div style={metaStyle}>
                  <span>{formatDate(expense.expense_date || expense.created_at)}</span>
                  {expense.category && (
                    <span style={categoryStyle}>
                      {expense.category}
                    </span>
                  )}
                  {expense.notes && <span>📝</span>}
                </div>
              </div>
              <div style={amountStyle}>
                {formatAmount(expense.amount)}
              </div>
            </div>
          ))}
        </div>
      )}
      <div style={paginationStyle}>
        <div style={pageInfo}>
          Page {page} · Showing {filteredAndSortedExpenses.length} of {total}
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <button style={pagerBtn} disabled={page <= 1} onClick={() => setPage(p => Math.max(1, p - 1))}>Prev</button>
          <button style={pagerBtn} disabled={(page * pageSize) >= total} onClick={() => setPage(p => p + 1)}>Next</button>
          <select value={pageSize} onChange={(e) => { setPage(1); setPageSize(parseInt(e.target.value, 10) || 10); }} style={{ ...pagerBtn, padding: '6px' }}>
            {[10, 20, 50, 100].map(ps => <option key={ps} value={ps}>{ps}/page</option>)}
          </select>
        </div>
      </div>
    </div>
  );
};

export default ExpenseList;
