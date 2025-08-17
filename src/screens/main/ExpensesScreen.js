/**
 * Expenses Screen (MVP)
 * - Month filter (YYYY-MM)
 * - Pagination
 * - List expenses with delete and edit hooks
 * - Add expense button opens simple inline form (same fields as dashboard modal)
 */

import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import apiService from '../../services/api';
import { getCategoryIcon } from '../../utils/categories';

export default function ExpensesScreen() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const now = new Date();
  const currentYM = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}`;
  const [selectedMonth, setSelectedMonth] = useState(currentYM);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [expenses, setExpenses] = useState([]);
  const [deletingId, setDeletingId] = useState(null);
  const [showAdd, setShowAdd] = useState(false);
  const [adding, setAdding] = useState(false);

  const load = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await apiService.getExpensesPaginated({ page, page_size: pageSize, month: selectedMonth });
      setExpenses(res.items || []);
      setTotal(res.total || 0);
      setPage(res.page || 1);
      setPageSize(res.page_size || pageSize);
    } catch (e) {
      setError(e.message || 'Failed to load expenses');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [selectedMonth, page, pageSize]);

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this expense?')) return;
    setDeletingId(id);
    try {
      await apiService.deleteExpense(id);
      await load();
    } catch(e) {
      alert(e.message || 'Failed to delete');
    } finally { setDeletingId(null); }
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <div>
          <h1 style={styles.title}>Expenses</h1>
          <p style={styles.subtitle}>Welcome, {user?.username || 'User'}</p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <input
            type="month"
            value={selectedMonth}
            onChange={(e)=>{ setSelectedMonth(e.target.value); setPage(1); }}
            style={styles.monthPicker}
          />
          <button style={styles.secondaryBtn} onClick={()=> navigate('/dashboard')}>Dashboard</button>
          <button style={styles.primaryBtn} onClick={()=> setShowAdd(true)}>Add Expense</button>
          <button style={styles.logoutBtn} onClick={logout}>Logout</button>
        </div>
      </header>

      <main style={styles.main}>
        {error && (
          <div style={styles.errorBox}>
            <span>{error}</span>
            <button style={styles.retryBtn} onClick={load}>Retry</button>
          </div>
        )}

        {loading ? (
          <div style={styles.loading}>Loading…</div>
        ) : expenses.length === 0 ? (
          <div style={styles.empty}>No expenses found for this month</div>
        ) : (
          <div style={styles.list}>
            {expenses.map((e, idx) => (
              <div key={e.id || idx} style={styles.item}>
                <div style={styles.left}>
                  <div style={styles.icon}>{getCategoryIcon(e.category)}</div>
                  <div>
                    <div style={styles.desc}>{e.description || 'Expense'}</div>
                    <div style={styles.meta}>
                      <span>{e.category || 'Uncategorized'}</span>
                      <span>•</span>
                      <span>{formatDate(e.expense_date || e.created_at)}</span>
                    </div>
                  </div>
                </div>
                <div style={styles.right}>
                  <div style={styles.amount}>${Number(e.amount||0).toFixed(2)}</div>
                  <div style={styles.actions}>
                    <button style={styles.editBtn} title="Edit" disabled>✏️</button>
                    <button
                      style={{...styles.deleteBtn, opacity: deletingId===e.id? 0.5:1}}
                      onClick={()=> handleDelete(e.id)}
                      disabled={deletingId===e.id}
                      title="Delete"
                    >{deletingId===e.id? '⏳':'🗑️'}</button>
                  </div>
                </div>
              </div>
            ))}

            <div style={styles.pager}>
              <button style={styles.pagerBtn} disabled={page<=1} onClick={()=> setPage(p=> Math.max(1, p-1))}>Prev</button>
              <span style={styles.pagerText}>Page {page} of {Math.max(1, Math.ceil(total / pageSize))}</span>
              <button style={styles.pagerBtn} disabled={page>=Math.ceil(total/pageSize)} onClick={()=> setPage(p=> (p < Math.ceil(total/pageSize)? p+1: p))}>Next</button>
            </div>
          </div>
        )}

        {showAdd && (
          <AddExpenseInline
            onCancel={()=> setShowAdd(false)}
            onAdded={async ()=> { setShowAdd(false); await load(); }}
          />
        )}
      </main>
    </div>
  );
}

function AddExpenseInline({ onCancel, onAdded }) {
  const [form, setForm] = useState({ description: '', amount: '', category: '', notes: '', expense_date: new Date().toISOString().split('T')[0] });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    if (!form.description.trim()) return setError('Description required');
    if (!form.amount || parseFloat(form.amount) <= 0) return setError('Enter a valid amount');
    try {
      setBusy(true);
      await apiService.createExpenseWithAI({
        description: form.description.trim(),
        amount: parseFloat(form.amount),
        category: form.category || undefined,
        notes: form.notes.trim(),
        expense_date: form.expense_date
      });
      await onAdded();
    } catch(e) {
      setError(e.message || 'Failed to add expense');
    } finally { setBusy(false); }
  };

  return (
    <div style={styles.inlineWrap}>
      <form onSubmit={submit} style={styles.inlineForm}>
        <input style={styles.input} placeholder="Description" value={form.description} onChange={e=> setForm({...form, description: e.target.value})} />
        <input style={styles.input} type="number" step="0.01" min="0" placeholder="Amount" value={form.amount} onChange={e=> setForm({...form, amount: e.target.value})} />
        <select style={styles.input} value={form.category} onChange={e=> setForm({...form, category: e.target.value})}>
          <option value="">Category (AI can suggest)</option>
          <option value="Food & Dining">Food & Dining</option>
          <option value="Transportation">Transportation</option>
          <option value="Entertainment">Entertainment</option>
          <option value="Shopping">Shopping</option>
          <option value="Utilities">Utilities</option>
          <option value="Healthcare">Healthcare</option>
          <option value="Other">Other</option>
        </select>
        <input style={styles.input} type="date" value={form.expense_date} onChange={e=> setForm({...form, expense_date: e.target.value})} />
        <input style={styles.input} placeholder="Notes (optional)" value={form.notes} onChange={e=> setForm({...form, notes: e.target.value})} />
        <div style={{display:'flex', gap:8}}>
          <button type="button" style={styles.cancelBtn} onClick={onCancel} disabled={busy}>Cancel</button>
          <button type="submit" style={styles.submitBtn} disabled={busy}>{busy? 'Adding…':'Add'}</button>
        </div>
      </form>
      {error && <div style={styles.inlineError}>{error}</div>}
    </div>
  );
}

function formatDate(value) {
  if (!value) return '';
  try {
    const d = new Date(value);
    if (isNaN(d.getTime())) return String(value);
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  } catch { return String(value); }
}

const styles = {
  container: { minHeight: '100vh', background: 'linear-gradient(180deg, #0f172a, #111827 60%, #0b1220)' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: 16, color: 'white' },
  title: { margin: 0 },
  subtitle: { margin: 0, color: '#94a3b8', fontSize: 14 },
  monthPicker: { background: '#0b1220', color: 'white', border: '1px solid #334155', borderRadius: 8, padding: '8px 10px' },
  primaryBtn: { background: '#2563eb', color: 'white', border: 'none', borderRadius: 8, padding: '8px 12px', cursor: 'pointer' },
  secondaryBtn: { background: '#334155', color: 'white', border: 'none', borderRadius: 8, padding: '8px 12px', cursor: 'pointer' },
  logoutBtn: { background: '#ef4444', color: 'white', border: 'none', borderRadius: 8, padding: '8px 12px', cursor: 'pointer' },
  main: { padding: 16 },
  errorBox: { background: '#fee2e2', border: '1px solid #fecaca', color: '#991b1b', padding: 12, borderRadius: 8, display:'flex', justifyContent:'space-between', alignItems:'center' },
  retryBtn: { background:'#111827', color:'white', border:'none', borderRadius:6, padding:'6px 10px', cursor:'pointer' },
  loading: { color: 'white' },
  empty: { background:'#0b1220', border:'1px solid #1f2937', color:'#94a3b8', padding:16, borderRadius:12, textAlign:'center' },
  list: { display:'flex', flexDirection:'column', gap:8 },
  item: { background:'#0b1220', border:'1px solid #1f2937', borderRadius:12, padding:12, display:'flex', justifyContent:'space-between', alignItems:'center', color:'white' },
  left: { display:'flex', alignItems:'center', gap:12 },
  icon: { width:36, height:36, borderRadius:8, background:'#111827', display:'grid', placeItems:'center', fontSize:18 },
  desc: { fontWeight:600 },
  meta: { color:'#94a3b8', display:'flex', gap:6, fontSize:12 },
  right: { display:'flex', alignItems:'center', gap:12 },
  amount: { fontWeight:700 },
  actions: { display:'flex', gap:6 },
  editBtn: { border:'1px solid #334155', background:'#111827', color:'white', borderRadius:6, padding:'4px 8px', cursor:'not-allowed' },
  deleteBtn: { border:'1px solid #dc2626', background:'#7f1d1d', color:'white', borderRadius:6, padding:'4px 8px', cursor:'pointer' },
  pager: { display:'flex', gap:8, alignItems:'center', justifyContent:'flex-end', marginTop:8 },
  pagerBtn: { background:'#334155', color:'white', border:'none', borderRadius:6, padding:'6px 10px', cursor:'pointer' },
  pagerText: { color:'#94a3b8', fontSize:12 },
  inlineWrap: { marginTop:16, background:'#0b1220', border:'1px solid #1f2937', borderRadius:12, padding:12 },
  inlineForm: { display:'grid', gridTemplateColumns:'2fr 1fr 1fr 1fr 2fr auto auto', gap:8 },
  input: { background:'#111827', color:'white', border:'1px solid #334155', borderRadius:8, padding:'8px 10px' },
  cancelBtn: { background:'#374151', color:'white', border:'none', borderRadius:8, padding:'8px 12px', cursor:'pointer' },
  submitBtn: { background:'#22c55e', color:'white', border:'none', borderRadius:8, padding:'8px 12px', cursor:'pointer' },
  inlineError: { color:'#fca5a5', marginTop:8 }
};
