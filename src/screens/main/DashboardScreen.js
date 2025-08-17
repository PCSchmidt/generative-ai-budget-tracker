import React, { useEffect, useState } from 'react';
import apiService from '../../services/api';

const DashboardScreen = () => {
  const [aiStatus, setAiStatus] = useState(null);
  const [loadingStatus, setLoadingStatus] = useState(true);
  const [advice, setAdvice] = useState(null);
  const [insights, setInsights] = useState(null);
  const [loadingAdvice, setLoadingAdvice] = useState(false);
  const [loadingInsights, setLoadingInsights] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const status = await apiService.getAISystemStatus();
        if (mounted) setAiStatus(status);
      } catch (e) {
        if (mounted) setError(e.message || 'Failed to load AI status');
      } finally {
        if (mounted) setLoadingStatus(false);
      }
    })();
    return () => { mounted = false; };
  }, []);

  const fetchAdvice = async () => {
    setLoadingAdvice(true);
    setError('');
    try {
      const resp = await apiService.getFinancialAdvice('general', false);
      if (resp?.success) {
        setAdvice(resp.advice);
      } else {
        setError(resp?.error || 'Failed to fetch advice');
      }
    } catch (e) {
      setError(e.message || 'Failed to fetch advice');
    } finally {
      setLoadingAdvice(false);
    }
  };

  const fetchInsights = async () => {
    setLoadingInsights(true);
    setError('');
    try {
      const resp = await apiService.getSpendingInsights();
      if (resp?.success) {
        setInsights(resp.insights);
      } else {
        setError(resp?.error || 'Failed to fetch insights');
      }
    } catch (e) {
      setError(e.message || 'Failed to fetch insights');
    } finally {
      setLoadingInsights(false);
    }
  };

  const card = {
    background: 'white',
    border: '1px solid #e5e7eb',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16
  };

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: 16 }}>
      <h1 style={{ fontSize: 24, fontWeight: 700, marginBottom: 16 }}>Dashboard</h1>

      {error && (
        <div style={{ ...card, background: '#fef2f2', borderColor: '#fecaca', color: '#991b1b' }}>{error}</div>
      )}

      <div style={card}>
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>AI System Status</h2>
        {loadingStatus ? (
          <div>Loading status...</div>
        ) : aiStatus ? (
          <div>
            <div style={{ display: 'flex', gap: 12, marginBottom: 8 }}>
              <span style={{ padding: '4px 10px', borderRadius: 999, background: aiStatus.ai_available ? '#ecfdf5' : '#fef2f2', color: aiStatus.ai_available ? '#065f46' : '#991b1b', border: `1px solid ${aiStatus.ai_available ? '#a7f3d0' : '#fecaca'}` }}>
                AI Available: {String(aiStatus.ai_available)}
              </span>
              <span style={{ padding: '4px 10px', borderRadius: 999, background: aiStatus.ml_enhanced ? '#eff6ff' : '#f3f4f6', color: aiStatus.ml_enhanced ? '#1e40af' : '#374151', border: `1px solid ${aiStatus.ml_enhanced ? '#bfdbfe' : '#e5e7eb'}` }}>
                ML Enhanced: {String(aiStatus.ml_enhanced)}
              </span>
            </div>
            {aiStatus.services && (
              <div style={{ fontSize: 14, color: '#4b5563' }}>
                Services: {Object.entries(aiStatus.services).map(([k, v]) => `${k}=${v}`).join(', ')}
              </div>
            )}
          </div>
        ) : (
          <div>Unable to load AI status.</div>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div style={card}>
          <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>Personalized Financial Advice</h3>
          <button onClick={fetchAdvice} disabled={loadingAdvice} style={{ padding: '8px 12px', background: '#2563eb', color: 'white', border: 'none', borderRadius: 8, cursor: loadingAdvice ? 'not-allowed' : 'pointer' }}>
            {loadingAdvice ? 'Loading...' : 'Get Advice'}
          </button>
          {advice && (
            <div style={{ marginTop: 12, fontSize: 14 }}>
              <div style={{ fontWeight: 600, marginBottom: 6 }}>{advice.main_advice}</div>
              {advice.action_items?.length > 0 && (
                <ul style={{ paddingLeft: 18 }}>
                  {advice.action_items.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </div>

        <div style={card}>
          <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 8 }}>Spending Insights</h3>
          <button onClick={fetchInsights} disabled={loadingInsights} style={{ padding: '8px 12px', background: '#059669', color: 'white', border: 'none', borderRadius: 8, cursor: loadingInsights ? 'not-allowed' : 'pointer' }}>
            {loadingInsights ? 'Loading...' : 'Get Insights'}
          </button>
          {insights && (
            <div style={{ marginTop: 12, fontSize: 14 }}>
              <div>Total Spending: ${Number(insights.total_spending || 0).toFixed(2)}</div>
              {insights.category_breakdown && (
                <div style={{ marginTop: 8 }}>
                  <div style={{ fontWeight: 600, marginBottom: 4 }}>By Category:</div>
                  <ul style={{ paddingLeft: 18 }}>
                    {Object.entries(insights.category_breakdown).map(([cat, amt]) => (
                      <li key={cat}>{cat}: ${Number(amt).toFixed(2)}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DashboardScreen;
