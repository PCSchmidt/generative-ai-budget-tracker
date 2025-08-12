/**
 * AI Budget Tracker - Dashboard Screen (React Web)
 * Clean, modern dashboard with expense management
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import apiService from '../../services/api';
import { buildCategoryBreakdown, getCategoryMeta, formatCurrency as fmt, getCategoryIcon } from '../../utils/categories';

export default function DashboardScreen() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
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

  // ======= NEW ML STATES =======
  const [financialAdvice, setFinancialAdvice] = useState(null);
  const [spendingInsights, setSpendingInsights] = useState(null);
  const [aiSystemStatus, setAiSystemStatus] = useState(null);
  const [loadingMLData, setLoadingMLData] = useState(false);
  const [showAIInsights, setShowAIInsights] = useState(false);

  // Budgets and Goals states
  const [budgets, setBudgets] = useState([]);
  const [goals, setGoals] = useState([]);
  const [loadingPortfolios, setLoadingPortfolios] = useState(false);
  const [showContributeGoal, setShowContributeGoal] = useState(null);
  const [contributing, setContributing] = useState(false);
  // New Budget & Goal CRUD state
  const [showBudgetModal, setShowBudgetModal] = useState(false);
  const [editingBudget, setEditingBudget] = useState(null);
  const [showGoalModal, setShowGoalModal] = useState(false);
  const [editingGoal, setEditingGoal] = useState(null);
  // Derived metrics
  const [monthlyTotals, setMonthlyTotals] = useState({ total: 0, avg: 0 });
  const [monthlyBudget, setMonthlyBudget] = useState(null);

  // Debug: Log auth state
  console.log('DashboardScreen - user:', user);
  console.log('DashboardScreen - localStorage tokens:', {
    accessToken: localStorage.getItem('accessToken'),
    refreshToken: localStorage.getItem('refreshToken'),
    user: localStorage.getItem('user')
  });

  useEffect(() => {
    loadDashboardData();
    loadAISystemStatus();
    loadBudgetsAndGoals();
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

      const expList = expensesData.expenses || expensesData || [];
      setExpenses(expList);
      setInsights(insightsData.insights);

      // Compute simple month-to-date stats
      try {
        const now = new Date();
        const ym = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}`;
        const mtx = expList.filter(e => (e.expense_date || e.created_at || '').startsWith(ym));
        const total = mtx.reduce((s, e) => s + Number(e.amount||0), 0);
        const avg = mtx.length ? total / mtx.length : 0;
        setMonthlyTotals({ total, avg });
      } catch {}
      
      // Load ML insights if we have expenses
      if ((expensesData.expenses || expensesData || []).length > 0) {
        loadMLInsights();
      }
      
    } catch (error) {
      console.error('Dashboard load error:', error);
      setError('Unable to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  // ======= NEW ML DATA LOADING METHODS =======
  const loadAISystemStatus = async () => {
    try {
      const status = await apiService.getAISystemStatus();
      setAiSystemStatus(status);
      console.log('AI System Status:', status);
    } catch (error) {
      console.warn('Could not load AI system status:', error);
    }
  };

  const loadMLInsights = async () => {
    if (loadingMLData) return; // Prevent multiple simultaneous calls
    
    try {
      setLoadingMLData(true);
      
      const [adviceResult, insightsResult] = await Promise.all([
        apiService.getFinancialAdvice('general', true).catch(err => {
          console.warn('Financial advice failed:', err);
          return { success: false, error: err.message };
        }),
        apiService.getSpendingInsights().catch(err => {
          console.warn('Spending insights failed:', err);
          return { success: false, error: err.message };
        })
      ]);

      if (adviceResult && adviceResult.success) {
        // Store only the advice payload, not the wrapper object
        setFinancialAdvice(adviceResult.advice);
        console.log('Financial advice loaded:', adviceResult.advice);
      }

      if (insightsResult && insightsResult.success) {
        setSpendingInsights(insightsResult);
        console.log('Spending insights loaded:', insightsResult);
      }

    } catch (error) {
      console.error('ML insights loading error:', error);
    } finally {
      setLoadingMLData(false);
    }
  };

  const loadBudgetsAndGoals = async () => {
    try {
      setLoadingPortfolios(true);
      const [bRes, gRes] = await Promise.all([
        apiService.getBudgets().catch(()=>({ budgets: [] })),
        apiService.getGoals().catch(()=>({ goals: [] }))
      ]);
      const bList = bRes.budgets || bRes || [];
      const gList = gRes.goals || gRes || [];
      setBudgets(bList);
      setGoals(gList);
      // Set the current month budget if present
      const now = new Date();
      const ym = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}`;
      const mb = bList.find(b => b.period === ym) || null;
      setMonthlyBudget(mb);
    } catch(e){ console.warn('Budget/Goal load failed', e); }
    finally { setLoadingPortfolios(false); }
  };

  const formatCurrency = (amount) => {
    return `$${Number(amount || 0).toFixed(2)}`;
  };

  // Simple date formatter for expense rows
  const formatDate = (value) => {
    if (!value) return '';
    try {
      const d = new Date(value);
      if (isNaN(d.getTime())) return String(value);
      return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    } catch {
      return String(value);
    }
  };

  const handleLogout = () => {
    logout();
  };

  const handleAddExpense = async (expenseData) => {
    try {
      setAddingExpense(true);
      console.log('Adding expense with AI categorization:', expenseData);
      
      // Use AI-enhanced expense creation
      const response = await apiService.createExpenseWithAI(expenseData);
      console.log('Expense created with AI:', response);
      
      // Reload dashboard data and ML insights
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

  // ==== Budget Handlers ====
  const handleCreateBudget = async (data) => {
    try {
      await apiService.createBudget(data);
      await loadBudgetsAndGoals();
      setShowBudgetModal(false);
    } catch (e) { alert('Failed to create budget: ' + e.message); }
  };
  const handleUpdateBudget = async (id, data) => {
    try {
      await apiService.updateBudget(id, data);
      await loadBudgetsAndGoals();
      setEditingBudget(null);
    } catch (e) { alert('Failed to update budget: ' + e.message); }
  };
  const handleDeleteBudget = async (b) => {
    if(!window.confirm('Delete budget '+ b.period +'?')) return;
    try { await apiService.deleteBudget(b.id); await loadBudgetsAndGoals(); } catch(e){ alert('Failed to delete budget: '+e.message);} }

  // ==== Goal Handlers ====
  const handleCreateGoal = async (data) => {
    try {
      await apiService.createGoal(data);
      await loadBudgetsAndGoals();
      setShowGoalModal(false);
    } catch (e) { alert('Failed to create goal: ' + e.message); }
  };
  const handleUpdateGoal = async (id, data) => {
    try {
      await apiService.updateGoal(id, data);
      await loadBudgetsAndGoals();
      setEditingGoal(null);
    } catch (e) { alert('Failed to update goal: ' + e.message); }
  };
  const handleDeleteGoal = async (g) => { if(!window.confirm('Delete goal '+ g.name +'?')) return; try { await apiService.deleteGoal(g.id); await loadBudgetsAndGoals(); } catch(e){ alert('Failed to delete goal: '+e.message);} }

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
          <div style={{ display: 'flex', gap: 8 }}>
            <button
              style={{ ...styles.logoutButton, backgroundColor: '#2563eb' }}
              onClick={() => navigate('/ai-dashboard')}
              title="Open AI Dashboard"
            >
              AI Dashboard
            </button>
            <button style={styles.logoutButton} onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main style={styles.main}>
        {/* Summary Cards with ML Insights */}
        <section style={styles.summarySection}>
          <div style={styles.summaryCard}>
            <h3 style={styles.cardTitle}>Month To Date</h3>
            <p style={styles.cardAmount}>{fmt(monthlyTotals.total)}</p>
            <p style={styles.cardSubtext}>Avg {fmt(monthlyTotals.avg)}</p>
          </div>
          {/* Budget summary */}
          <div style={styles.summaryCard}>
            <h3 style={styles.cardTitle}>Budget Utilization</h3>
            {monthlyBudget ? (
              <>
                <p style={styles.cardAmount}>{Math.round((monthlyBudget.utilization||0)*100)}%</p>
                <p style={styles.cardSubtext}>{fmt(monthlyBudget.spent_amount)} / {fmt(monthlyBudget.total_limit)}</p>
              </>
            ) : <p style={styles.cardSubtext}>No budget this month</p>}
          </div>
          {/* Goals summary */}
          <div style={styles.summaryCard}>
            <h3 style={styles.cardTitle}>Active Goals</h3>
            <p style={styles.cardAmount}>{goals.length}</p>
            <p style={styles.cardSubtext}>Tracking savings</p>
          </div>
          <div style={styles.summaryCard}>
            <h3 style={styles.cardTitle}>AI Analysis</h3>
            <p style={styles.cardAmount}>
              {spendingInsights?.insights?.category_breakdown ? 
                Object.keys(spendingInsights.insights.category_breakdown).length + ' categories' :
                'Analyzing...'
              }
            </p>
            <p style={styles.cardSubtext}>
              {aiSystemStatus?.ml_enhanced ? '🤖 AI Enhanced' : '📊 Basic Analysis'}
            </p>
          </div>
        </section>

        {/* AI Financial Advisor Section */}
        {(financialAdvice || spendingInsights) && (
          <section style={styles.aiInsightsSection}>
            <h2 style={styles.sectionTitle}>
              🤖 AI Financial Advisor
              {loadingMLData && <span style={styles.loadingDot}>●</span>}
            </h2>
            
            {financialAdvice && (
              <div style={styles.adviceCard}>
                <h3 style={styles.adviceTitle}>💡 Personalized Advice</h3>
                <p style={styles.adviceText}>{financialAdvice.main_advice}</p>
                {Array.isArray(financialAdvice.action_items) && financialAdvice.action_items.length > 0 && (
                  <ul style={styles.recommendationList}>
                    {financialAdvice.action_items.slice(0, 3).map((item, idx) => (
                      <li key={idx} style={styles.recommendationItem}>{item}</li>
                    ))}
                  </ul>
                )}
                <div style={styles.adviceMeta}>
                  <span>Confidence: {Math.round(((financialAdvice.confidence ?? 0.7)) * 100)}%</span>
                  <span>•</span>
                  <span>{financialAdvice.advice_type || 'General'}</span>
                </div>
              </div>
            )}

            {spendingInsights?.insights && (
              <div style={styles.insightsGrid}>
                {spendingInsights.insights.category_breakdown && (
                  <div style={styles.insightCard}>
                    <h4 style={styles.insightTitle}>📊 Category Breakdown</h4>
                    <div style={styles.categoryList}>
                      {Object.entries(spendingInsights.insights.category_breakdown)
                        .slice(0, 3)
                        .map(([category, amount]) => (
                          <div key={category} style={styles.categoryItem}>
                            <span>{category}</span>
                            <span>{formatCurrency(amount)}</span>
                          </div>
                        ))}
                    </div>
                  </div>
                )}

                {spendingInsights.insights.recommendations && spendingInsights.insights.recommendations.length > 0 && (
                  <div style={styles.insightCard}>
                    <h4 style={styles.insightTitle}>🎯 Smart Recommendations</h4>
                    <ul style={styles.recommendationList}>
                      {spendingInsights.insights.recommendations.slice(0, 3).map((rec, index) => (
                        <li key={index} style={styles.recommendationItem}>
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            )}
          </section>
        )}

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
            <button 
              style={styles.actionButton}
              onClick={loadMLInsights}
              disabled={loadingMLData}
            >
              <span style={styles.actionIcon}>🤖</span>
              {loadingMLData ? 'Analyzing...' : 'AI Insights'}
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

        {/* Budgets Section */}
        <section style={styles.portfolioSection}>
          <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
            <h2 style={styles.sectionTitle}>Budgets</h2>
            <button style={styles.smallActionBtn} onClick={()=> setShowBudgetModal(true)}>+ Budget</button>
          </div>
          {monthlyBudget ? (
            <div style={styles.budgetCardWrapper}>
              {budgets.map(b => {
                const over = (b.utilization||0) > 1;
                const pct = Math.min(1, b.utilization||0);
                return (
                  <div key={b.id} style={{...styles.budgetCard, borderColor: over ? '#dc2626':'#e2e8f0'}}>
                    <div style={styles.budgetHeader}>
                      <strong>{b.period}</strong>
                      <span style={{color: over?'#dc2626':'#64748b'}}>{Math.round((b.utilization||0)*100)}%</span>
                    </div>
                    <div style={styles.progressBarOuter}>
                      <div style={{...styles.progressBarInner, background: over?'linear-gradient(90deg,#dc2626,#ef4444)':'linear-gradient(90deg,#2563eb,#3b82f6)', width: `${pct*100}%`}} />
                    </div>
                    <div style={styles.budgetMeta}>
                      <span>{fmt(b.spent_amount)} / {fmt(b.total_limit)}</span>
                      <span style={{color: over?'#dc2626':'#10b981'}}>{over? `${fmt(b.spent_amount - b.total_limit)} over` : `${fmt(b.total_limit - b.spent_amount)} left`}</span>
                    </div>
                    <div style={styles.inlineActions}>
                      <button style={styles.inlineEditBtn} onClick={()=> setEditingBudget(b)}>Edit</button>
                      <button style={styles.inlineDeleteBtn} onClick={()=> handleDeleteBudget(b)}>Del</button>
                    </div>
                  </div>
                )})}
            </div>
          ) : (
            <div style={styles.emptyInline}>No budgets yet</div>
          )}
        </section>

        {/* Goals Section */}
        <section style={styles.portfolioSection}>
          <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
            <h2 style={styles.sectionTitle}>Goals</h2>
            <button style={styles.smallActionBtn} onClick={()=> setShowGoalModal(true)}>+ Goal</button>
          </div>
          {goals.length ? (
            <div style={styles.goalsGrid}>
              {goals.map(g => {
                const pct = Math.min(100, g.progress_percent || (g.current_amount && g.target_amount? (g.current_amount / g.target_amount * 100):0));
                return (
                  <div key={g.id} style={styles.goalCard}>
                    <div style={styles.goalHeader}>
                      <strong style={styles.goalName}>{g.name}</strong>
                      <span style={styles.goalPct}>{Math.round(pct)}%</span>
                    </div>
                    <div style={styles.progressBarOuterSmall}>
                      <div style={{...styles.progressBarInnerSmall, width: `${pct}%`, background: pct>=100? '#10b981':'linear-gradient(90deg,#6366f1,#8b5cf6)'}} />
                    </div>
                    <div style={styles.goalMeta}>
                      <span>{fmt(g.current_amount)} / {fmt(g.target_amount)}</span>
                      {pct>=100 && <span style={styles.goalComplete}>Complete</span>}
                    </div>
                    <div style={styles.inlineActions}>
                      <button style={styles.inlineEditBtn} onClick={()=> setEditingGoal(g)}>Edit</button>
                      <button style={styles.inlineDeleteBtn} onClick={()=> handleDeleteGoal(g)}>Del</button>
                    </div>
                    <button style={styles.contributeBtn} onClick={()=>setShowContributeGoal(g)}>Contribute</button>
                  </div>
                )})}
            </div>
          ) : <div style={styles.emptyInline}>No goals yet</div>}
        </section>
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

      {/* Contribute to Goal Modal */}
      {showContributeGoal && (
        <ContributeModal
          goal={showContributeGoal}
          onCancel={()=>setShowContributeGoal(null)}
          onSubmit={async (amount)=>{
            try { setContributing(true); await apiService.contributeGoal(showContributeGoal.id, amount); await loadBudgetsAndGoals(); setShowContributeGoal(null);} finally { setContributing(false);} }}
          loading={contributing}
        />
      )}

      {/* Budget Create Modal */}
      {showBudgetModal && (
        <BudgetFormModal
          onCancel={()=> setShowBudgetModal(false)}
          onSubmit={handleCreateBudget}
        />
      )}
      {/* Budget Edit Modal */}
      {editingBudget && (
        <BudgetFormModal
          initialData={editingBudget}
          onCancel={()=> setEditingBudget(null)}
          onSubmit={(data)=> handleUpdateBudget(editingBudget.id, data)}
          title="Edit Budget"
        />
      )}
      {/* Goal Create Modal */}
      {showGoalModal && (
        <GoalFormModal
          onCancel={()=> setShowGoalModal(false)}
          onSubmit={handleCreateGoal}
        />
      )}
      {/* Goal Edit Modal */}
      {editingGoal && (
        <GoalFormModal
          initialData={editingGoal}
          onCancel={()=> setEditingGoal(null)}
          onSubmit={(data)=> handleUpdateGoal(editingGoal.id, data)}
          title="Edit Goal"
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
  const [suggestedCategory, setSuggestedCategory] = useState('');
  const [categorizingAI, setCategorizingAI] = useState(false);
  const [aiSuggestionUsed, setAiSuggestionUsed] = useState(false);

  // AI Categorization when description changes
  const handleDescriptionChange = async (e) => {
    const { value } = e.target;
    setFormData(prev => ({ ...prev, description: value }));
    if (error) setError('');

    // Trigger AI categorization if description is meaningful
    if (value.trim().length > 3 && !formData.category && !aiSuggestionUsed) {
      setCategorizingAI(true);
      try {
        const response = await apiService.categorizeExpenseSmart(value.trim(), parseFloat(formData.amount) || 0);
        if (response.success && response.category !== 'Other') {
          setSuggestedCategory(response.category);
        }
      } catch (error) {
        console.log('AI categorization failed, using fallback');
      } finally {
        setCategorizingAI(false);
      }
    }
  };

  const applySuggestedCategory = () => {
    setFormData(prev => ({ ...prev, category: suggestedCategory }));
    setAiSuggestionUsed(true);
    setSuggestedCategory('');
  };

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
              onChange={handleDescriptionChange}
              placeholder="Coffee, Lunch, Gas, etc."
              style={modalStyles.input}
              required
            />
            {categorizingAI && (
              <div style={modalStyles.aiHint}>
                🤖 AI is analyzing your expense...
              </div>
            )}
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
            {suggestedCategory && !formData.category && (
              <div style={modalStyles.aiSuggestion}>
                <span>🤖 AI suggests: <strong>{suggestedCategory}</strong></span>
                <button 
                  type="button" 
                  onClick={applySuggestedCategory}
                  style={modalStyles.aiAcceptButton}
                >
                  Use This
                </button>
                <button 
                  type="button" 
                  onClick={() => setSuggestedCategory('')}
                  style={modalStyles.aiRejectButton}
                >
                  Dismiss
                </button>
              </div>
            )}
            <select
              name="category"
              value={formData.category}
              onChange={handleChange}
              style={modalStyles.input}
            >
              <option value="">Select Category (AI will suggest)</option>
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

function ContributeModal({ goal, onCancel, onSubmit, loading }) {
  const [amount, setAmount] = useState('');
  return (
    <div style={modalStyles.overlay}>
      <div style={modalStyles.modal}>
        <h2 style={modalStyles.title}>Contribute to {goal.name}</h2>
        <form onSubmit={(e)=>{e.preventDefault(); const val=parseFloat(amount); if(!val||val<=0)return; onSubmit(val);}}>
          <div style={modalStyles.formGroup}>
            <label style={modalStyles.label}>Amount</label>
            <input style={modalStyles.input} type="number" min="0" step="0.01" value={amount} onChange={e=>setAmount(e.target.value)} />
          </div>
          <div style={modalStyles.buttons}>
            <button type="button" style={modalStyles.cancelButton} onClick={onCancel} disabled={loading}>Cancel</button>
            <button type="submit" style={modalStyles.submitButton} disabled={loading}>{loading? 'Saving...':'Add Contribution'}</button>
          </div>
        </form>
      </div>
    </div>
  );
}

// New Budget Form Modal
function BudgetFormModal({ onSubmit, onCancel, initialData=null, title='New Budget' }) {
  const [form, setForm] = useState(()=> initialData ? { period: initialData.period, total_limit: initialData.total_limit } : { period:'', total_limit:'' });
  const handleChange = e => setForm(f=> ({...f, [e.target.name]: e.target.value}));
  const handleSubmit = e => { e.preventDefault(); if(!form.period || !form.total_limit) return; onSubmit({ period: form.period, total_limit: parseFloat(form.total_limit) }); };
  return (
    <div style={modalStyles.overlay}>
      <div style={modalStyles.modal}>
        <h2 style={modalStyles.title}>{title}</h2>
        <form onSubmit={handleSubmit}>
          <div style={modalStyles.formGroup}>
            <label style={modalStyles.label}>Period (YYYY-MM)</label>
            <input name="period" value={form.period} onChange={handleChange} placeholder="2025-08" style={modalStyles.input} required={!initialData} disabled={!!initialData} />
          </div>
          <div style={modalStyles.formGroup}>
            <label style={modalStyles.label}>Total Limit</label>
            <input name="total_limit" type="number" min="0" step="0.01" value={form.total_limit} onChange={handleChange} style={modalStyles.input} required />
          </div>
          <div style={modalStyles.buttons}>
            <button type="button" style={modalStyles.cancelButton} onClick={onCancel}>Cancel</button>
            <button type="submit" style={modalStyles.submitButton}>{initialData? 'Save':'Create'}</button>
          </div>
        </form>
      </div>
    </div>
  );
}

function GoalFormModal({ onSubmit, onCancel, initialData=null, title='New Goal' }) {
  const [form, setForm] = useState(()=> initialData ? { name: initialData.name, target_amount: initialData.target_amount, current_amount: initialData.current_amount } : { name:'', target_amount:'', current_amount:'0' });
  const handleChange = e => setForm(f=> ({...f, [e.target.name]: e.target.value}));
  const handleSubmit = e => { e.preventDefault(); if(!form.name || !form.target_amount) return; onSubmit({ name: form.name, target_amount: parseFloat(form.target_amount), current_amount: parseFloat(form.current_amount||0) }); };
  return (
    <div style={modalStyles.overlay}>
      <div style={modalStyles.modal}>
        <h2 style={modalStyles.title}>{title}</h2>
        <form onSubmit={handleSubmit}>
          <div style={modalStyles.formGroup}>
            <label style={modalStyles.label}>Name</label>
            <input name="name" value={form.name} onChange={handleChange} style={modalStyles.input} required />
          </div>
          <div style={modalStyles.formGroup}>
            <label style={modalStyles.label}>Target Amount</label>
            <input name="target_amount" type="number" min="0" step="0.01" value={form.target_amount} onChange={handleChange} style={modalStyles.input} required />
          </div>
          <div style={modalStyles.formGroup}>
            <label style={modalStyles.label}>Current Amount</label>
            <input name="current_amount" type="number" min="0" step="0.01" value={form.current_amount} onChange={handleChange} style={modalStyles.input} />
          </div>
          <div style={modalStyles.buttons}>
            <button type="button" style={modalStyles.cancelButton} onClick={onCancel}>Cancel</button>
            <button type="submit" style={modalStyles.submitButton}>{initialData? 'Save':'Create'}</button>
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
  aiHint: {
    color: '#6b7280',
    fontSize: '12px',
    fontStyle: 'italic',
    marginTop: '4px',
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
  },
  aiSuggestion: {
    backgroundColor: '#f0f9ff',
    border: '1px solid #0ea5e9',
    borderRadius: '6px',
    padding: '8px 12px',
    marginBottom: '8px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    fontSize: '14px',
  },
  aiAcceptButton: {
    backgroundColor: '#10b981',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    padding: '4px 8px',
    fontSize: '12px',
    cursor: 'pointer',
    marginLeft: '8px',
  },
  aiRejectButton: {
    backgroundColor: '#6b7280',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    padding: '4px 8px',
    fontSize: '12px',
    cursor: 'pointer',
    marginLeft: '4px',
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

  // AI Insights Section Styles
  aiInsightsSection: {
    marginBottom: '32px',
  },

  loadingDot: {
    color: '#3b82f6',
    animation: 'pulse 1.5s ease-in-out infinite',
    marginLeft: '8px',
  },

  adviceCard: {
    backgroundColor: '#f0f9ff',
    border: '1px solid #0ea5e9',
    borderRadius: '12px',
    padding: '20px',
    marginBottom: '20px',
  },

  adviceTitle: {
    color: '#0c4a6e',
    fontSize: '16px',
    fontWeight: '600',
    margin: '0 0 12px 0',
  },

  adviceText: {
    color: '#1e293b',
    fontSize: '15px',
    lineHeight: '1.6',
    margin: '0 0 12px 0',
  },

  adviceMeta: {
    display: 'flex',
    gap: '8px',
    fontSize: '12px',
    color: '#64748b',
    alignItems: 'center',
  },

  insightsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '16px',
  },

  insightTitle: {
    color: '#374151',
    fontSize: '14px',
    fontWeight: '600',
    margin: '0 0 12px 0',
  },

  categoryList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },

  categoryItem: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '8px 0',
    borderBottom: '1px solid #e5e7eb',
    fontSize: '14px',
  },

  recommendationList: {
    margin: '0',
    paddingLeft: '16px',
  },

  recommendationItem: {
    fontSize: '14px',
    color: '#374151',
    marginBottom: '6px',
    lineHeight: '1.4',
  },

  miniSpinner: {
    width: '12px',
    height: '12px',
    border: '2px solid #e5e7eb',
    borderTop: '2px solid #3b82f6',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
    display: 'inline-block',
    marginLeft: '8px',
  },

  portfolioSection: { marginBottom: '32px' },
  budgetCardWrapper: { display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(240px,1fr))', gap:'16px'},
  budgetCard: { background:'#fff', border:'1px solid #e2e8f0', borderRadius:'12px', padding:'16px', display:'flex', flexDirection:'column', gap:'8px' },
  budgetHeader: { display:'flex', justifyContent:'space-between', fontSize:'14px', color:'#475569' },
  progressBarOuter: { position:'relative', height:'12px', background:'#f1f5f9', borderRadius:'8px', overflow:'hidden' },
  progressBarInner: { position:'absolute', left:0, top:0, bottom:0, borderRadius:'8px', transition:'width .4s ease' },
  budgetMeta: { display:'flex', justifyContent:'space-between', fontSize:'12px', color:'#64748b' },
  emptyInline: { fontSize:'14px', color:'#94a3b8' },
  goalsGrid: { display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(220px,1fr))', gap:'16px' },
  goalCard: { background:'#fff', border:'1px solid #e2e8f0', borderRadius:'12px', padding:'16px', display:'flex', flexDirection:'column', gap:'6px' },
  goalHeader: { display:'flex', justifyContent:'space-between', fontSize:'14px', color:'#475569' },
  goalName: { fontWeight:600 },
  goalPct: { fontWeight:600, color:'#6366f1' },
  progressBarOuterSmall: { position:'relative', height:'8px', background:'#f1f5f9', borderRadius:'6px', overflow:'hidden' },
  progressBarInnerSmall: { position:'absolute', left:0, top:0, bottom:0, borderRadius:'6px', transition:'width .4s ease' },
  goalMeta: { display:'flex', justifyContent:'space-between', fontSize:'12px', color:'#64748b' },
  goalComplete: { color:'#10b981', fontWeight:600 },
  contributeBtn: { marginTop:'4px', background:'#2563eb', color:'#fff', border:'none', borderRadius:'6px', padding:'6px 10px', fontSize:'12px', cursor:'pointer' },
  inlineActions: { display:'flex', gap:'6px', marginTop:'4px' },
  inlineEditBtn: { background:'#f1f5f9', border:'1px solid #cbd5e1', borderRadius:'4px', padding:'4px 6px', fontSize:'11px', cursor:'pointer' },
  inlineDeleteBtn: { background:'#fff5f5', border:'1px solid #fecaca', borderRadius:'4px', padding:'4px 6px', fontSize:'11px', cursor:'pointer', color:'#dc2626' },
  smallActionBtn: { background:'#2563eb', color:'#fff', border:'none', borderRadius:'6px', padding:'6px 12px', fontSize:'13px', cursor:'pointer' },
};

// Add CSS keyframes for spinner animation
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
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
